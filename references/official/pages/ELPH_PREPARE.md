{{DISPLAYTITLE:ELPH_PREPARE}}
{{TAGDEF|ELPH_PREPARE|[logical]|.FALSE.}}

Description: Writes the potential, the force-constants and other information related to electron-phonon interactions to the {{FILE|vaspout.h5}} file.
{{Available|6.5.0}}

----

In order to calculate electron-phonon interactions, one must first perform finite-difference calculations in the supercell and generate the {{FILE|phelel_params.hdf5}} file.
To do this using phelel (https://github.com/phonopy/phelel), it is necessary to provide additional supercell information to phelel.
This is accomplished by setting {{TAG|ELPH_PREPARE|True}} in each involved supercell calculation.
Afterwards, phelel can be used to calculate the required derivatives and produce the {{FILE|phelel_params.hdf5}} file.
For further information on this workflow, please consult the online documentation of phelel (https://github.com/phonopy/phelel).
## Related tags and articles
* Electron-phonon potential from supercells
* {{FILE|phelel_params.hdf5}}

Category:INCAR tagCategory:Electron-phonon_interactions
