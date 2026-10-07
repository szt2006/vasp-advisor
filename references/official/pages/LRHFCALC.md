{{TAGDEF|LRHFCALC|.TRUE. {{!}} .FALSE. |.FALSE.}}

Description: Switch on the decomposition of the exchange for the hybrid functionals using full Hartree-Fock exchange at long range.
----
If {{TAG|LRHFCALC}}=.TRUE. the exchange functional is decomposed into short-range LDA, PBE or PBEsol ({{TAG|GGA}}{{=}}CA, PE, PS, respectively) and long-range Hartree-Fock:

:E_{\mathrm{xc}}^{\mathrm{hybrid}}=a_{\mathrm{LR}} E_{\mathrm{x,LR}}^{\mathrm{HF}}(\mu) + E_{\mathrm{x,SR}}^{\mathrm{SL}}(\mu) + (1-a_{\mathrm{LR}})E_{\mathrm{x,LR}}^{\mathrm{SL}}(\mu) + E_{\mathrm{c}}^{\mathrm{SL}}

The mixing a_{\mathrm{LR}} and screening \mu are controlled by the {{TAG|AEXX}} and {{TAG|HFSCREEN}} tags, respectively. The RSHXLDA or RSHXPBE functionals{{cite|iikura:jcp:2001}}{{cite|gerber:cpl:2005}}{{cite|gerber:jcp:2007}} are examples of such functionals and
their settings are shown on the page listing the hybrid functionals.
{{NB|mind|
*If {{TAG|LRHFCALC}}{{=}}.TRUE., then {{TAG|LHFCALC}}{{=}}.TRUE. is automatically set.
*If {{TAG|LRHFCALC}}{{=}}.TRUE., then {{TAG|AEXX}}{{=}}1 is automatically set, but {{TAG|AEXX}} can be set to another value.}}
{{NB|important|When {{TAG|AEXX}}{{=}}1 (the default for {{TAG|LRHFCALC}}{{=}}.TRUE.), the correlation E_{\mathrm{c}}^{\mathrm{SL}} is not included. However, it can be included by setting {{TAG|ALDAC}}{{=}}1.0 and {{TAG|AGGAC}}{{=}}1.0.}}
## Related tags and articles
{{TAG|LHFCALC}},
{{TAG|HFSCREEN}},
{{TAG|AEXX}},
{{TAG|LMODELHF}},
{{TAG|LTHOMAS}},
list of hybrid functionals,
Hybrid functionals: formalism

{{sc|LRHFCALC|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
