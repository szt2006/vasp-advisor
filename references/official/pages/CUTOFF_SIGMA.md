{{DISPLAYTITLE:CUTOFF_SIGMA}}
{{TAGDEF|CUTOFF_SIGMA| [real] ( [real] )}}
{{DEF|CUTOFF_SIGMA|0.1|}}

Description: {{TAG|CUTOFF_SIGMA}} specifies the broadening \sigma in eV for the cutoff function specified by {{TAG|CUTOFF_TYPE}}.
 
----

Corresponds to a broadening of the cutoff function used in the  one-shot method to obtain Wannier functions.
The meaning of \sigma depends on the {{TAG|CUTOFF_TYPE}} tag.

For spin-polarized calculations ({{TAG|ISPIN|2}}), two values can be specified for {{TAG|CUTOFF_SIGMA}}, one for each spin channel.
If only a single value is specified, it will be used for both spin channels.
## Related tags and articles
{{TAG|CUTOFF_TYPE}},
{{TAG|CUTOFF_MU}},
{{TAG|LSCDM}},
{{TAG|LOCPROJ}}

{{sc|CUTOFF_SIGMA|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Wannier functions
