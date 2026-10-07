{{TAGDEF|EDIFF|[real]|10^{-4}}}

Description: {{TAG|EDIFF}} specifies the global break condition for the electronic SC-loop. {{TAG|EDIFF}} is specified in units of eV.
----
The relaxation of the electronic degrees of freedom stops if the total (free) energy change and the band-structure-energy change ('change of eigenvalues') between two steps are both smaller than {{TAG|EDIFF}} (in eV). For {{TAG|EDIFF}}=0, strictly {{TAG|NELM}} electronic self-consistency steps will be performed.

In most cases, the convergence speed is quadratic, so often the cost for the additional iterations is small. Hence, for well converged calculations, we strongly recommend to decrease {{TAG|EDIFF}} to 1E-6. For finite difference calculations (e.g. phonons), even {{TAG|EDIFF}} {{=}} 1E-7 might be required in order to obtain precise results. On the other hand, for large systems with many atoms and/or when using {{TAG|METAGGA}} functionals, attaining an energy convergence of 1E-8 or even 1E-7 might be difficult. So, overall {{TAG|EDIFF}}= 1E-6 is likely the best compromise.
{{NB|tip|You can get information at each electronic step using {{TAG|NWRITE|2,3}}.}}
## Related tags and articles
{{TAG|EDIFFG}}, {{TAG|NWRITE}}

{{sc|EDIFF|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:Electronic minimization
