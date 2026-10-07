{{DISPLAYTITLE:LFINITE_TEMPERATURE}}
{{TAGDEF|LFINITE_TEMPERATURE|[logical]|.FALSE.}}

Description: {{TAG|LFINITE_TEMPERATURE}} switches on the finite-temperature formalism of many-body perturbation theory for adiabatic-connection-fluctuation-dissipation-theorem (ACFDT)/GW calculations.
----
This feature is available as of VASP.6.1.0 for ACFDT/random-phase-approximation (RPA), i.e., {{TAG|ALGO}}=ACFDT, ACFDTR, ACFDTRK, and low-scaling GW calculations, i.e., {{TAG|ALGO}}=EVGW0R, GWR[K]. 

For {{TAG|LFINITE_TEMPERATURE}}=.TRUE., a compressed Matsubara-frequency grid is used (instead of the zero-temperature formalism of many-body perturbation theory). This allows for GW and RPA calculations for metallic systems. {{cite|Kaltak:PRB:2020}} 
To this end, the electronic temperature is set with the k-point smearing parameter {{TAG|SIGMA}} in units of eV, e.g. a value of \sigma=1 eV corresponds to a electronic temperature of T\approx 11 604 K.
{{NB|warning|Can only be used in combination with Fermi smearing {{TAG|ISMEAR}} {{=}} -1.}} 
## Related tags and articles
{{TAG|NOMEGA}},
{{TAG|NOMEGAPAR}}, 
{{TAG|NTAUPAR}},
{{TAG|ISMEAR}}
----

Category:INCAR tagCategory:Many-body perturbation theoryCategory:GW Category:ACFDTCategory:Low-scaling GW and RPA
