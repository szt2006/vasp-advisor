{{TAGDEF|ALDAX|[real]}}
{{DEF|ALDAX|1.0-{{TAG|AEXX}} | if {{TAG|LHFCALC}}{{=}}.TRUE. | 1.0 | if {{TAG|LHFCALC}}{{=}}.FALSE.}}

Description: {{TAG|ALDAX}} is a parameter that multiplies the LDA exchange functional or the LDA part of the GGA exchange functional.
----
{{TAG|ALDAX}} can be used as the fraction of LDA exchange in a Hartree-Fock/DFT hybrid functional.
{{NB|important|{{TAG|ALDAX}} can be used only if {{TAG|LHFCALC}}{{=}}.TRUE.}}
{{NB|mind|
*For versions of VASP prior to 6.4.0, {{TAG|ALDAX}} was constrained to be equal to 1.0-{{TAG|AEXX}}. This constraint is lifted since VASP.6.4.0.
*{{TAG|ALDAX}} is implemented for all functionals listed at {{TAG|GGA}} except AM05.
*{{TAG|ALDAX}} is implemented for the functionals from Libxc (see {{TAG|LIBXC1}} for details).
}}
## Related tags and articles
{{TAG|AEXX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
{{TAG|LHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|ALDAX|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
