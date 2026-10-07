{{TAGDEF|VCAIMAGES|[real]|-1}}

Description: The tag {{TAG|VCAIMAGES}} allows to perform thermodynamic integrations (TI); it defines the coupling parameter &lambda;. 
----
{{TAG|VCAIMAGES}} allows two molecular dynamics (MD) simulations to be performed with e.g. different {{TAG|POTCAR}} or {{TAG|KPOINTS}} files or different exchange-correlation functionals, and averages the energies and forces between the two calculations. This is known as thermodynamic integration (TI) {{cite|dorner:PRL:2018}}.

The tag {{TAG|VCAIMAGES}} internally splits the available nodes into two groups, and each group then performs an independent VASP calculation (this implies {{TAG|VCAIMAGES}} only works in the MPI version). This behavior is implemented in the same way as the  nudged elastic band method (NEB) described under the tag {{TAG|IMAGES}}. As opposed to NEB, only two images are created ({{TAG|IMAGES}}=2 is set internally). The two calculations are performed in subdirectories 01 and 02 (00 and 03 are not required, in contrast to NEB).
### Description of reading a writing during the calculation
The two calculations are performed essentially independently in subdirectories 01 and 02. The forces, energies, and the stress tensor of the two calculations are averaged according to the coupling parameter supplied by {{TAG|VCAIMAGES}}. Specifically, the value supplied in the tag {{TAG|VCAIMAGES}} determines the weight of the calculations performed in subdirectory 01. The weight of the second image is 1-{{TAG|VCAIMAGES}}. After self-consistency has been reach for both calculations, the energies and forces are averaged, affecting the final total energy as well as the forces. This ensures that the trajectories for the two MD simulations are identical. 
{{NB|important|Make sure that the initial {{FILE|POSCAR}} is identical in both subdirectories.}}
### Finding the energies
The averaged energies can be found in the {{TAG|OUTCAR}} file after the lines
ENERGY OF THE ELECTRON-ION-THERMOSTAT SYSTEM (eV), as well as in the file {{TAG|OSZICAR}}
(in the lines writing the free energy F=). This can make looking for the energies of the individual calculation awkward. You can find these under FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV) in the {{FILE|OUTCAR}} file for a DFT calculation (They are under ML FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV) for a machine-learned force field (MLFF)).  
{{NB|important|In some cases it might be desirable to use a different number of cores for
the first image and the second image. E.g., when the thermodynamic integration is performed from a coarse to a dense k-point grid, or from a cheap
to an expensive exchange-correlation functional. To set the number of cores in the first image the tag {{TAG|NCORE_IN_IMAGE1}} has to be set. The second image then 
contains the remaining cores.}}
The usage of this tag is also explained in the supplementary information of reference {{cite|dorner:PRL:2018}}.
## Related tags and articles
{{TAG|NCORE_IN_IMAGE1}}, {{TAG|SCALEE}}, {{TAG|IMAGES}}, Thermodynamic integration calculations
## References
Category:INCAR tagCategory:Advanced molecular-dynamics sampling
