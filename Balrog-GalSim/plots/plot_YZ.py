### YZ March 29, 2018
### call method: fignames=plot_YZ.make_all(basepath=None, tile_list=None, realizations=None)
## example call: fignames=plot_YZ.make_all(basepath='/data/des71.a/data/kuropat/blank_test/y3v02/balrog_images', tile_list=['DES0347-5540'], realizations=['0', '1']) 
### It will make a bunch of plots with names listed in fignames
##this file also contains the followign functions readfiles(), match_func(), running_medians()
## dm_m_plot(), dm_T_plot(), dm_dT_plot() 

from sys import argv
import numpy as np
import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from esutil import htm
import sys
import os
from astropy.table import Table, hstack, vstack

def read_files(basepath, tile_list, realizations):
    truth_gals=[]
    truth_stas=[]
    measu_objs=[]
    for tile in tile_list:
        for realn in realizations:
            truth_gal_file=os.path.join(basepath, realn, tile, tile+'_'+realn+'_balrog_truth_cat_gals.fits')
            truth_star_file=os.path.join(basepath, realn, tile, tile+'_'+realn+'_balrog_truth_cat_stars.fits')
            meas_file=os.path.join(basepath, realn, tile, 'mof', tile+'_mof.fits')
            if os.path.isfile(truth_gal_file):
               gals_temp=Table.read(truth_gal_file, hdu=1)
               if len(gals_temp) > 0: 
                 if len(truth_gals)==0:
                   truth_gals=gals_temp
                 else:
                   truth_gals=vstack([truth_gals, gals_temp])
            if os.path.isfile(truth_star_file):
               stas_temp=Table.read(truth_star_file, hdu=1)
               if len(stas_temp) > 0:
                  if len(truth_stas)==0:
                     truth_stas=stas_temp
                  else:
                     truth_stas=vstack([truth_stas, stas_temp])
            if os.path.isfile(meas_file):
               objs_temp=Table.read(meas_file, hdu=1)
               if len(objs_temp) > 0:
                  if len(measu_objs)==0:
                     measu_objs=objs_temp
                  else:
                     measu_objs=vstack([measu_objs, objs_temp])

    print 'found:\n %i truth gals,\n %i truth stars,\n %i observed objects'%(len(truth_gals), len(truth_stas), len(measu_objs))
    return truth_gals, truth_stas, measu_objs
    

def match_func(ra1st, dec1st, ra2st, dec2st, cat1, cat2, comp_dis=0.5):
    if len(cat1) > 0 and len(cat2) > 0:
        ra1=cat1[ra1st]
        dec1=cat1[dec1st]
        ra2=cat2[ra2st]
        dec2=cat2[dec2st]
        cosA=np.cos(np.mean(0)*np.pi/180.0)
        cosB=np.cos(np.mean(0)*np.pi/180.0)
        A= np.array([ra1*cosA, dec1]).transpose()
        B= np.array([ra2*cosB, dec2]).transpose()
        tree = cKDTree( B)
        dis, inds = tree.query(A , k=1, p=2)
        dis=dis*3600.0
        indA, =np.where(dis < comp_dis)
        indB=inds[indA]
        if len(indA) > 0:
           print ' %i objects matched'%(len(indA))
           return cat1[indA], cat2[indB]
        else: 
           print ' No matches found!'
           return [], []
    else:
           print 'Catalog empty!'
           return [], []

def estimate_dist(ra1, dec1, ra2, dec2):
        cosA=np.cos(np.mean(0)*np.pi/180.0)
        cosB=np.cos(np.mean(0)*np.pi/180.0)
        A= np.array([ra1*cosA, dec1]).transpose()
        B= np.array([ra2*cosB, dec2]).transpose()
        tree = cKDTree( B)
        dis, inds = tree.query(A , k=2, p=2)
        dis=dis*3600.0
        disB=dis[:, 1]
        return disB

def running_medians(xx, yy, binsize=1):
    bins_lo=np.arange(np.min(xx), np.max(xx), binsize)
    bins_up=bins_lo+binsize
    yy_med=np.zeros(len(bins_up))
    yy_lo=np.zeros(len(bins_up))
    yy_hi=np.zeros(len(bins_up))
    xx_bin=np.zeros(len(bins_up))-10.0**15.0
    for ii in range(len(bins_lo)):
	bin_xx_lo=bins_lo[ii]
        bin_xx_up=bins_up[ii]
        ind, =np.where( (xx > bin_xx_lo)&(xx < bin_xx_up) )
        if len(ind) > 0:
           yy_med[ii]=np.median(yy[ind])
           xx_bin[ii]=np.median(xx[ind])
           yy_lo[ii]=np.percentile(yy[ind], 15.9)
           yy_hi[ii]=np.percentile(yy[ind], 84.1)
    ind=np.where(xx_bin > -10.0**15.0)
    xx_bin=xx_bin[ind]
    yy_med=yy_med[ind]
    yy_lo=yy_lo[ind]
    yy_hi=yy_hi[ind]
    return xx_bin, yy_med, yy_lo, yy_hi
        
def dm_m_plot(t_gm, o_gm, t_sm, o_sm, up_perc=1, lo_perc=99, figname=None):
  plt.figure(figsize=(9, 9))
  if len(t_gm) > 0:
    plt.subplot(431)
    yy=o_gm['cm_mag'][:, 0]-t_gm['cm_mag'][:, 0]
    xx=t_gm['cm_mag'][:, 0]
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.title('Galaxies (cm_mag)', fontsize=10)
    plt.xlabel('True cm_mag (g) ', fontsize=10)
    plt.ylabel('Obs -True cm_mag (g)', fontsize=8)
 
    plt.subplot(434) 
    yy=o_gm['cm_mag'][:, 1]-t_gm['cm_mag'][:, 1]
    xx=t_gm['cm_mag'][:, 1]
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True cm_mag (r) ', fontsize=10)
    plt.ylabel('Obs -True cm_mag (r)', fontsize=8)

    plt.subplot(437) 
    yy=o_gm['cm_mag'][:, 2]-t_gm['cm_mag'][:, 2]
    xx=t_gm['cm_mag'][:, 2]
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True cm_mag (i) ', fontsize=10)
    plt.ylabel('Obs -True cm_mag (i)', fontsize=8)

    plt.subplot(4, 3, 10) 
    yy=o_gm['cm_mag'][:, 3]-t_gm['cm_mag'][:, 3]
    xx=t_gm['cm_mag'][:, 3]
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True cm_mag (z) ', fontsize=10)
    plt.ylabel('Obs -True cm_mag (z)', fontsize=8)

  if len(t_sm) > 0:
    plt.subplot(432)
    xx=t_sm['g_Corr']
    yy=o_sm['cm_mag'][:, 0]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2, label=None)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--', label='50, 15.9, 84.1 percentiles')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.title('Stars (cm_mag comparison)', fontsize=10)
    plt.xlabel('True mag (g) ', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (g)', fontsize=8)
    plt.legend(loc=3, fontsize=8)   

    plt.subplot(435)
    xx=t_sm['g_Corr']-t_sm['gr_Corr']
    yy=o_sm['cm_mag'][:, 1]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True mag (r) ', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (r)', fontsize=8)

    plt.subplot(438)
    xx=t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr']
    yy=o_sm['cm_mag'][:, 2]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True mag (i) ', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (i)', fontsize=8)

    plt.subplot(4, 3, 11)
    xx=t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr']-t_sm['iz_Corr']
    yy=o_sm['cm_mag'][:, 3]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True mag (z) ', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (z)', fontsize=8)

    plt.subplot(433)
    xx=t_sm['g_Corr']
    yy=o_sm['psf_mag'][:, 0]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.plot([14, 28], [0, 0], 'r:')
    plt.title('Stars (psf_mag comparison)', fontsize=10)
    plt.xlabel('True mag (g) ', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (g)', fontsize=8)

    plt.subplot(436)
    xx=t_sm['g_Corr']-t_sm['gr_Corr']
    yy=o_sm['psf_mag'][:, 1]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True mag (r) ', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (r)', fontsize=8)

    plt.subplot(439)
    xx=t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr']
    yy=o_sm['psf_mag'][:, 2]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True mag (i) ', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (i)', fontsize=8)

    plt.subplot(4, 3, 12)
    xx=t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr']-t_sm['iz_Corr']
    yy=o_sm['psf_mag'][:, 3]-xx
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([14, 28])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([14, 28], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('True mag (z) ', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (z)', fontsize=8)

  plt.tight_layout()
  if figname is None:
     plt.show()
     return []
  else:
     plt.savefig(figname)
     return figname

def dm_T_plot(t_gm, o_gm, t_sm, o_sm, up_perc=1, lo_perc=99, figname=None):
  plt.figure(figsize=(9, 9))
  if len(t_gm) > 0:
    ind=np.where((o_gm['cm_T'])> 0 & (o_gm['cm_T']< 10.0**15.0))
    t_gm=t_gm[ind]
    o_gm=o_gm[ind]
    plt.subplot(431)
    yy=o_gm['cm_mag'][:, 0]-t_gm['cm_mag'][:, 0]
    xx=np.log10(o_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 7])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 7], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy, binsize=1)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs -True cm_mag (g)', fontsize=8)
 
    plt.subplot(434) 
    yy=o_gm['cm_mag'][:, 1]-t_gm['cm_mag'][:, 1]
    xx=np.log10(o_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 7])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 7], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs -True cm_mag (r)', fontsize=8)

    plt.subplot(437) 
    yy=o_gm['cm_mag'][:, 2]-t_gm['cm_mag'][:, 2]
    xx=np.log10(o_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 7])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 7], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs -True cm_mag (i)', fontsize=8)

    plt.subplot(4, 3, 10) 
    yy=o_gm['cm_mag'][:, 3]-t_gm['cm_mag'][:, 3]
    xx=np.log10(o_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 7])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 7], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs -True cm_mag (z)', fontsize=8)

  if len(t_sm) > 0:
    ind=np.where((o_sm['cm_T'])> 0 & (o_sm['cm_T']< 10.0**15.0))
    t_sm=t_sm[ind]
    o_sm=o_sm[ind]
    plt.subplot(432)
    yy=o_sm['cm_mag'][:, 0]-(t_sm['g_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2, label=None)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--', label='50, 15.9, 84.1 percentiles')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.title('Stars (cm_mag comparison)', fontsize=10)
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (g)', fontsize=8)
    plt.legend(loc=3, fontsize=8)

    plt.subplot(435)
    yy=o_sm['cm_mag'][:, 1]-(t_sm['g_Corr']-t_sm['gr_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (r)', fontsize=8)

    plt.subplot(438)
    yy=o_sm['cm_mag'][:, 2]-(t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (i)', fontsize=8)

    plt.subplot(4, 3, 11)
    yy=o_sm['cm_mag'][:, 3]-(t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr']-t_sm['iz_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs cm_mag -True mag (z)', fontsize=8)

    plt.subplot(433)
    yy=o_sm['psf_mag'][:, 0]-(t_sm['g_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.plot([14, 28], [0, 0], 'r:')
    plt.title('Stars (psf_mag comparison)', fontsize=10)
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (g)', fontsize=8)

    plt.subplot(436)
    yy=o_sm['psf_mag'][:, 1]-(t_sm['g_Corr']-t_sm['gr_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (r)', fontsize=8)

    plt.subplot(439)
    yy=o_sm['psf_mag'][:, 2]-(t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (i)', fontsize=8)

    plt.subplot(4, 3, 12)
    yy=o_sm['psf_mag'][:, 3]-(t_sm['g_Corr']-t_sm['gr_Corr']-t_sm['ri_Corr']-t_sm['iz_Corr'])
    xx=np.log10(o_sm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-3, 5])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-3, 5], [0, 0], 'b:')
    xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
    plt.plot(xx_bin, yy_med, 'r--')
    plt.plot(xx_bin, yy_lo, 'r--')
    plt.plot(xx_bin, yy_hi, 'r--')
    plt.xlabel('Obs log10(cm_T)', fontsize=10)
    plt.ylabel('Obs psf_mag -True mag (z)', fontsize=8)

  plt.tight_layout()
  if figname is None:
     plt.show()
     return []
  else:
     plt.savefig(figname)
     return figname


def dm_dT_plot(t_gm, o_gm, t_sm, o_sm, up_perc=1, lo_perc=99, figname=None):
  plt.figure(figsize=(4, 9))
  if len(t_gm) > 0:
    ind=np.where((o_gm['cm_T'])> 0 & (o_gm['cm_T']< 10.0**15.0))
    t_gm=t_gm[ind]
    o_gm=o_gm[ind]
    plt.subplot(411)
    yy=o_gm['cm_mag'][:, 0]-t_gm['cm_mag'][:, 0]
    xx=(o_gm['cm_T']-t_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-10, 10000])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-1000, 10000], [0, 0], 'b:')
    plt.xscale('symlog')
    plt.xlabel('cm_T Obs-Truth', fontsize=10)
    plt.ylabel('Obs-True cm_mag (g)', fontsize=8)
 
    plt.subplot(412) 
    yy=o_gm['cm_mag'][:, 1]-t_gm['cm_mag'][:, 1]
    xx=(o_gm['cm_T']-t_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-10, 10000])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-1000, 10000], [0, 0], 'b:')
    plt.xscale('symlog')
    plt.xlabel('cm_T Obs-Truth', fontsize=10)
    plt.ylabel('Obs-True cm_mag (r)', fontsize=8)

    plt.subplot(413) 
    yy=o_gm['cm_mag'][:, 2]-t_gm['cm_mag'][:, 2]
    xx=(o_gm['cm_T']-t_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-10, 10000])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-1000, 10000], [0, 0], 'b:')
    plt.xscale('symlog')
    plt.xlabel('cm_T Obs-Truth', fontsize=10)
    plt.ylabel('Obs -True cm_mag (i)', fontsize=8)

    plt.subplot(414) 
    yy=o_gm['cm_mag'][:, 3]-t_gm['cm_mag'][:, 3]
    xx=(o_gm['cm_T']-t_gm['cm_T'])
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.xlim([-10, 10000])
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.plot([-1000, 10000], [0, 0], 'b:')
    plt.xscale('symlog')
    plt.xlabel('cm_T Obs-Truth', fontsize=10)
    plt.ylabel('Obs -True cm_mag (z)', fontsize=8)

  plt.tight_layout()
  if figname is None:
     plt.show()
     return []
  else:
     plt.savefig(figname)
     return figname

#------------------------------------------------------------------------------
# Plots added by Spencer

def df_f_plot(t_gf, o_gf, t_sf, o_sf, up_perc=1, lo_perc=99, figname=None):
  plt.figure(figsize=(9, 9))
  if len(t_gf) > 0:
    bands = ['g', 'r', 'i', 'z']
    for i in range(4):
        plt.subplot(4,3,3*i+1)
        yy=o_gf['cm_flux'][:, i]-t_gf['cm_flux'][:, i]
        xx=t_gf['cm_flux'][:, i]
        ind=np.where((yy>-10**4)&(yy < 10**4)&(o_gf['flags']==0)&(o_gf['cm_T']<100))
        xx=xx[ind];yy=yy[ind]
        plt.xlim([0, 10**4])
        plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
        plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
        plt.plot([0, 10**4], [0, 0], 'k:')
        xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
        plt.plot(xx_bin, yy_med, 'r--')
        plt.plot(xx_bin, yy_lo, 'r--')
        plt.plot(xx_bin, yy_hi, 'r--')
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        if i==0:
            plt.title('Galaxies Flux (cm_flux)', fontsize=10)
        plt.xlabel('True cm_flux ({})'.format(bands[i]), fontsize=10)
        plt.ylabel('Obs -True cm_flux ({})'.format(bands[i]), fontsize=8)

        # Chi scatter
        plt.subplot(4,3,3*i+2)
        yy=(o_gf['cm_flux'][:, i]-t_gf['cm_flux'][:, i]) / np.sqrt(o_gf['cm_flux_cov'][:, i, i])
        # Use old xx and ind
        yy=yy[ind]

        plt.xlim([0, 10**4])
        plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
        plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
        plt.plot([0, 10**4], [0, 0], 'k:')
        xx_bin, yy_med, yy_lo, yy_hi=running_medians(xx, yy)
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        plt.plot(xx_bin, yy_med, 'r--')
        plt.plot(xx_bin, yy_lo, 'r--')
        plt.plot(xx_bin, yy_hi, 'r--')
        if i==0:
            plt.title('Galaxies Flux Chi (cm_flux / cm_flux_err)', fontsize=10)
        plt.xlabel('True cm_flux chi ({})'.format(bands[i]), fontsize=10)
        plt.ylabel('Obs -True cm_flux chi ({})'.format(bands[i]), fontsize=8)

        # Chi scatter histogram
        yy=(o_gf['cm_flux'][:, i]-t_gf['cm_flux'][:, i]) / np.sqrt(o_gf['cm_flux_cov'][:, i, i])
        xx=t_gf['cm_flux'][:, i]
        # Makes histograms more uniform
        ind=np.where((yy>-10**2)&(yy < 10**2)&(o_gf['flags']==0)&(o_gf['cm_T']<100))
        xx=xx[ind]
        yy=yy[ind]
        plt.subplot(4,3,3*i+3)
        plt.xlim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
        plt.hist(yy, histtype='step', ec='k', bins=150)
        ax = plt.gca()
        ax.axvline(x=0, color='k', linestyle=':', linewidth=2)
        ax.xaxis.set_major_locator(plt.MaxNLocator(3))
        ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        if i==0:
            plt.title('Galaxies Chi Distribution', fontsize=10)
        plt.xlabel('Obs -True cm_flux chi ({})'.format(bands[i]), fontsize=8)
        plt.ylabel('Counts')

  plt.tight_layout()
  if figname is None:
     plt.show()
     return []
  else:
     plt.savefig(figname)
     return figname

def dT_dist_plot(t_gm, o_gm, t_sm, o_sm, oo, up_perc=1, lo_perc=99, figname=None):
  plt.figure()
  if len(t_gm) > 0:
    ind=np.where((o_gm['cm_T'])> 0 & (o_gm['cm_T']< 10.0**15.0))
    t_gm=t_gm[ind]
    o_gm=o_gm[ind]
    dists=estimate_dist(t_gm['ra'], t_gm['dec'], oo['ra'], oo['dec'])
    xx=o_gm['cm_weight']#-t_gm['cm_TdByTe']
    yy=o_gm['cm_T']/t_gm['cm_T']
    ind=np.where((yy>-10)&(yy < 10))
    xx=xx[ind];yy=yy[ind]
    plt.ylim([np.percentile(yy, up_perc), np.percentile(yy, lo_perc)])
    plt.scatter(xx, yy, 1, marker='o', alpha=0.2)
    plt.xlim([np.percentile(xx, up_perc), np.percentile(xx, lo_perc)])
  plt.tight_layout()
  if figname is None:
     plt.show()
     return []
  else:
     plt.savefig(figname)
     return figname

def make_all(basepath=None, tile_list=None, realizations=None, outdir=None):
    if basepath is None:
       basepath='/data/des71.a/data/kuropat/blank_test/y3v02/balrog_images/'
    if realizations is None:
       realizations=os.listdir(basepath)   
    if tile_list is None:
       tile_list=os.listdir( os.path.join(basepath, realizations[0]) )
    if outdir is None:
        outdir = os.getcwd()

    ## Make output directory if it does not yet exist
    if not os.path.exists(outdir):
       print 'output dir doesnt exist. Please make the output dir.'
       sys.exit(0)

    ##read in files
    tg, ts, oo=read_files(basepath, tile_list, realizations)
    ### doing matching
    truth_gm, obs_gm=match_func('ra', 'dec', 'ra', 'dec', tg, oo, comp_dis=0.5)
    truth_sm, obs_sm=match_func('RA_new', 'DEC_new', 'ra', 'dec', ts, oo, comp_dis=0.5)

    ### make plots
    names=[]
    ##Diff_m vs True_m plots
    fn1 = os.path.join(outdir, 'dm_m_YZ.png')
    names=np.append(names, dm_m_plot(truth_gm, obs_gm, truth_sm, obs_sm, figname=fn1))
    ##Diff_m vs Obs_T plots
    fn2 = os.path.join(outdir, 'dm_T_YZ.png')
    names=np.append(names, dm_T_plot(truth_gm, obs_gm, truth_sm, obs_sm, figname=fn2))
    ##Diff_m vs diff T plots
    fn3 = os.path.join(outdir, 'dm_dT_gals_YZ.png')
    names=np.append(names, dm_dT_plot(truth_gm, obs_gm, truth_sm, obs_sm, figname=fn3))
    ##Diff T vs distance to nearest neighbor plots
    # commented out. my experiment plot
    #fn4 = os.path.join(outdir, 'dT_dist_gals_YZ.png')
    #names=np.append(names, dT_dist_plot(truth_gm, obs_gm, truth_sm, obs_sm, oo, figname=fn4))
    ##Diff_f vs True_f plots
    fn4 = os.path.join(outdir, 'df_f_spencer.png')
    # names=np.append(names, df_f_plot(truth_gm, obs_gm, truth_sm, obs_sm, up_perc=0, lo_perc=100, figname=fn4))
    names=np.append(names, df_f_plot(truth_gm, obs_gm, truth_sm, obs_sm, figname=fn4))
    print 'generated plots: ', names
    return names

if __name__ == "__main__":

    ## We can make this fancier, but for now this is simple enough. Could use argparse instead.

    # First argument is basepath
    try:
        print(argv[1])
        basepath = argv[1]
    except IndexError:
        basepath = None

    # Second argument is output directory
    try:
        print(argv[2])
        outdir = argv[2]
    except IndexError:
        outdir = None

    make_all(basepath=basepath, outdir=outdir)
