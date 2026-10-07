{{TAGDEF|NGY|[integer]|set in accordance with {{TAG|PREC}} and {{TAG|ENCUT}}}}

Description: {{TAG|NGY}} sets the number of grid points in the FFT grid along the second lattice vector.
----
By default {{TAG|NGY}} is set in accordance with the requested "precision" mode {{TAG|PREC}} and the plane wave kinetic energy cutoff {{TAG|ENCUT}}:

::{| cellpadding="5" cellspacing="0" border="1"
  {{TAG|PREC}} ||align="center"| {{TAG|NGY}} 
  Normal ||align="center"| 3/2&times;G_{\rm cut} 
  Single (VASP.5) ||align="center"| 3/2&times;G_{\rm cut}
  Single (VASP.6) ||align="center"| 2&times;G_{\rm cut}
  SingleN (VASP.6) ||align="center"| 3/2&times;G_{\rm cut}
  Accurate ||align="center"| 2&times;G_{\rm cut}
  Low ||align="center"| 3/2&times;G_{\rm cut}
  Medium ||align="center"| 3/2&times;G_{\rm cut}
  High ||align="center"| 2&times;G_{\rm cut}

where
:E_{\rm cut}=\frac{\hbar^2}{2m_e}G_{\rm cut}^2
with E_{\rm cut}={{TAG|ENCUT}}.

Alternatively, {{TAG|NGY}} can be set to a specific value in the {{FILE|INCAR}} file.
## Related tags and articles
{{TAG|NGX}},
{{TAG|NGZ}},
{{TAG|NGXF}},
{{TAG|NGYF}},
{{TAG|NGZF}},
{{TAG|PREC}},
{{TAG|ENCUT}},
{{TAG|ENAUG}}

{{sc|NGY|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Projector-augmented-wave method
