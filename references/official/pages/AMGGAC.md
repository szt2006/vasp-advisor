{{TAGDEF|AMGGAC|[real]}}
{{DEF|AMGGAC|1.0 | if {{TAG|LHFCALC}}=.FALSE. or {{TAG|AEXX}}\neq1.0 | 0.0 | if {{TAG|LHFCALC}}=.TRUE. and {{TAG|AEXX}}=1.0}}

Description: {{TAG|AMGGAC}} is a parameter that multiplies the meta-GGA correlation functional (available as of VASP.6.4.0).
----
{{TAG|AMGGAC}} can be used as the fraction of  meta-GGA correlation in a Hartree-Fock/DFT hybrid functional. 
{{NB|mind|Note the difference with respect to {{TAG|AGGAC}}: {{TAG|AMGGAC}} multiplies the whole meta-GGA correlation functional, while {{TAG|AGGAC}} multiplies only the gradient-correction term of a GGA correlation functional.}}
## Related tags and articles
{{TAG|AEXX}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|LHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|AMGGAC|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
