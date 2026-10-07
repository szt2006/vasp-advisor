{{TAGDEF|TITEL|[string]}}

Definition: The {{TAG|TITEL}} tag specifies the title of a specific {{FILE|POTCAR}} file. It is also the first line of any {{FILE|POTCAR}} file. It is not possible nor necessary to set this tag in the {{FILE|INCAR}} file.
-----
The {{FILE|POTCAR}} tag {{TAG|TITEL}} is a string composed of:
* the type of pseudopotential (either PAW for the projector-augmented-wave formalism or US for ultrasoft pseudopotentials,
* information about the exchange-correlation functional (GGA for PW91, PBE for PBE, missing for LDA),
* the element symbol,
* a suffix specifying the type of potential.
* the date of the pseudopotential creation.

In very early pseudopotentials releases, not all of this information is necessarily present.
## Examples
*{{TAG|TITEL}} = PAW Ti_sv 26Sep2005 (Ti potential with the semicore <i>s</i> and <i>p</i> states added to the valence from the potpaw_LDA.64 potential set.
*{{TAG|TITEL}} = PAW_PBE Ti_sv_GW 05Dec2013 (Ti potential for GW calculations with the semicore <i>s</i> and <i>p</i> states added to the valence from the potpaw_PBE.64 potential set
*{{TAG|TITEL}} = PAW_GGA Ti_pv 07Sep2000 (Ti potential with the semicore <i>p</i> states added to the valence from the PW91 (2010) potential set.
*{{TAG|TITEL}} = US Ti (Ti potential with the semicore <i>p</i> states added to the valence from the PW91 USPP (2002) potential set. For this very old pseudopotential, no information on functional, valency, or creation date is available.
## Related tags and articles
{{FILE|POTCAR}}, pseudopotentials, available pseudopotentials

Category:Exchange-correlation functionalsCategory:POTCAR tag
## References
