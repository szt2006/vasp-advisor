{{TAGDEF|NSUBSYS|[integer array]}}

Description: {{TAG|NSUBSYS}} defines the atomic subsystems in calculations with multiple Anderson thermostats (in case VASP was compiled with -Dtbdyn).
----
Up to three user-defined atomic subsystems may be coupled with independent Andersen thermostats ({{TAG|MDALGO}}=13).

These subsystems are defined by specifying the last atom for each subsystem (two or three values must be supplied). For instance, if total of 20 atoms is defined in the {{FILE|POSCAR}}-file, and the initial 10 atoms belong to the subsystem 1, the next 7 atoms to the subsystem 2, and the last 3 atoms to the subsystem 3, {{TAG|NSUBSYS}} should be defined as follows:

 {{TAG|NSUBSYS}}= 10 17 20

Note that the last number in the previous example is actually redundant (clearly the last three atoms belong to the last subsystem) and does not have to be user-supplied.
## Related tags and articles
{{TAG|TSUBSYS}},
{{TAG|PSUBSYS}},
{{TAG|MDALGO}}

{{sc|NSUBSYS|Examples|Examples that use this tag}}
## References
</references>
----

Category:INCAR tagCategory:Molecular dynamics
