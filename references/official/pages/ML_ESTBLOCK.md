{{DISPLAYTITLE:ML_ESTBLOCK}}
{{TAGDEF|ML_ESTBLOCK|[integer]|{{TAG|ML_OUTBLOCK}}}}

Description: Calculation and output frequency of error estimates for {{TAG|ML_MODE}}=*RUN* computations.
----
{{NB|warning|This tag was previously called ML_IERR in VASP versions 6.5.0 and earlier. Since VASP 6.5.1, {{TAG|ML_ESTBLOCK}} is the official variant (although ML_IERR is still supported for compatibility reasons).}}
This tag sets the interval in units of molecular-dynamics steps at which the error estimates are written to the {{TAG|ML_LOGFILE}}. The error estimate is computed by utilizing the spilling factor if a refit with {{TAG|ML_MODE}}=*REFIT* was done. The spilling factor is calculated for each atom in the current structure and the maximum among all atoms is written to the {{TAG|ML_LOGFILE}} file marked with SFF. 

The spilling factor measures the similarity of the local environment of each atom in the current structure to that of the local reference configurations of the force field. The values of the spilling factor are in the range [0,1]. If the atomic environment is "properly" represented by the local reference configurations the spilling factor approaches 0. Vice versa the spilling factor quickly approaches 1, if the force field is extrapolating.

The calculation of the spilling factor scales quadratically with the number of local reference configurations and linearly with the number of species. For force fields containing many species and/or local reference configurations, the evaluation time of the spilling factor becomes of the order of the evaluation of a single force field step or more. Since it is sufficient to monitor the error every  {{TAG|ML_ESTBLOCK}} MD steps, the total time consumed by the evaluation of the spilling factor can become insignificantly compared to the total time. 

In long molecular dynamics calculations, we recommend to use at least {{TAG|ML_ESTBLOCK}}=20-100.

{{TAG|ML_ESTBLOCK}}=0 turns off the calculation of the spilling factor.

{{TAG|ML_ESTBLOCK}} can be freely chosen only if {{TAG|ML_MODE}}=*RUN*. In any other calculation mode, if {{TAG|ML_ESTBLOCK}} is not equal to 1, the code will exit with an error and provide an error description.

For calculations using force fields obtained by {{TAG|ML_MODE}}=*REFITBAYESIAN* or without any refitting, the Bayesian error estimates of energy, forces and stress (BEFF) are additionally written out to the {{TAG|ML_LOGFILE}} file and their output frequency is also controlled by {{TAG|ML_ESTBLOCK}}. Albeit having the advantage of an additional error estimate we still do not recommend using these force fields, since they are significantly slower than force fields obtained by {{TAG|ML_MODE}}=*REFIT*.
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_MODE}}, {{TAG|ML_LFAST}}, {{TAG|ML_OUTBLOCK}}, {{TAG|ML_OUTPUT_MODE}}, {{TAG|ML_CALGO}}
----
Category:INCAR tagCategory:Machine-learned force fields
