{{DISPLAYTITLE:SPRING_V0}}
{{TAGDEF|SPRING_V0|[real (array)]}}
{{DEF|SPRING_V0|0|for all coordinates with status{{=}}8 in {{FILE|ICONST}}.}}

Description: Rate at which the bias potential is shifted in uc/fs.
----
Consider the bias potential for a molecular-dynamics (MD) run of the form:

::
\tilde{V}(\xi_1,\dots,\xi_{M_8}) = \sum_{\mu=1}^{M_8}\frac{1}{2}\kappa_{\mu} (\xi_{\mu}(q)-\xi_{0\mu})^2, \;
 

where the sum runs over all (M_8) coordinates the potential acts upon (\xi_{\mu}(q)). The coordinates are defined in the {{FILE|ICONST}} file by setting the status=8.
Optionally, the position of minimum (\xi_{0\mu}) can be shifted at a constant rate \dot{\xi}_{\mu} every MD step, i.e.,

::
\xi_{0\mu}(t+\Delta t) = \xi_{0\mu}(t) + \dot{\xi}_{\mu}(q)\Delta t, \;

where \Delta t is the time step used in MD ({{TAG|POTIM}}). 
The rate \dot{\xi}_{\mu} can be defined via the parameter {{TAG|SPRING_V0}} and its units are uc/fs, where uc corresponds to the units of the coordinate the potential acts upon (e.g., {\AA} for coordinates with flag R, rad. for coordinates with flag A, dimensionless for coordinates with flag W, etc...).
The number of items defined via {{TAG|SPRING_V0}} must be equal to M_8, otherwise the calculation terminates with an error message.
## Related tags and articles
{{TAG|SPRING_K}},
{{TAG|SPRING_R0}},
{{FILE|ICONST}},
{{TAG|Biased molecular dynamics}}
----
Category:INCAR tagCategory:Advanced molecular-dynamics sampling
