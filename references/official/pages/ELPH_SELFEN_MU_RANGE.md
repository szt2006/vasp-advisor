{{DISPLAYTITLE:ELPH_SELFEN_MU_RANGE}}
{{TAGDEF|ELPH_SELFEN_MU_RANGE|[real array]}}

Description: List of the range of chemical potentials (in eV) at which to compute the phonon-mediated electron self-energy and transport coefficients. 
{{Available|6.5.0}}

----
A set of different chemical potentials can be set using {{TAG|ELPH_SELFEN_MU_RANGE}} as a shift with respect to the Fermi level E_F as an alternative to {{TAG|ELPH_SELFEN_MU}}. 
A range of chemical potentials can be defined using {{TAG|ELPH_SELFEN_MU_RANGE|l u n}}, where:

* *l* is the lower limit of the chemical potential range.
* *u* is the upper limit of the chemical potential range.
* *n* is the number of steps between the two limits.

For example, {{TAG|ELPH_SELFEN_MU_RANGE|-1.0 1.0 101}} would create a list of <b>101</b> points around the Fermi level between E_F - 1.0 and E_F + 1.0. 
## Related tags and articles
* Transport calculations
* Electron-phonon accumulators
* Chemical potential in electron-phonon interactions
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_SELFEN_MU}}
* {{TAG|ELPH_SELFEN_CARRIER_DEN}}
* {{TAG|ELPH_SELFEN_CARRIER_DEN_RANGE}}
* {{TAG|ELPH_SELFEN_CARRIER_PER_CELL}}
* {{TAG|ELPH_SELFEN_TEMPS}}
* {{TAG|ELPH_SELFEN_TEMPS_RANGE}}
* {{TAG|NELECT}}

Category:INCAR tagCategory:Electron-phonon_interactions
