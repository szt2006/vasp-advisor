{{DISPLAYTITLE:PHON_SIGMA}}
{{TAGDEF|PHON_SIGMA| [real] }}
{{DEF|PHON_SIGMA|0.0005 eV|}}

Description: Set the width of the Gaussian function in eV to compute the phonon density of states.

----

The density of states is computed between 
[\omega_{\text{min}}-5\sigma,\omega_{\text{max}}+5\sigma] with 
\omega_{\text{min}} and 
\omega_{\text{max}} the lowest and highest phonon frequency and 
\sigma the broadening {{TAG|PHON_SIGMA}}.
The number of energy points in this interval is set by {{TAG|PHON_NEDOS}}.
{{NB|mind| Only available as of VASP 6.4.0.}}
## Related tags and articles
{{FILE| QPOINTS}},
{{TAG | PHON_NWRITE}},
{{TAG | LPHON_POLAR}},
{{TAG | PHON_DIELECTRIC}},
{{TAG | PHON_BORN_CHARGES}},
{{TAG | PHON_G_CUTOFF}}

{{sc|LPHON_DISPERSION|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Phonons
