{{TAGDEF|INCREM|[real array]|0}}

Description: {{TAG|INCREM}} controls the transformation velocity in the slow-growth approach (in case VASP was compiled with -Dtbdyn).
----
In slow-growth simulations ({{TAG|MDALGO}}=1 {{!}} 2), the value of each controlled geometric parameter with STATUS=0 is increased by {{TAG|INCREM}} in every simulation step.

It must be supplied for each controlled geometric parameter for which STATUS=0 was specified in the {{FILE|ICONST}}-file.
## Related tags and articles
{{TAG|MDALGO}},
{{TAG|ICONST}}

{{sc|INCREM|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Advanced molecular-dynamics sampling
