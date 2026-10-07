{{DISPLAYTITLE:ELPH_SELFEN_TEMPS_RANGE}}
{{TAGDEF|ELPH_SELFEN_TEMPS_RANGE|[real array]}}

Description: The range of temperatures (in K) at which to compute the phonon-mediated electron self-energy and transport coefficients. 
{{Available|6.5.0}}

----
This list of temperatures is used to determine the chemical potential, the occupation factors entering the electron self-energy due to electron-phonon coupling as well as the transport coefficients in the context of a transport calculation.

A range of temperatures can be defined using {{TAG|ELPH_SELFEN_TEMPS_RANGE|l u n}}, where:
* *l* is the lower limit of the temperature range.
* *u* is the upper limit of the temperature range.
* *n* is the number of steps between the two limits.

For example, {{TAG|ELPH_SELFEN_TEMPS_RANGE|0 700 41}} would create a list of <b>41</b> points from 0 K to 700 K. This is printed in the {{FILE|OUTCAR}} file:

 elph_selfen_temps=
       0.000
      17.500
      35.000
   ...
     665.000
     682.500
     700.000

At each temperature an electron-phonon calculation is performed, rather than defining it manually using {{TAG|ELPH_SELFEN_TEMPS}}.
## Related tags and articles
* Transport calculations
* Electron-phonon accumulators
* Chemical potential in electron-phonon interactions
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_SELFEN_MU}}
* {{TAG|ELPH_SELFEN_MU_RANGE}}
* {{TAG|ELPH_SELFEN_CARRIER_DEN}}
* {{TAG|ELPH_SELFEN_CARRIER_DEN_RANGE}}
* {{TAG|ELPH_SELFEN_CARRIER_PER_CELL}}
* {{TAG|ELPH_SELFEN_TEMPS}}
* {{TAG|NELECT}}

Category:INCAR tagCategory:Electron-phonon_interactions
