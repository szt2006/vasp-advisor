{{DISPLAYTITLE:SPRING_K}}
{{TAGDEF|SPRING_K|[real (array)]}}

Description: Force constant for harmonic bias potential.
----
The parameter {{TAG|SPRING_K}} defines force constants (\kappa_{\mu}) for the harmonic bias of the following form:

::
\tilde{V}(\xi_1,\dots,\xi_{M_8}) = \sum_{\mu=1}^{M}\frac{1}{2}\kappa_{\mu} (\xi_{\mu}(q)-\xi_{0\mu})^2 \;

where the sum runs over all (M_8) coordinates the potential acts upon (\xi_{\mu}(q)), which are defined in the {{FILE|ICONST}} file by setting the status to 8.
The units of \kappa_{\mu} are eV/uc where uc units of coordinate the potential acts upon (e.g., {\AA} for coordinates with flag R, rad. for coordinates with flag A, dimensionless for coordinates with flag W, etc...)
The number of items defined via {{TAG|SPRING_K}} must be equal to M_8, otherwise the calculation terminates with an error message.
## Related tags and articles
{{TAG|SPRING_R0}},
{{TAG|SPRING_V0}},
{{FILE|ICONST}},
{{TAG|Biased molecular dynamics}}
----
Category:INCAR tagCategory:Advanced molecular-dynamics sampling
