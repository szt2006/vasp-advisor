{{DISPLAYTITLE:ML_SIGV0}}
{{TAGDEF|ML_SIGV0|[real]|1.0}}

Description: This flag sets the noise parameter s_{\mathrm{v}} (see here for definition) for the fitting in the machine learning force field method.
----
If the regularization needs to be controlled manually, like e.g. in the fitting via singular value decomposition ({{TAG|ML_MODE}}=*REFIT* or {{TAG|ML_IALGO_LINREG}}=4), the best is to keep this parameter constant at 1 and control the regularization via the precision parameter s_{\mathrm{w}} (see {{TAG|ML_SIGW0}}).

For the theory of this regularization parameter see this section.
## Related tags and sections
{{TAG|ML_LMLFF}}, {{TAG|ML_IREG}}, {{TAG|ML_SIGW0}}, {{TAG|ML_IALGO_LINREG}}

{{sc|ML_SIGV0|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
