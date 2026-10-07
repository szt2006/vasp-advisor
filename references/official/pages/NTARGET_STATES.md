{{DISPLAYTITLE:NTARGET_STATES}}
{{TAGDEF|NTARGET_STATES|[integer array]}}

Description: Controls which Wannier states are excluded in constrained random-phase approximation. Check also {{TAG|NCRPA_BANDS}}.

----
This tag is effective for {{TAG|ALGO|CRPA}} and ignored otherwise.
For instance 
 NTARGET_STATES = 1 2 4 
selects the Wannier state 1, 2 and 4, where the ordering of the Wannier states depends on the chosen basis set.
## Related tags and articles
{{TAG|ALGO}},
{{TAG|NCRPA_BANDS}},
{{TAG|LOCALIZED_BASIS}}

{{sc|NTARGET_STATES|Howto|Workflows that use this tag}}
Category:INCAR tagCategory:Wannier functionsCategory:Many-body perturbation theoryCategory:Constrained-random-phase approximationCategory:Strongly correlated electrons
