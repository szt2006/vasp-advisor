The {{FILE|POTCAR}} file is a mandatory input file. It contains the pseudopotential for each atomic species in the same order as in the {{FILE|POSCAR}}. An example to create the {{FILE|POTCAR}} file for a structure with three elements is
  cat ~/pot/Al/POTCAR ~/pot/C/POTCAR ~/pot/H/POTCAR > POTCAR
The order must be the same order as defined in the {{FILE|POSCAR}} file.

Also see: 
* Simple instructions to set up a {{FILE|POTCAR}} file with the correct format: Preparing a POTCAR.

* Guide on recommendations:  Choosing pseudopotentials.
{{NB|important| The settings in the {{FILE|POTCAR}} file are read-only and must not be edited.}}
No standard usage of VASP requires modifying the {{FILE|POTCAR}} file. Specifically, do not modify the {{TAG|LEXCH}} tag in the {{FILE|POTCAR}} file. If you want to select a different functional, set the {{TAG|XC}}, {{TAG|GGA}} or {{TAG|METAGGA}} tag in the {{FILE|INCAR}} file.
## File format
{{FILE|POTCAR}} files contain a header section with some tags, and large blocks of tabulated data containing the actual pseudopotential.
More recent potential sets contain more information in the headers, so not all tags described below are present in all files ever distributed. Information about the atoms, i.e., their mass {{TAG|POMASS}}, their number of valence electrons {{TAG|ZVAL}}, the energy of the reference configuration for which the pseudopotential was created, etc. is present since VASP version 3.2. Since the release of the potpaw.54 potential set (VASP version 5.4) {{FILE|POTCAR}} files also contain a copyright notice and a unique hash that can be used for verification of the file.

Some data, e.g., additional information about the kinetic-energy density of the core-electrons, is not available in all {{FILE|POTCAR}} files, but required for METAGGA calculations

All {{FILE|POTCAR}}s end with the line  End of Dataset.

The Ti_pv potential from the potpaw_PBE.64 set, where the *3p* states are included in the valence, serves as an example to explain some tags in the following.
{{NB|mind|The information below is not complete. However, we believe that it covers the most information required in practice. Some other tags are also documented in the {{FILE|POTCAR}} file itself.}}

; {{TAG|TITEL}}
: The first line in any {{FILE|POTCAR}} file is the title of the pseudopotential. It is later printed again under the {{TAG|TITEL}} tag. Depending on the potential set, this might be more or less verbose. In our example, we have a PAW potential of Ti created with the PBE functional. The "_pv" suffix indicates that semicore *p*-states are included as valence electrons. We also see that this potential was created in September of 2000.
:TITEL  = PAW_PBE Ti_pv 07Sep2000
{{NB|tip|You may choose this string to indicate what pseudopotential you have used in your publication to ensure the reproducibility of your results.|:}}
; {{TAG|LEXCH}}
: This tag specifies the exchange-correlation functional used to create the potential. Even if another functional is selected in the {{FILE|INCAR}} via the {{TAG|XC}}, {{TAG|GGA}} or {{TAG|METAGGA}} tag, this information is required to recalculate the exchange-correlation energy inside the PAW spheres. Here, PE stands for the PBE functional.
:LEXCH  = PE
; {{TAG|ZVAL}}
: This specifies the number of valence electrons considered in the pseudopotential. It is printed in the second line of the {{FILE|POTCAR}} and again in the same line as {{TAG|POMASS}}.
; {{TAG|POMASS}}
: The atomic mass in atomic units. One can increase this in molecular dynamics calculations for light elements
:POMASS =   47.880; ZVAL   =   10.000    mass and valenz
; {{TAG|ENMAX}} and {{TAG|ENMIN}}
: These two tags are default plane-wave cutoffs for the pseudopotential in electron Volt (eV). {{TAG|ENMIN}} is the minimum viable, end {{TAG|ENMAX}} the recommended cutoff. For {{FILE|POTCAR}} files with more than one species, the maximum cutoffs ({{TAG|ENMAX}} or {{TAG|ENMIN}}) are used for the calculation. Note that the {{FILE|INCAR}} tag {{TAG|ENCUT}} overwrites the default from the {{FILE|POTCAR}}.
:ENMAX  =  222.335; ENMIN  =  166.751 eV
{{NB|tip|We recommend setting the {{TAG|ENCUT}} tag in the {{FILE|INCAR}} file.|:}}
; {{TAG|EAUG}}
: The energy cutoff for the plane-wave representation for the augmentation charges in eV. This might be overwritten in the {{FILE|INCAR}} using the tag {{TAG|ENAUG}}.
:EAUG   =  482.848
; Atomic configuration
: This block describes the atomic reference configuration used to create the pseudopotential. The first three columns, <i>n</i>, <i>l</i>, and <i>j</i> represent the principal, angular momentum, and total angular momentum <i>j</i>=|<i>l</i>+<i>s</i>| quantum numbers. This is followed by the total energy and the occupation numbers of the orbitals. Note that fractional occupations are possible because the reference configuration does not have to be the ground state. It is possible to deduce the valence-electron configuration of the potentential using the valence electron number ({{TAG|ZVAL}}): Add occupied states from the bottom of the table until it counts {{TAG|ZVAL}}, i.e., 10 in our example. Thus, we arrive at 3<i>p</i>63<i>d</i>34<i>s</i>1 for Ti_pv.
 Atomic configuration
    8 entries
     n  l   j            E        occ.
     1  0  0.50     -4865.3608   2.0000
     2  0  0.50      -533.1368   2.0000
     2  1  1.50      -440.5031   6.0000
     3  0  0.50       -59.3186   2.0000
     3  1  1.50       -35.7012   6.0000
     3  2  2.50        -1.9157   3.0000
     4  0  0.50        -3.7291   1.0000
     4  3  2.50        -1.3606   0.0000
## Related tags and sections
Available pseudopotentials, Prepare a POTCAR, Choosing pseudopotentials, Projector-augmented-wave formalism

Category:FilesCategory:Input filesCategory:Pseudopotentials
