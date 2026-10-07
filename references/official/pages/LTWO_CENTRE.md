{{TAGDEF|LTWO_CENTRE|[logical]|.FALSE.}}
{{DISPLAYTITLE:LTWO_CENTRE}}
Description: {{TAG|LTWO_CENTRE}} calculates off-center Coulomb integrals. 
----
When chosen, the system calculates two types of integrals:

* Bare integrals (stored in {{FILE|VRijkl}})
::
V_{ijkl}^{\sigma\sigma'} =  \int {\rm d}{\bf r}\int {\rm d}{\bf r}'
\frac{w_{i}^{*\sigma}({\bf r}) w_{j}^{\sigma}({\bf r}) w_{k}^{*\sigma'}({\bf r}'+{\bf R}) w_{l}^{\sigma'}({\bf r}'+{\bf R})}{|{\bf r}-{\bf r}'|}

* Effectively screened integrals (stored in {{FILE|URijkl}})
::
U_{ijkl}^{\sigma\sigma'} =  \int {\rm d}{\bf r}\int {\rm d}{\bf r}'
w_{i}^{*\sigma}({\bf r}) w_{j}^{\sigma}({\bf r}) U({\bf r},{\bf r}',\omega)
w_{k}^{*\sigma'}({\bf r}'+{\bf R}) w_{l}^{\sigma'}({\bf r}'+{\bf R})

When chosen, cRPA matrix elements in {{FILE|vaspout.h5}} can be used with {{py4vasp}} to analyze the spatial decay of the Coulomb interaction using the Ohno potential{{cite|kaltak:prb:2025}}

U(R) = \frac{U(R=0)}{\sqrt{\frac{R}\delta + 1}}

import py4vasp as pv

calc = pv.Calculation.from_path(".")
calc.effective_coulomb.plot(selection="U V", radius=...)

The above plots the spatial decay of the Coulomb interaction and fits the Ohno potential to the off-center integrals. Using radius=... passes the radial grid directly from the VASP output.
{{Available|6.6.0}}
## Related tags and articles
{{FILE|VRijkl}},
{{FILE|URijkl}},
{{TAG|LDISENTANGLED}},
{{TAG|LWEIGHTED}},
{{TAG|LSCRPA}},
{{TAG|ALGO}}

{{sc|LTWO_CENTRE|Howto|Workflows that use this tag}}
## References
Category:INCAR_tagCategory:Constrained-random-phase approximation
