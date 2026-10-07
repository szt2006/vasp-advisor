{{DISPLAYTITLE:PHON_NEDOS}}
{{TAGDEF|PHON_NEDOS| [integer] }}
{{DEF|PHON_NEDOS|2000|}}

Description: Sets the number of frequency points to compute the phonon density of states.

----

The density of states is computed between 
[\omega_{\text{min}}-5\sigma,\omega_{\text{max}}+5\sigma] with 
\omega_{\text{min}} and 
\omega_{\text{max}} the lowest and highest phonon frequency and 
\sigma the broadening {{TAG|PHON_SIGMA}}.
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
