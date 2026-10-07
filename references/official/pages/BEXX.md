{{TAGDEF|BEXX|[real]}}
{{DEF|BEXX|1|if {{TAG|LHFCALC}}{{=}}.TRUE.}}

Description: {{TAG|BEXX}} specifies the fraction of short-range exact exchange in range-separated hybrid-functionals constructed with {{TAG|LMODELHF}}=.TRUE.
{{Available|6.6.0}}
{{NB|important|Until VASP.6.5.1, the fraction of short-range exact exchange (when {{TAG|LMODELHF}}{{=}}.TRUE.) was fixed to 1 and could not be changed.}}
----
The {{TAG|BEXX}} tag specifies the fraction of short-range exact exchange in range-separated hybrid-functionals. This tag can be used only when {{TAG|LMODELHF}}=.TRUE. More details can be found in the description of this class of hybrid functionals.
## Related tags and articles
{{TAG|AEXX}},
{{TAG|LMODELHF}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
{{TAG|LHFCALC}},
{{TAG|HFSCREEN}},
{{TAG|LRHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|BEXX|Examples|Examples that use this tag}}

----
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
