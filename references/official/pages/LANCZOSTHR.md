{{NB|deprecated|This feature is deprecated and will be removed in a future release. Please use {{TAG|BSEPREC}} instead.}}

{{TAGDEF|LANCZOSTHR|[real]|10^{-3}}}

Description: {{TAG|LANCZOSTHR}} is used by the BSE Lanczos algorithm to stop the iterative procedure, once the dielectric function has reached numerical convergence.

----

The difference between the dielectric function at two consecutive iterations, i and i+1, is computed as root-mean-square over the frequency grid

::
\mathrm{RMS}[\epsilon] = \sqrt{\sum_{j=1}^N\frac{1}{N}\left[\epsilon_{i}(\omega_j)-\epsilon_{i+1}(\omega_j)\right]^2}

and once \mathrm{RMS}[\epsilon]<={{TAG|LANCZOSTHR}} the iterative algorithm stops. 
## Related tag and articles
{{TAG|BSE}},
BSE calculations,
Bethe-Salpeter equations
----
Category:INCAR tagCategory:Bethe-Salpeter equationsCategory:Many-body perturbation theory
