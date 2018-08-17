#!/bin/bash
#
# CALL PARAMETERS - <meds base> derectory where data will be;
#                   <tilename>
#                   <mode> positional code 1 -prep only; 2 - coadd and catalog 
#	                4 - meds for base; 8 - injection; 16 - coadd and catalog for injected; 
#	                32 - meds for injected; 63 - all together
#                   <ncpu> - number of CPUs to be used by GalSim, by defauld the progrm will use
#                            ncpu equal the number of bands
#
echo $1
echo $HOME
HOSTNAME=`/bin/hostname`
DATE=`/bin/date +%H%M%S`
medsbase=$1
tilename=$2
mode=$3
ncpu=$4
source /cvmfs/des.opensciencegrid.org/eeups/startupcachejob21i.sh
setup galsim 1.5.1tmv # Brian's updated build
setup swarp 2.36.2+3
setup mofpsfex 0.3.2
setup psycopg2 2.4.6+7
setup despyastro 0.3.9+2
setup pil 1.1.7+13
setup fitsverify
setup pathos
setup healpy
setup esutil 0.6.2rc1+1
#setup meds 0.9.3rc2
setup pixcorrect 0.5.3+12
setup sextractor 2.23.2+4
setup despydb
setup IntegrationUtils 2.0.9+1
setup ngmixer y3v0.9.4c
setup meds 0.9.3+0
#setup desmeds 0.9.2.2+0
setup covmatrix 0.9.0+1 
setup cfitsio 3.370+0
setup easyaccess
#
export BALROG_BASE=`pwd`
export PYTHONPATH=${BALROG_BASE}/Balrog-GalSim/balrog:${PYTHONPATH}
#
export PYTHONPATH=${BALROG_BASE}/balrogutils/python/:${PYTHONPATH}
export PATH=${BALROG_BASE}/balrogutils/bin/:$PATH
export DESMEDS_CONFIG_DIR=${BALROG_BASE}/desmeds-config/
export PYTHONPATH=${BALROG_BASE}/desmeds/python/:$PYTHONPATH
export PATH=${BALROG_BASE}/desmeds/bin/:$PATH

#
cd ../
mkdir -p ${medsbase}/
export MEDS_DATA=`pwd`/${medsbase}
cd ${BALROG_BASE}
echo "MEDS_DATA="${MEDS_DATA}
# We have to redifine MEDS_DIR variable as Erin expect it be 
# the place where we put all results
export MEDS_DIR=${MEDS_DATA}
echo "MEDS_DIR="${MEDS_DIR}
#
export DESDATA=${BALROG_BASE}/DESDATA

export medsconf="y3v02"
#
# Now edit bal_config.yaml to make absolute path for input data
#
cd Balrog-GalSim/config
sed "s(BALROG-BASE(${BALROG_BASE}(g" config_template_COSMOS.yaml > bal_config.yaml
#sed "s(BALROG-BASE(${BALROG_BASE}(g" config_template.yaml > bal_config.yaml
cat bal_config.yaml >> ${BALROG_BASE}/base_${tilename}.log 2>&1
cd ${BALROG_BASE}
ls -l  >> base_${tilename}.log 2>&1
#
#
export PYTHONPATH=${BALROG_BASE}/Balrog-GalSim/balrog:${PYTHONPATH}

#
# Now execute BalrogBase.py
#
echo "running BalrogBase.py in mode:"$mode
BalrogBase.py -c desmeds-config/meds-y3v02.yaml -t $tilename -m $mode -n $ncpu >& base_${tilename}.log 