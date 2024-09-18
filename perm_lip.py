#!/usr/bin/env python

'''
Program that computes permeation of water through a lipid membrane (with phosphorus atoms) and embedded channels.

Output files : created in the directory provided by input arguments :
- a CSV file with columns : water_index resid time_per_frame(ps) time(frame) time(ns) duration(frames) direction 
- a LOG file with the list of the processed filenames

For module dependencies, convenience usage is to use virtual environment in python with following packages :
- python 3.7.5
- MDAnalysis 0.20.1
- numpy 1.17.3

Updates:
---
05/2020 
- compute absolute number of permeations and relative number of permeations
- check if membrane is centered along the z-axis of the membrane and calculate selections from box dimensions
----
09/2021
- improve docstring with argparse 
10/2021
- add subdivision groups of water to be used with large trajectories
'''

import MDAnalysis as mda
import numpy as np
import os, sys, psutil, time, glob, re
import math
import argparse
from argparse import RawTextHelpFormatter
import pandas as pd

########################################### DEFAULTS PARAMETERS ##############################################################
MIN_DISP_MEMB=30   #  Minimum threshold displacement in Angstrom 
                        #  for corrections to periodic conditions , must be close to membrane thickness
MEMORY=False            #  put this variable to false to avoid load trajectory in RAM
##############################################################################################################################

def parse_args(required=False):
    parser = argparse.ArgumentParser(description="Program that computes permeation of water\n"
                                            " through a lipid membrane (with phosphorus atoms) and embedded channels/protein.\n"
                                            "For selection commands, see MDAnalysis doc :\n"
                                            "https://docs.mdanalysis.org/stable/documentation_pages/selections.html",
                                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("-f", "--traj",
                        required=required,
                        nargs="+",
                        help="Trajectory file (.xtc,.trr).")
    parser.add_argument("-r", "--ref",
                        required=required,
                        help="Reference or first frame file (.pdb, .gro).")
    parser.add_argument("-o", "--outdirname",
                        default=".",
                        help="Output Sub-directory name.")
    parser.add_argument("-x", "--suffixname",
                        help="Output suffix name.")
    parser.add_argument("-v","--verbose",
                        action="store_true",
                        help="Increase verbosity and print the passed arguments.")
    parser.add_argument("-p","--process",
                        action="store_true",
                        help="Sort dataframe with time, and add a column with cumulative permeations.")
    parser.add_argument("-t","--time",
                        action="store_true",
                        help="Print performance and timing in sdtout.")
    parser.add_argument("-s", "--sub",
                        type=int,
                        default=1,
                        help="Number of subgroups of water molecules.")
    parser.add_argument("--print_limits",
                        action="store_true",
                        help="Print the position of the boundaries in a csv file.")
    return parser.parse_args()
    
def get_memory():
    '''Check RAM'''
    process = psutil.Process(os.getpid())
    print("\n ---> Allocated memory %10.2f MB"%(process.memory_info().rss/(1024)**2))  # in megabytes 
    print(" ---> Available memory %10.2f MB\n"%(psutil.virtual_memory().available/(1024)**2))
    
### Functions for human sorting (or natural sorting) 
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def progress(count, total, status=''):
    '''
    https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
    '''
    bar_len = 10
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def split(a, n):
    '''
    From a list of elements, return a list generator of n approximately equally sized lists
    '''
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

### Main()
start_time = time.time()



### get arguments and debugging mode 
args=parse_args(required=True)
if args.verbose:
    for arg,val in vars(args).items():
        print(arg,val)

### Create output folders and filenames
PATH_TO_OUTPUT="outputs/{}/".format(args.outdirname)
if args.suffixname:
    suf="_"+args.suffixname
else:
    suf=""
PERM_FILE="permeation{}.csv".format(suf)
LIMIT_FILE="limits{}.csv".format(suf)
LOGFILE="permeation{}.log".format(suf)        # filename for log file

if not os.path.exists(PATH_TO_OUTPUT):
    os.makedirs(PATH_TO_OUTPUT)

### Check Data
#assert len(glob.glob("*.xtc"))>0, "No data with extension .xtc found ! \n"

### Loading Trajectory in Memory and writing a log file to save data paths
ref =args.ref
traj=args.traj

if MEMORY:
    ("Loading trajectory files %s in memory ..." %str(traj))

u = mda.Universe(ref,traj,in_memory=MEMORY)

### Writing log files with absolute paths of all data files related
with open(PATH_TO_OUTPUT+LOGFILE,"w") as stdlog:
    stdlog.write("%s\n"%(os.path.abspath(ref)))
    for filename in traj: 
        stdlog.write("%s\n"%(os.path.abspath(filename)))
    stdlog.write("%s\n"%(os.path.abspath(PATH_TO_OUTPUT+PERM_FILE)))
    stdlog.write("%s\n"%(os.path.abspath(PATH_TO_OUTPUT+LOGFILE)))

get_memory()

# Define boundaries using only the closest phosphor atoms from the center
xbox,ybox,zbox=u.coord.dimensions[:3]
limit_memb=u.select_atoms("name P")
limit_sup=limit_memb.select_atoms("prop z > %f and prop z < %f"%(zbox/2,zbox/2+MIN_DISP_MEMB),updating=True)
limit_inf=limit_memb.select_atoms("prop z < %f and prop z > %f"%(zbox/2,zbox/2-MIN_DISP_MEMB),updating=True)
assert limit_inf.atoms.n_atoms!=0 , "Selections of Phosphore atoms from the bilayer is empty, check that the membrane is centered in the box."

nframes = u.trajectory.n_frames-1
z_inf_traj=np.zeros(nframes)
z_sup_traj=np.zeros(nframes)
limits=np.zeros((nframes,3))

for iframe,ts in enumerate(u.trajectory[1:]):
    progress(iframe, nframes, status='Reading trajectory to compute boundaries.')
    z_inf_traj[iframe]=limit_inf.positions[:,2].mean()
    z_sup_traj[iframe]=limit_sup.positions[:,2].mean()
    limits[iframe] = [iframe,z_inf_traj[iframe],z_sup_traj[iframe]]

if args.print_limits:
    pd.DataFrame(limits).to_csv(PATH_TO_OUTPUT+LIMIT_FILE,sep="\t")

# Select oxygen atoms in water molecules
waterox_tot=u.select_atoms("resname TIP3 SOL TP3 and name OW OH2")
assert waterox_tot.atoms.n_atoms!=0 ,   "Selection of all water molecule is empty"\
                                    "Check that the residue name for water is either"\
                                    "TIP3 TP3 or SOL"
stdout=open(PATH_TO_OUTPUT+PERM_FILE,"w")
stdout.write("water_index resid time_per_frame(ps) time(frame) time(ns) duration(frames) direction\n")

### Iterate over all subgroups of water atoms
list_ag=split(waterox_tot,args.sub)
count=0
count_rel=0       

for (isub,waterox) in enumerate(list_ag):

    # Data arrays for water positions wrt to phosphore limits
    nb_waters = len(waterox.atoms.resids)
    size_array=nb_waters*nframes/(1024**2)
    print("Will generate numpy arrays (int64) with size (%d,%d) -> %4.2f MB per array.\n"%(nb_waters,nframes,size_array))
    assert size_array < 100 , "Too many values to unpack in one single array, change the number of groups of molecule to treat by -s option!"

    z=np.zeros((nb_waters,nframes))
    old_z=np.zeros((nb_waters,nframes))

    PS_PER_FRAME = u.trajectory.ts.dt
    NS_PER_FRAME = PS_PER_FRAME*0.001 # Time between each step in ns 

    #initialize the old coordinates
    u.trajectory[0]
    old_z[:,0]=waterox.positions[:,2]
    # excluding first frame since history is ignored in the first frame
    for iframe,ts in enumerate(u.trajectory[1:]):
        progress(iframe, nframes, status='Reading trajectory : part %d over %d'%(isub+1,args.sub))
        # mean position of phosphores in the upper and lower leaflets
        #z_inf_traj[iframe]=limit_inf.positions[:,2].mean()
        #z_sup_traj[iframe]=limit_sup.positions[:,2].mean()

        #coordinates
        z[:,iframe]=waterox.positions[:,2]

    old_z[:,1:nframes]=z[:,:nframes-1] 

    get_memory()

    ### Storing History of z coordinates for water molecules and boundaries inf and sup of the membrane
    print("Store a simplified trajectory for each water molecule ...")

    ### Computing the error due to PBC jumps, comparing z positions and membrane boundaries
    # MIN_DISP_MEMB is the minimal distance above which a z-translation of a molecule inside the membrane can be considered as a periodic boundary artifact

    test_disp=abs(z-old_z)>MIN_DISP_MEMB

    is_inf=np.zeros((nb_waters,nframes),dtype=bool)
    is_sup=np.zeros((nb_waters,nframes),dtype=bool)
    is_rel=np.zeros((nb_waters,nframes),dtype=bool)
    for i in range(z.shape[0]):
        is_inf[i]=z[i,:nframes]<z_inf_traj[:nframes]
        is_sup[i]=z[i,:nframes]>z_sup_traj[:nframes]
        is_rel[i]=(z[i,:nframes]<(z_inf_traj+z_sup_traj)[:nframes]/2)
    is_memb=np.invert(is_inf+is_sup)
    is_memb_inf=is_rel*np.invert(is_inf)
    is_memb_sup=np.invert(is_rel)*np.invert(is_sup)

    # Compute a simplified trajectory with labels in {-1,0,1}
    # Divide the box in 4 regions :
    # - upper water bulk
    # - upper membrane
    # - lower membrane
    # - lower water bulk
    # Assign the following state to each water molecule :
    # -1 if the molecule is below  the membrane boundary (inside the lower water bulk)
    # 0  if the molecule is inside the membrane/channel
    # 1  if the molecule is above  the membrane boundary (inside the upper water bulk)
    # -1 if the molecule is inside the upper membrane and has just jumped through the BC (criteria involving MIN_DISP_MEMB)
    # 1  if the molecule is inside the lower membrane and has just jumped through the BC (criteria involving MIN_DISP_MEMB)

    traj_simp=(is_inf[:,:nframes-1]*-1
               +is_sup[:,:nframes-1]*1
               +is_memb[:,:nframes-1]*0 # maybe useless
               +test_disp[:,:nframes-1]*(is_memb_sup[:,:nframes-1]*1+is_memb_inf[:,:nframes-1]*-1)
               +test_disp[:,1:nframes]*(is_memb_sup[:,:nframes-1]*1+is_memb_inf[:,:nframes-1]*-1))
    nmol,nmoves=traj_simp.shape

    get_memory()

    ### processing simplified trajectory to compute time of permeations for each water molecules
    print("Processing coordinates and writing results ...")

    # Loop on each single trajectories
    for index,value in enumerate(traj_simp[:,:]):
        history= np.zeros(nmoves,dtype=int)
        history[0]=value[0]
        label_previous=value[0] # first position in memory

        # Compute the history at each time : the sign gives the bulk region visited (-1 or +1) and the value gives the frame number elapsed since the last bulk visit
        for i,position in enumerate(value[:]):
            history[i]=0 # initialize history
            if (position==1):
                history[i]=1
            elif (position==-1):
                history[i]=-1
            else :
                if (label_previous>0):
                    history[i]=label_previous+1
                elif (label_previous<0):
                    history[i]=label_previous-1
            label_previous=history[i]

        # calculating an array with type of jump
        # Identify in a array the type of jump at each time ({-2,+2} : pbc , -1: exit in the lower compartment, 0:,same region, +1: exit in the upper compartment)    
        diff= value[1:nmoves]-value[:nmoves-1]

        # return an array with integer value corresponding to permeation time and sign refers to direction of permeation
        # condition requires :
        # - permeation occurs when departing from membrane (value-diff=0)
        # - permeation occurs when the value the jump (diff) is opposed sign of the last past state (history) 
        events_sparse=(value[1:]-diff==0)*(history[:nmoves-1]*diff<0)*diff*(np.arange(nmoves-1)+2)
        events_bool=(events_sparse != 0)
        events=events_sparse[events_bool]
        #duration_frames=abs((events_bool*history[:nmoves-1]*diff)[events_bool])
        duration_frames=abs(history[:nmoves-1][events_bool])
        direction_perm=diff[events_bool]

        if events.size:
            for i,time_frame in enumerate(events):
                count+=1 # count number of permeation
                count_rel+=direction_perm[i]
                resid,time_ns=waterox.resids[index],time_frame*NS_PER_FRAME    
                stdout.write("%5d %5d %5d %5d %6.3f %6.3f %5d\n" 
                         %(index,resid,PS_PER_FRAME,abs(time_frame),abs(time_ns),duration_frames[i],direction_perm[i]))
stdout.close()

# Sort rows with respect to event times and add a column with cumulative permeation
if args.process:
    df=pd.read_csv(PATH_TO_OUTPUT+PERM_FILE,delimiter="\s+")
    df=df.sort_values(by=['time(ns)'],axis=0)
    df["permeations_tot"]=np.arange(df.shape[0])
    df.to_csv(PATH_TO_OUTPUT+PERM_FILE,sep="\t")

print("\nOutput files created with success in%s :\n%s\n%s\n\n"
" ---> %5d events of permeation during %6.3f ns!\n ---> Relative number of permeations : %5d\n"%(os.path.abspath(PATH_TO_OUTPUT),PERM_FILE,LOGFILE,count,float(nframes*NS_PER_FRAME),count_rel))

if args.time:
    print("Performance %4.2f seconds \n" % (time.time() - start_time))
