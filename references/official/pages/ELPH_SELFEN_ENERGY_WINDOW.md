{{DISPLAYTITLE:ELPH_SELFEN_ENERGY_WINDOW}}
{{TAGDEF|ELPH_SELFEN_ENERGY_WINDOW|[real, real]| 0.0 0.0}}

Description:  
Specifies the energy window (in eV) around the band edges within which the electron-phonon self-energy is computed.  
{{Available|6.5.0}}

----
The self-energy is evaluated for electronic states with energies in the intervals around the valence band minimum (VBM) and the conduction band minimum (CDM), with an energy window defined with {{TAG|ELPH_SELFEN_ENERGY_WINDOW|*a* *b*}}:

* from VBM – *a* up to VBM, and  
* from CBM up to CBM + *b*
## Related tags and articles
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_TRANSPORT}}
* {{TAG|ELPH_SCATTERING_APPROX}}
* {{TAG|ELPH_SELFEN_IMAG_SKIP}}
Category:INCAR tagCategory:Electron-phonon_interactions
