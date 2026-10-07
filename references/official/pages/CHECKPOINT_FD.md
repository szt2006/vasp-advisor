{{DISPLAYTITLE:CHECKPOINT_FD}}
{{TAGDEF|CHECKPOINT_FD| CONTINUE {{!}} RESET {{!}} NONE {{!}} SINGLE | RESET}}

Description: Enables a finite differences calculation to be restarted or split up into displacements.

----

Phonons can be calculated using  finite differences. A series of displacements is made, DFT calculations are performed on each of these, and then the second-order force constants are computed and the dynamical matrix constructed, from which the phonon modes and frequencies are calculated. Using {{TAG|CHECKPOINT_FD}} (with {{TAG|IBRION|6}}), it is possible to  restart a calculation that crashed from the last displacement, or  split the calculation into individual displacements. The displacements are written to the {{FILE|vaspcheckfd.h5}} file.
{{Available|6.6.0}}
{{NB|important|This feature requires  HDF5 support.}}
{{NB|mind|This is currently only available for {{TAG|IBRION|6}}.}}
----
### {{TAG|CHECKPOINT_FD|CONTINUE}}
:The {{FILE|vaspcheckfd.h5}} file is read (if it exists) and the calculation continues where it left off. If the {{FILE|vaspcheckfd.h5}} file is missing, a {{FILE|vaspcheckfd.h5}} is created and the displacements are written to it. In both cases, the calculation will finish with the complete {{FILE|vaspcheckfd.h5}}. Repeating {{TAG|CHECKPOINT_FD|CONTINUE}} will perform a single SCF at the equilibrium structure and read the displacements from {{FILE|vaspcheckfd.h5}}. 
:This mode also detects if the calculation is a single VASP calculation or if it was split into separate pieces. If it has been split, all the calculations need to have finished, or an error will be produced.
### {{TAG|CHECKPOINT_FD|RESET}} (default)
:Overwrite the {{FILE|vaspcheckfd.h5}} file and start from scratch. The rest is identical to {{TAG|CHECKPOINT_FD|CONTINUE}}.
### {{TAG|CHECKPOINT_FD|NONE}}
:No {{FILE|vaspcheckfd.h5}} file is written. This is the behavior of the code before VASP 6.6.0.
### {{TAG|CHECKPOINT_FD|PREPARE}}
:The {{FILE|vaspcheckfd.h5}} file is created (or overwritten) and filled with metadata. For each displacement, a {{FILE|CONTCAR_disp-N}} file is written containing the Nth displacement. The calculation stops after performing one electronic minimization to obtain the SCF solution of the unperturbed structure. 
:To run the calculation for a specific displacement, create a directory disp-N, copy across the corresponding {{FILE|CONTCAR_disp-N}} file and rename it to {{FILE|POSCAR}}. Then, run the calculation with {{TAG|CHECKPOINT_FD|SINGLE}}.
### {{TAG|CHECKPOINT_FD|SINGLE}}
:This mode is used to run the individual single-shot VASP calculations produced by {{TAG|CHECKPOINT_FD|PREPARE}}. This also produces a {{FILE|vaspcheckfd.h5}} file in the corresponding directory that contains the displaced data.
## Related tags and articles
Phonons from finite differences, Restarting finite differences calculations, {{TAG|IBRION}}, {{FILE|vaspcheckfd.h5}}, {{FILE|CONTCAR_disp-N}}

{{sc|CHECKPOINT_FD|HowTo|Workflows that use this tag}}
Category:INCAR tagCategory:Phonons
