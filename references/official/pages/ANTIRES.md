{{TAGDEF|ANTIRES|0 {{!}} 1 {{!}} 2|0}}

Description: {{TAG|ANTIRES}} determines whether the Tamm-Dancoff approximation is used or not. 

----
*{{TAG|ANTIRES}}=0 Tamm-Dancoff approximation (TDA)
*{{TAG|ANTIRES}}=1 yields exact results at &omega;{{=}}0 at roughly the same cost  as TDA
*{{TAG|ANTIRES}}=2 beyond Tamm-Dancoff, coupling between positive and negative frequencies

VASP uses the procedures outlined in reference  to include contributions beyond TDA. Beyond-TDA calculations increase the computational time and memory requirements by typically a factor of 2.
## Related tags and articles
{{TAG|BSE calculations}}

{{sc|ANTIRES|Examples|Examples that use this tag}}
## References
</references>
----

Category:INCAR tagCategory:Many-body perturbation theoryCategory:Bethe-Salpeter equations
