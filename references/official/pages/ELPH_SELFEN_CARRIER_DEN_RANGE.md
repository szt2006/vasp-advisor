{{DISPLAYTITLE:ELPH_SELFEN_CARRIER_DEN_RANGE}}
{{TAGDEF|ELPH_SELFEN_CARRIER_DEN_RANGE|[real array]}}

Description: List of carrier density ranges in logarithmic scale (in cm^{-3}) at which to compute the phonon-mediated electron self-energy and transport coefficients. 
{{Available|6.6.0}}

----
From each carrier density specified in the array, a positive (electron doping) or negative (hole doping) number of electrons is added to the value of {{TAG|NELECT}} and the chemical potential computed. A range of carrier densities can be defined using {{TAG|ELPH_SELFEN_CARRIER_DEN_RANGE|l u n}}, where:
* *l* is the lower limit of the carrier density range.
* *u* is the upper limit of the carrier density range.
* *n* is the number of steps between the two limits.

The range of carrier densities is used to generate a log-scale mesh of carrier densities.
{{NB|important|*l* or *u* must be both positive (*n*-doping) or both negative (*p*-doping).}}

You can add the range (*l* *u* *n*) N times, so you can have several different meshes of holes or electrons or both. For example, {{TAG|ELPH_SELFEN_CARRIER_DEN_RANGE|-1e20 -1e16 51 1e20 1e16 51}} would create a list of two meshes of carrier densities, (-1e20 -1e16 51) and (1e20 1e16 51). The first mesh has 51 carrier densities of holes between -1e16 and -1e20; the second mesh has 51 carrier densities of electrons between 1e16 and 1e20. You could also include more meshes if you want. You can check the carriers that you have chosen in the {{FILE|OUTCAR}} file:

 Chemical potential calculation:
###### ===================
 elph_ismear=-24
 elph_fermi_nedos=     501
 elph_selfen_carrier_den=
  -0.100E+21
  -0.832E+20
  -0.692E+20
 ...
  -0.145E+17
  -0.120E+17
  -0.100E+17
   0.100E+21
   0.832E+20
   0.692E+20
 ...
   0.145E+17
   0.120E+17
   0.100E+17
## Related tags and articles
* Transport calculations
* Electron-phonon accumulators
* Chemical potential in electron-phonon interactions
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_SELFEN_MU}}
* {{TAG|ELPH_SELFEN_MU_RANGE}}
* {{TAG|ELPH_SELFEN_CARRIER_DEN}}
* {{TAG|ELPH_SELFEN_CARRIER_PER_CELL}}
* {{TAG|ELPH_SELFEN_TEMPS}}
* {{TAG|ELPH_SELFEN_TEMPS_RANGE}}
* {{TAG|NELECT}}

Category:INCAR tagCategory:Electron-phonon_interactions
