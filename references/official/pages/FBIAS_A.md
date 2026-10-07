{{DISPLAYTITLE:FBIAS_A}}
{{TAGDEF|FBIAS_A|[real (array)]}}

Description: Defines the step height for the bias potential in eV.
----

{{TAG|FBIAS_A}} defines the height of the step (A_{\mu}) in the Fermi-like step-shaped bias potential of the following form:

::
\tilde{V}(\xi_1,\dots,\xi_{M_4}) = \sum_{\mu=1}^{M_4}\frac{A_{\mu}}{1+\text{exp}\left [-D_{\mu}(\frac{\xi(q)}{\xi_{0\mu}} -1) \right ]}, \;

where the sum runs over all (M_4) coordinates the potential acts upon, which are defined in the {{FILE|ICONST}} file by setting the status to 4.
The units of A_{\mu} are eV.
The number of items defined via {{TAG|FBIAS_A}} must be equal to M_4, otherwise the calculation terminates with an error message.
## Related tags and articles
{{TAG|FBIAS_R0}},
{{TAG|FBIAS_D}},
{{FILE|ICONST}},
{{TAG|Biased molecular dynamics}}
----
Category:INCAR tagCategory:Advanced molecular-dynamics sampling
