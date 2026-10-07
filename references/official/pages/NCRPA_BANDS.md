{{DISPLAYTITLE:NCRPA_BANDS}}
{{TAGDEF|NCRPA_BANDS|[integer array]}}

Description: Controls which bands are excluded in the constrained random-phase approximation. Check also {{TAG|NTARGET_STATES}}.

----
This tag is effective for {{TAG|ALGO|CRPA}} and ignored otherwise.

For instance 
 NCRPA_BANDS = 21 22 23 
removes all screening effects between bands 21, 22 and 23 from the constrained random-phase approximation of the screened Coulomb interaction. 
## Related tags and articles
{{TAG|ALGO}},
{{TAG|NTARGET_STATES}}

{{sc|NCRPA_BANDS|Howto|Workflows that use this tag}}

Category:INCAR tagCategory:Many-body perturbation theoryCategory:Constrained-random-phase approximation
