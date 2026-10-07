{{DISPLAYTITLE:ELPH_DRIVER}}
{{TAGDEF|ELPH_DRIVER|el {{!}} mels|el}}

Description: Chooses which driver to use for electron-phonon calculations.
{{Available|6.5.0}}
{{NB|warning|There was a  known issue 54 for electron-phonon calculations using {{TAG|ISPIN|2}} for VASP 6.5.0 and 6.5.1 that was fixed in VASP 6.6.0.}}

----

This is a high-level tag that chooses what to compute during an electron-phonon calculation.
Currently, the following drivers are supported:

;{{TAG|ELPH_DRIVER|el}}
:Computes the phonon-induced electron self-energy. This can be used to compute the renormalization of the electronic band structure and electronic transport properties.
;{{TAG|ELPH_DRIVER|mels}}
:Computes the electron-phonon matrix elements and writes them to the {{FILE|vaspelph.h5}} file. For performance reasons, it is usually not recommended to write the matrix elements and process them externally. However, this mode is still useful for analyzing or plotting the matrix elements directly.
## Related tags and articles
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_DECOMPOSE}}
* {{TAG|ELPH_SELFEN_FAN}}
* {{TAG|ELPH_SELFEN_DW}}

Category:INCAR tagCategory:Electron-phonon_interactions
