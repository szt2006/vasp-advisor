{{TAGDEF|NGXF|[integer]|set in accordance with {{TAG|PREC}}, {{TAG|NGX}}, {{TAG|ENCUT}} and {{TAG|ENAUG}}}}

Description: {{TAG|NGXF}} sets the number of grid points in the "fine" FFT grid along the first lattice vector.
----
On this "fine" FFT mesh the localized augmentation charges are represented if ultrasoft pseudopotentials (USPPs) or the PAW method are used. In case USPPs are used, the local potentials (exchange-correlation, Hartree-potential and ionic potentials) are also calculated on this "fine" FFT-mesh.

By default {{TAG|NGXF}} is set in accordance with the requested "precision" mode {{TAG|PREC}}, {{TAG|NGX}}, and the plane wave kinetic energy cutoffs {{TAG|ENCUT}} and {{TAG|ENAUG}}:

::{| cellpadding="5" cellspacing="0" border="1"
  {{TAG|PREC}} ||align="center"| {{TAG|NGX}} ||align="center"| {{TAG|NGXF}}
  Normal ||align="center"| 3/2&times;G_{\rm cut} ||align="center"| 2&times;{{TAG|NGX}}
  Single (VASP.5) ||align="center"| 3/2&times;G_{\rm cut} ||align="center"| {{TAG|NGX}}
  Single (VASP.6) ||align="center"| 2&times;G_{\rm cut} ||align="center"| {{TAG|NGX}}
  SingleN (VASP.6) ||align="center"| 3/2&times;G_{\rm cut} ||align="center"| {{TAG|NGX}}
  Accurate ||align="center"| 2&times;G_{\rm cut} ||align="center"| 2&times;{{TAG|NGX}}
  Low ||align="center"| 3/2&times;G_{\rm cut} ||align="center"| 3&times;G_{\rm aug}
  Medium ||align="center"| 3/2&times;G_{\rm cut} ||align="center"| 4&times;G_{\rm aug}
  High ||align="center"| 2&times;G_{\rm cut} ||align="center"| 16/3&times;G_{\rm aug}

where
:E_{\rm cut}=\frac{\hbar^2}{2m_e}G_{\rm cut}^2 \qquad E_{\rm aug}=\frac{\hbar^2}{2m_e}G_{\rm aug}^2
with E_{\rm cut}={{TAG|ENCUT}} and E_{\rm aug}={{TAG|ENAUG}}.

Alternatively, {{TAG|NGXF}} can be set to a specific value in the {{FILE|INCAR}} file.
## Related tags and articles
{{TAG|NGX}},
{{TAG|NGY}},
{{TAG|NGZ}},
{{TAG|NGYF}},
{{TAG|NGZF}},
{{TAG|PREC}},
{{TAG|ENCUT}},
{{TAG|ENAUG}}

{{sc|NGXF|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Projector-augmented-wave method
