There are three main output files: {{FILE|OUTCAR}} in human-readable format, {{FILE|vasprun.xml}} in xml format, and {{FILE|vaspout.h5}} in HDF5 format. The {{FILE|OUTCAR}} file gives detailed human-readable output of a VASP run with roughly the following format:
*A summary of the used input parameters (e.g., {{FILE|INCAR}} tags), the starting structure (cf. {{FILE|POSCAR}}), the k-point mesh (cf. {{FILE|KPOINTS}}), and the pseudopotentials used (cf. {{FILE|POTCAR}} and choosing pseudopotentials).
*Information about the electronic steps, KS-eigenvalues.
*Stress tensors.
*Forces on the atoms.
*Local charges and magnetic moments.
*Dielectric properties
*The amount of output written onto the {{FILE|OUTCAR}} file can be chosen by modifying the {{TAG|NWRITE}} tag in the {{TAG|INCAR}} file.
## INCAR tags
### Common tags
The output to the {{TAG|OUTCAR}} file is determined by {{FILE|INCAR}} tags. The output for these is documented on their respective tag or how-to pages. Some of the most common tags are:
*the {{TAG|IBRION}} tag selects structure optimization - {{TAG|IBRION|1-3}}, molecular dynamics (MD) calculations - {{TAG|IBRION|0}}, or phonon calculations - {{TAG|IBRION|5-6}}. 
*{{TAG|ISIF}} selects for degrees of ionic and structural freedom in structural optimization and MD.
*{{TAG|ALGO}} is used to define the electronic minimization algorithm that is used or to select the many-body perturbation theory (MBPT) algorithm, e.g., the GW approximation, the random-phase approximation (RPA), the Bethe-Salpeter equation (BSE).
### Property tags
There are also many tags for specific properties, such as electron-phonon interactions (cf. the long list of ELPH_ tags at the end of the category page), nuclear magnetic resonance (NMR) - e.g., chemical shielding ({{TAG|LCHIMAG}}), electric field gradient EFG ({{TAG|LEFG}}), etc. 

There are several other output files which we summarize below, along with several common tags for
## Related tags and articles
* Output and input files: {{FILE|INCAR}}, {{FILE|POSCAR}}, {{FILE|KPOINTS}}, {{FILE|POTCAR}}, {{FILE|OSZICAR}}, {{FILE|IBZKPT}}, {{FILE|CHGCAR}}, {{FILE|WAVECAR}}, {{FILE|vasprun.xml}}, {{FILE|vaspout.h5}}.
* Controlling output verbosity: {{TAG|NWRITE}}.
* Output-controlling tags: chemical shielding, electric field gradient, hyperfine coupling constant, dielectric function, Born effective charges and dielectric tensor (DFPT), Born effective charges (finite-differences), X-ray core-level binding energies, optics, density of states (DOS).

Category:Files Category:Output files
