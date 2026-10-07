{{TAGDEF|ALDAC|[real]}}
{{DEF|ALDAC|1.0 | if {{TAG|LHFCALC}}=.FALSE. or {{TAG|AEXX}}\neq1.0 | 0.0 | if {{TAG|LHFCALC}}=.TRUE. and {{TAG|AEXX}}=1.0}}

Description: {{TAG|ALDAC}} is a parameter that multiplies the LDA correlation functional or the LDA part of the GGA correlation functional. 
----
{{TAG|ALDAC}} can be used as the fraction of LDA correlation in a Hartree-Fock/DFT hybrid functional. 
{{NB|mind|
*{{TAG|ALDAC}} is implemented for all functionals listed at {{TAG|GGA}} except AM05.
*{{TAG|ALDAC}} is implemented for the functionals from Libxc (see {{TAG|LIBXC1}} for details).
}}
## Related tags and articles
{{TAG|AEXX}},
{{TAG|ALDAX}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
{{TAG|LHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|ALDAC|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
