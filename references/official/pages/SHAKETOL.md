{{TAGDEF|SHAKETOL|[Real]|10^{-5}}}

Description: {{TAG|SHAKETOL}} specifies the tolerance for the SHAKE algorithm (in case VASP was compiled with -Dtbdyn).
----
Constrained molecular dynamics ({{TAG|MDALGO}}=1 {{!}} 2  {{!}} 3  {{!}} 4  {{!}} 5) are performed using a SHAKE algorithm.

{{TAG|SHAKETOL}} specifies the tolerance for the SHAKE algorithm.
If the error for all geometric constraints does not decrease below this predefined tolerance within the allowed number of iterations ({{TAG|SHAKEMAXITER}}), VASP terminates with an error message. This behavior can be changed by defining the soft convergence tolerance {{TAG|SHAKETOLSOFT}} > {{TAG|SHAKETOL}}, in which case the algorithm will not terminate if at least accuracy specified by {{TAG|SHAKETOLSOFT}} was reached.  
## Related tags and articles
{{TAG|SHAKETOLSOFT}},
{{TAG|SHAKEMAXITER}},
{{TAG|MDALGO}}

Constrained molecular dynamics

{{sc|SHAKETOL|Examples|Examples that use this tag}}
## References
</references>

----

Category:INCAR tagCategory:Advanced molecular-dynamics sampling
