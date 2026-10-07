{{TAGDEF|AGGAC|[real]}}
{{DEF|AGGAC|1.0 | if {{TAG|LHFCALC}}=.FALSE. or {{TAG|AEXX}}\neq1.0 | 0.0 | if {{TAG|LHFCALC}}=.TRUE. and {{TAG|AEXX}}=1.0}}

Description: {{TAG|AGGAC}} is a parameter that multiplies the gradient correction in the GGA correlation functional.
----
{{TAG|AGGAC}} can be used as the fraction of gradient correction in the GGA correlation in a Hartree-Fock/DFT hybrid functional. 
{{NB|mind|
*{{TAG|AGGAC}} is implemented for all functionals listed at {{TAG|GGA}} except AM05.
*{{TAG|AGGAC}} is implemented for the functionals from Libxc (see {{TAG|LIBXC1}} for details).
}}
## Related tags and articles
{{TAG|AEXX}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
{{TAG|LHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|AGGAC|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
