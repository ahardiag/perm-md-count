# perm-md-count

Compute the Cumulative Number of Permeation of water molecules in a lipid bilayer in Molecular Dynamics simulations.

Quick start
===========


Installation
------------
Here are the steps to install **perm-md-count** in `~/Programs`, but you can of course change the installation directory.

1. Clone this repository on your computer.
   ```bash
   mkdir -p ~/Programs
   cd ~/Programs
   git clone https://github.com/ahardiag/perm-md-count.git
   ```

2. Add the main script `perm_lip.py` to your python modules. 
For example, if you have a directory with some executable python script like /path/to/python/modules/, you need to link the main script on this program into this directory:
    ```bash
   ln -s ~/Programs/perm_lip/perm_lip.py /path/to/python/modules/ 
   ```
3. Install the dependencies :
This algorithm uses the python packages **MDAnalysis**, **numpy** and **pandas**.
The best way to use `perm-md-count` is to run the executables in a conda environment with the librairies installed and the versions used during the development :
    ```bash
    conda env create --file "~/Programs/perm-md-count/perm_lip.yml" -n perm_lip
    conda activate perm_lip
   ```
4. Add the bash executable `run_perm_lip.sh` to your bash modules to run several analysis sequentially. 
    ```bash
   ln -s ~/Programs/perm-md-count/run_perm_lip.sh /path/to/bash/modules/ 
   ```


Tutorial
--------

To run the program, you need to provide an input file (by default `parameters.in` ) to your bash executable. In each line of this file - except comments and empty lines - are specified the parameters of the algorithm.
All arguments in the same line must appear in the same order as in the following example:

    #SUF            DATADIR REF               TRAJ                     FREQ    OUTDIRNAME  SUB 
    SC8_6chnd_test3 ./      ref_SC8_6chnd.gro traj_SC8_6chnd_50ns.xtc  1000    test3/sub1  1
    
Then you just have to run the executable in a directory where you want to store results:

    run_perm_lip.sh -f parameters.in

More information about the main python script can be obtained with :

    perm_lip.py --help


MD trajectories
-------
In principle, all formats that are readable by `mdanalysis` can be used. **The membrane must be centered in the box**. If several membranes are present in your system, just center your system on the membrane of interest. In order to delimit the membrane boundaries, the program consider only the lipids (phosphor atoms) located in a layer of $2\cdot MAX=60\AA$ around the central z-plane ($z = z_{box}/2$).

Parameters
-------
Parameters      | Definition
----------------|-----------------------------------------------------------
SUF             | The keyword name, appended to output filenames.
DATADIR         | The relative path for the trajectory data.
REF             | The reference file (.pdb,.gro,.tpr) where resids are defined. 
TRAJ            | The trajectory file (.xtc,.gro,.tpr).
OUTDIRNAME      | The name of the sub-directory to find outputs.
FREQ            | The sampling frequency (duration time in _ns_ between two frames to analyze).
SUB             | The subdivision of the total number of water molecules. By default : 1. Useful for large systems and /or low RAM memory.

Outputs
-------
On can find the output files in the sub-directory ./outputs/`OUTDIRNAME` :
- a _csv_ file :

water_index  | resid |  time_per_frame(ps)  |   time(frame) |   time(ns)|   duration(frames) | direction |  permeations_tot
|-|-|-|-|-|-|-|-|
1843|2255|100|58|5.8|41.0|-1|0|
...|...|...|...|...|...|...|...|

Each line corresponds to a water permeation event, defined as a displacement of a water molecule from one leaflet limit (phosphorus atom of the bilayer) to the opposite leaflet. The corresponding events with periodic boundary crossings are excluded.

The first column has no column name, it is a simple index. By default, the program sort the permeation events with respect to the time of appearance, so the index dos not start from 0.
The following information is extracted from the algorithm :

    water_index          : the index of the water molecule in MDAnalysis
    resid                : the residue index, given in the reference file.
    time_per_frame(ps)   : same argument as FREQ (see above)
    time(frame)          : the frame number which corresponds to the exit of the bilayer
    time(ns)             : same event in nanosecond
    duration(frames)     : the time spent in the bilayer/channel
    direction            : the direction of the motion of the water molecule 
                           (+1 : from the lower to the upper compartment;
                            -1 : from the upper to the lower compartment)
    permeations_tot      : the cumulative number of total permeations (in both 
                           direction) 

- a _log_ file  : a text file with the name of the input files. Useful for post-processing.

Other files created in tests:
- a _.sel_ file : the selection of all resids of the water molecule. Useful to visualize in VMD.

Tests
-------
    cd tests
    chmod u+x run_test1.sh
    ./run_test1.sh

Citation
-------
If you use **perm-md-count** in your research, please cite the following article:

Hardiagon, A.; Murail, S.; Huang, L.-B.; van der Lee, A.; Sterpone, F.; Barboiu, M.; Baaden, M. Molecular Dynamics Simulations Reveal Statistics and Microscopic Mechanisms of Water Permeation in Membrane-Embedded Artificial Water Channel Nanoconstructs. J. Chem. Phys. 2021, 154 (18), 184102. https://doi.org/10.1063/5.0044360.

TEST