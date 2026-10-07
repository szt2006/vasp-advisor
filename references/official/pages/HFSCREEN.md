{{TAGDEF|HFSCREEN|[real]|0 (none)}}

Description: {{TAG|HFSCREEN}} (in &Aring;-1) specifies the range-separation parameter in range-separated hybrid functionals.
----
If {{TAG|LHFCALC}}=.TRUE. and {{TAG|GGA}}=PE (PBE functional), attributing a value to {{TAG|HFSCREEN}} will switch from the PBE0 functional to, e.g., the closely related HSE03 ({{TAG|HFSCREEN}}=0.3) or HSE06 ({{TAG|HFSCREEN}}=0.2) functionals. It also needs to be set for dielectric-dependent hybrid functionals (DDH) and doubly screened hybrid (DSH) functionals, see {{TAG|LMODELHF}}.
{{NB|mind|{{TAG|HFSCREEN}} can be used only when {{TAG|GGA}}{{=}}PE, PS or CA. The other {{TAG|GGA}} and {{TAG|METAGGA}} functionals have no screened version available in VASP.}}
## Related tags and articles
{{TAG|LMODELHF}},
{{TAG|AEXX}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|LTHOMAS}},
{{TAG|LRHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|HFSCREEN|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
