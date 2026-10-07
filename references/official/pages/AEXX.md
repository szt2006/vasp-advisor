{{TAGDEF|AEXX|[real]}}
{{DEF|AEXX|0.25|if {{TAG|LHFCALC}}{{=}}.TRUE. .AND. {{TAG|LRHFCALC}}{{=}}.FALSE.|1|if {{TAG|LRHFCALC}}{{=}}.TRUE.|0|if {{TAG|LHFCALC}}{{=}}.FALSE.}}

Description: {{TAG|AEXX}} specifies the fraction of exact exchange in a Hartree-Fock-type/hybrid-functional calculation.
----
{{NB|mind|
*For versions of VASP prior to 6.4.0, {{TAG|ALDAX}} was constrained to be equal to 1.0-{{TAG|AEXX}}. This constraint is lifted since VASP.6.4.0.
*For {{TAG|AEXX}}{{=}}1.0, VASP switches off correlation by default ({{TAG|ALDAC}}{{=}}0.0, {{TAG|AGGAC}}{{=}}0.0, and {{TAG|AMGGAC}}{{=}}0.0) and thus runs a full Hartree-Fock calculation.}}
## Related tags and articles
{{TAG|BEXX}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
{{TAG|LHFCALC}},
{{TAG|HFSCREEN}},
{{TAG|LMODELHF}},
{{TAG|LTHOMAS}},
{{TAG|LRHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|AEXX|Examples|Examples that use this tag}}
## References
----
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
