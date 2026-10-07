{{TAGDEF|SHAKEMAXITER|[Integer]|1000}}

Description: {{TAG|SHAKEMAXITER}} specifies the maximum number of iterations in the SHAKE algorithm (in case VASP was compiled with -Dtbdyn).
----
Constrained molecular dynamics ({{TAG|MDALGO}}=1 {{!}} 2) are performed using a SHAKE algorithm.

If the error for all geometric constraints does not decrease below a predefined tolerance ({{TAG|SHAKETOL}}) within the allowed number of iterations, VASP terminates with an error message. 
The aforementioned maximum number of iterations is set by means of the {{TAG|SHAKEMAXITER}} tag.
## Related tags and articles
{{TAG|SHAKETOL}},
{{TAG|SHAKETOLSOFT}},
{{TAG|MDALGO}}

Constrained molecular dynamics

{{sc|SHAKEMAXITER|Examples|Examples that use this tag}}
## References
</references>

----
Category:INCAR tagCategory:Advanced molecular-dynamics sampling
