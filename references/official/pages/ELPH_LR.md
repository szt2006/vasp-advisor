{{DISPLAYTITLE:ELPH_LR}}
{{TAGDEF|ELPH_LR|[integer]|1}}

Description: Controls the treatment of the long-range part of the electron-phonon potential.
{{Available|6.5.0}}

----

This tag controls the treatment of the long-range electrostatic contributions to the electron-phonon coupling arising in polar dielectric materials.
{{NB|mind|In this case, the required Born effective charges and dielectric tensor are read from the {{FILE|phelel_params.hdf5}} file.}}
## Modes
;{{TAG|ELPH_LR|0|op=≤}}
:No long-range correction scheme is applied to the electron-phonon coupling. This is most likely very inaccurate for semiconductors and insulators with non-vanishing Born effective charge.
;{{TAG|ELPH_LR|1}}
:Dipole corrections are applied to the electron-phonon coupling{{cite|engel:prb:2022}}.
## Related tags and articles
* Bandstructure renormalization
* Transport calculations
* {{TAG|ELPH_RUN}}
* {{TAG|IFC_LR}}

Category:INCAR tagCategory:Electron-phonon_interactions
## References
