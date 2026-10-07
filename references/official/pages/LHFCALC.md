{{TAGDEF|LHFCALC|.TRUE. {{!}} .FALSE. |.FALSE.}}

Description: {{TAG|LHFCALC}} specifies whether a Hartree-Fock/DFT hybrid functional type calculation is performed.
----
If one does not specifically request a particular hybrid functional (see {{TAG|AEXX}}, {{TAG|ALDAX}}, {{TAG|ALDAC}}, {{TAG|AGGAX}}, {{TAG|AGGAC}}, {{TAG|AMGGAX}}, {{TAG|AMGGAC}}, and the list_of_hybrid_functionals) VASP will default to the PBE0 hybrid functional.
{{NB|tip|For the most reliable convergence, select a "direct optimization" algorithm for HF/DFT hybrid functonal type calculations, i.e., {{TAG|ALGO|Damped}} ({{TAG|IALGO|53}}) or {{TAG|ALGO|All}} ({{TAG|IALGO|58}}) in the {{FILE|INCAR}} file. You may also consider {{TAG|ALGO|Normal}} which in combination with {{TAG|LFOCKACE|TRUE}} (the default) can be a fast alternative. Do not use {{TAG|ALGO|Fast}} which is not properly supported (note: no warning is printed).}}

If the blocked-Davidson algorithm {{TAG|ALGO|Normal}} is used, in many cases the Pulay mixer will be unable to determine the proper ground-state. We hence recommend to select the blocked-Davidson algorithm only in combination with straight mixing or a Kerker-like mixing (see the section on mixing). The following combination have been successfully applied for small and medium-sized systems

 {{TAG|LHFCALC}} = .TRUE. ; {{TAG|ALGO}} = Normal ; {{TAG|IMIX}} = 1 ; {{TAG|AMIX}} = a

Decrease the parameter a until convergence is reached.

In most cases, however, it is recommended to use the "Damped" algorithm with a suitably chosen timestep. The following setup for the electronic optimization works reliably in most cases:

 {{TAG|LHFCALC}} = .TRUE. ; {{TAG|ALGO}} = Damped ; {{TAG|TIME}} = 0.5

If convergence is not obtained, it is recommended to reduce the timestep {{TAG|TIME}}.
{{NB|mind|The stress tensor is not calculated by default for {{TAG|LHFCALC|.TRUE.}} (i.e., {{TAG|ISIF|0}}) as it is expensive for hybrid functionals. It can be turned on by setting {{TAG|ISIF|2}}.}}
## Related tags and articles
{{TAG|AEXX}},
{{TAG|ALDAX}},
{{TAG|ALDAC}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|AMGGAX}},
{{TAG|AMGGAC}},
{{TAG|HFSCREEN}},
{{TAG|LTHOMAS}},
{{TAG|LRHFCALC}},
{{TAG|LFOCKACE}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|LHFCALC|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
