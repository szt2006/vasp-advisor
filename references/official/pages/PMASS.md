{{TAGDEF|PMASS|[Real]|1000}}

Description: {{TAG|PMASS}} assigns a fictitious mass (in amu) to the lattice degrees-of-freedom in case of Parrinello-Rahman dynamics (in case VASP was compiled with -Dtbdyn).
----
When running *NpT* simulations with a Langevin thermostat ({{TAG|MDALGO}}=3), using the method of Parrinello and Rahman, a fictitious mass (in amu) for the lattice degrees-of-freedom has to be assigned using the {{TAG|PMASS}} tag.
The friction coefficient for lattice degrees-of-freedom have to be specified (in ps-1) by means of the {{TAG|LANGEVIN_GAMMA_L}} tag.

The friction coefficients &gamma; for the atomic degrees-of-freedom are specified using the {{TAG|LANGEVIN_GAMMA}} tag.

The optimal setting for {{TAG|PMASS}} depends very much on the particular system at hand and can be considered as a compromise between two opposing factors: too large values lead to very slow variation of lattice degrees of freedom (and hence the sampling becomes inefficient) while too small value can lead to too large geometric changes in an MD step and hence may cause numerical problems. We strongly recommend to make careful tests with various settings before performing the production run.

As demonstrated by Nosé and Klein, the harmonic frequency of oscillation of a cubic cell can be expressed as \omega_L = \sqrt{\frac{3BL}{W}}, where B, L, and W are bulk modulus, size of the unit cell, and mass of the lattice degrees-of-freedom, respectively. Should \omega_L remain the same upon (say) doubling one of the cell dimensions, the {{TAG|PMASS}} should also be doubled.  
## Related tags and articles
{{TAG|LANGEVIN_GAMMA_L}},
{{TAG|LANGEVIN_GAMMA}},
{{TAG|MDALGO}}
## References
</references>

{{sc|PMASS|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Molecular dynamics
