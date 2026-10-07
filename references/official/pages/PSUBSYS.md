{{TAGDEF|PSUBSYS|[real array]}}

Description: {{TAG|PSUBSYS}} sets the collision probabilities for the atoms in each atomic subsystem in calculations with multiple Anderson thermostats (in case VASP was compiled with -Dtbdyn).
----
Up to three user-defined atomic subsystems may be coupled with independent Andersen thermostats ({{TAG|MDALGO}}=13).

The collision probabilities for the atoms in each atomic subsystem is set by means of the {{TAG|PSUBSYS}} tag (one has to specify one number for each subsystem).

Note: 0 &le; {{TAG|PSUBSYS}} &le; 1
## Related Tags and Sections
{{TAG|NSUBSYS}},
{{TAG|TSUBSYS}},
{{TAG|MDALGO}}

{{sc|PSUBSYS|Examples|Examples that use this tag}}
## References
</references>
----

Category:INCAR tagCategory:Molecular dynamics
