{{DISPLAYTITLE:LANGEVIN_GAMMA_L}}{{TAGDEF|LANGEVIN_GAMMA_L|[Real]|0}}

Description: {{TAG|LANGEVIN_GAMMA_L}} specifies the friction coefficient (in ps-1) for lattice degrees-of-freedom in case of Parrinello-Rahman dynamics (in case VASP was compiled with -Dtbdyn).
----
When running *NpT* simulations with a Langevin thermostat{{Cite|allen:book:1991}} ({{TAG|MDALGO}}=3), using the method of Parrinello and Rahman{{Cite|parrinello:prl:1980}}{{Cite|parrinello:jap:1981}}, the friction coefficient for lattice degrees-of-freedom have to be specified (in ps-1) by means of the {{TAG|LANGEVIN_GAMMA_L}}-tag.
A fictitious mass for the lattice degrees-of-freedom has to be assigned using the {{TAG|PMASS}} tag.

The friction coefficients &gamma; for the atomic degrees-of-freedom are specified using the {{TAG|LANGEVIN_GAMMA}}-tag.
## Related tags and articles
{{TAG|LANGEVIN_GAMMA}},
{{TAG|PMASS}},
{{TAG|MDALGO}}

{{sc|LANGEVIN_GAMMA_L|Examples|Examples that use this tag}}
## References
----

Category:INCAR tagCategory:Molecular dynamicsCategory:Thermostats
