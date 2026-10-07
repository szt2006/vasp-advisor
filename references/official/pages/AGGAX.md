{{TAGDEF|AGGAX|[real]}}
{{DEF|AGGAX|1.0-{{TAG|AEXX}} | if {{TAG|LHFCALC}}{{=}}.TRUE. | 1.0 | if {{TAG|LHFCALC}}{{=}}.FALSE.}}

Description: {{TAG|AGGAX}} is a parameter that multiplies the gradient correction in the GGA exchange functional.
----
{{TAG|AGGAX}} can be used as the fraction of gradient correction in the GGA exchange in a Hartree-Fock/GGA hybrid functional.
{{NB|important|{{TAG|AGGAX}} can be used only if {{TAG|LHFCALC}}{{=}}.TRUE.}}
{{NB|mind|
*{{TAG|AGGAX}} is implemented for all functionals listed at {{TAG|GGA}} except AM05.
*{{TAG|AGGAX}} is implemented for the functionals from Libxc (see {{TAG|LIBXC1}} for details).
}}
## Related tags and articles
{{TAG|AEXX}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
{{TAG|LHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|AGGAX|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
