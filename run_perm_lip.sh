#!/bin/bash

inputfile=''
verbose=false
print_usage() {
  printf "Usage: run_perm_lip.sh -f inputfile [-v]"
}

while getopts 'f:v' flag; do
  case "${flag}" in
    f) inputfile="${OPTARG}" ;;
    v) verbose='true' ;;
    *) print_usage
       exit 1 ;;
  esac
done

while IFS= read -r line 
do 
case $line in
       ''|\#*) continue ;;         # skip blank lines and lines starting with #
   esac
arr=($line)

# Read parameters

SUF=${arr[0]}
DATADIR=${arr[1]}
REF=${arr[2]}
TRAJ=${arr[3]}
FREQ=${arr[4]}
OUTPUTDIR=${arr[5]}
SUB=${arr[6]}

if [[ ${#arr[@]} -ne 7 ]]  
then
    echo "ERROR : 7 arguments needed in each line in input file parameters.in"
    exit 0
fi

echo "Reading inputfile :" $SUF
if [[ $verbose == 'true' ]] 
then
    echo "$SUF $DATADIR $FREQ $REF $TRAJ $OUTPUTDIR $SUB"
    echo "$DATADIR/$REF"
    echo "$DATADIR/$TRAJ"

fi
# Get resid and time of permeation events
#echo -e "$SUF\nREF_$SUF.gro\traj_${SUF}_${FREQ}pspf.xtc\n"| \
perm_lip.py -r $DATADIR/$REF \
            -f $DATADIR/$TRAJ \
            -o $OUTPUTDIR \
            -x $SUF \
            -p \
            -t \
            -s $SUB
#            -v

done < $inputfile
