#!/ibpc/telesto/hardiagon/anaconda3/bin/python

"""
Analyze data in csv output from previous permeation.py program 
Inputs :
1 name of the csv file
2 flag for output name
3 (opt) time offset for printing water molecule selection
Outputs:
- png format
- pdf format
- data in xvg format
- sel file with name of the selections of the water molecules that permeates in the simulatuon

"""

import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import sys,os

def list2str(l):
    """
    Transform list to string with whitespace.
    """
    string=''
    for el in l : string+=' '+str(el)
    return string

dirname=os.path.dirname(sys.argv[1])
if dirname == "": dirname="."

assert len(sys.argv)>2, \
"Usage : python plot_perm_tot.py file.csv flag (time_offset)\n"

assert sys.argv[1] != ".csv" \
 "First argument must be a csv file \n"

FLAG_SIM=sys.argv[2]

if len(sys.argv)>3:
    TIME_OFFSET=float(sys.argv[3])
else:
    TIME_OFFSET=0

X_data= pd.read_csv(sys.argv[1], sep='\s+', header=0, skipinitialspace=True)

X=X_data[X_data["time(ns)"]>TIME_OFFSET]

#Add total number of permeations
X=X.sort_values(by='time(ns)')
X['permeations_tot']= [i+1 for i in range(len(X))]

print("Saving total permeation events over time in png and pdf format...\n")

plt.figure()
plt.step(X['time(ns)'],X['permeations_tot'],'-',where='post')
plt.title('Cumulated Total number of Permeations \n in %s'%FLAG_SIM,fontsize=18)
plt.xlabel('time(ns)',fontsize=16)
plt.ylabel('# permeations',fontsize=16)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlim(TIME_OFFSET,)
plt.ylim(0,)

plt.savefig('%s/permeation_cumul_%s.png'%(dirname,FLAG_SIM))
plt.savefig('%s/permeation_cumul_%s.pdf'%(dirname,FLAG_SIM))

print("Saving data in xvg format...\n")

with open(dirname+"permeation_"+FLAG_SIM+".xvg","w") as fxvg:
    for t,perm in zip(X['time(ns)'],X['permeations_tot']):
        #print("%6.2f% 6.2f"%(t,perm))
        fxvg.write("%6.2f% 6.2f\n"%(t,perm))

print("Writing selection of water molecules that have permeated, for visualization in VMD ...\n")

with open(dirname+"permeation_"+FLAG_SIM+".sel","w") as fsel:
    sel='resname SOL TIP3 and resid'+list2str(X['resid'].tolist())
    fsel.write(sel)
