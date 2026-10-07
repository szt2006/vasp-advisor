{{DISPLAYTITLE:IFC_LR}}
{{TAGDEF|IFC_LR|[integer]|1}}

Description: Controls the treatment of the long-range part of the interatomic force constants during electron-phonon calculations.
{{Available|6.5.0}}

----

This tag controls the treatment of the long-range electrostatic contributions to the interatomic force constants (IFC) arising in polar dielectric materials.
{{TAG|IFC_LR|1}} has the same effect as {{TAG|LPHON_POLAR|True}} but is used in the context of electron-phonon interactions.
{{NB|mind|In this case, the required Born effective charges and dielectric tensor are read from the {{FILE|phelel_params.hdf5}} file.}}
## Modes
;{{TAG|IFC_LR|0|op=≤}}
:No long-range correction scheme is applied to the IFC matrix. This is most likely very inaccurate for semiconductors and insulators with non-vanishing Born effective charge.
;{{TAG|IFC_LR|1}}
:Dipole corrections are applied to the IFC matrix.
## Related tags and articles
* Bandstructure renormalization
* Transport calculations
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_LR}}

Category:INCAR tagCategory:Electron-phonon_interactions
