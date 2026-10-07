{{DISPLAYTITLE:ELPH_NBANDS}}
{{TAGDEF|ELPH_NBANDS|[integer]| {{TAG|NBANDS}}}}

Description: Number of bands to compute on the dense <b>k</b> point grid for the electron-phonon driver
{{Available|6.5.0}}

----
For transport calculations, this value should be as little as possible while including all the states potentially participating in the transport calculation.

If {{TAG|ELPH_NBANDS}}=-2 then the number of bands is set to the maximum number of plane waves. This setting is particularly useful for calculating the  bandgap renormalization.
In this case, the final result converges slowly with the number of bands in the calculation, similar to RPA, and BSE calculations.
## Related tags and articles
* Bandstructure renormalization
* Transport calculations
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_NBANDS_SUM}}
* {{TAG|ELPH_SELFEN_FAN}}
* {{TAG|ELPH_SELFEN_DW}}

Category:INCAR tagCategory:Electron-phonon_interactions
