{{TAGDEF|NELMGW|[integer]|1}}

Description: {{TAG|NELMGW}} sets the number of self-consistent GW steps.
Available as of 6.3.0.

----
This tag is effective for {{TAG|ALGO}}=EVGW[0] | QPGW[0] | GW[0][R][K] and ignored otherwise.
For instance
 {{TAG|ALGO}} = EVGW0
 {{TAG|NELMGW}} = 4
performs a  partially self-consistent GW calculations, where G is updated four times. 

Omit {{TAG|NBANDS}} and {{TAG|NELM}} to select the single-step GW procedure.
## Related tags and articles
{{TAG|ALGO}}, GW calculations

{{sc|NELMGW|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Many-body perturbation theoryCategory:GWCategory:Low-scaling GW and RPA
