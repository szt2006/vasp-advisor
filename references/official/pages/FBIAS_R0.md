{{DISPLAYTITLE:FBIAS_R0}}
{{TAGDEF|FBIAS_R0|[real (array)]}}

Description: Defines the half-step position for the bias potential.
----
{{TAG|FBIAS_R0}} defines the half-step position (\xi_{0\mu}) for the Fermi-like step-shaped bias potential of the following form:

::
\tilde{V}(\xi_1,\dots,\xi_{M_4}) = \sum_{\mu=1}^{M_4}\frac{A_{\mu}}{1+\text{exp}\left [-D_{\mu}(\frac{\xi(q)}{\xi_{0\mu}} -1) \right ]}, \;

where the sum runs over all (M_4) coordinates the potential acts upon, which are defined in the {{FILE|ICONST}} file by setting the status to 4.
The units of \xi_{0\mu} correspond to units of the coordinate the potential acts upon (e.g., {\AA} for coordinates with flag R, rad. for coordinates with flag A, dimensionless for coordinates with flag W, etc...).
The number of items defined via {{TAG|FBIAS_R0}} must be equal to M_4. Otherwise, the calculation terminates with an error message.
## Related tags and articles
{{TAG|FBIAS_A}},
{{TAG|FBIAS_D}},
{{FILE|ICONST}}
----
Category:INCAR tagCategory:Advanced molecular-dynamics sampling
