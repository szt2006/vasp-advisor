{{TAGDEF|LFXC|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LFXC}} enables the (semi-)local exchange-correlation kernel in Casida and time-evolution TDDFT calculations.
----
In linear-response TDDFT, the density-density response function \chi obeys the Dyson equation
::
\chi(\mathbf r, \mathbf r'; \omega) = \chi_\mathrm{KS}(\mathbf r, \mathbf r'; \omega) + \int \mathrm d\mathbf r_1 \mathrm d\mathbf r_2 \, \chi_\mathrm{KS}(\mathbf r, \mathbf r_1; \omega) \left[ v(\mathbf r_1, \mathbf r_2) + f_\mathrm{xc}(\mathbf r_1, \mathbf r_2; \omega) \right] \chi(\mathbf r_2, \mathbf r'; \omega),

where \chi_\mathrm{KS} is the non-interacting Kohn-Sham response function, v is the bare Coulomb interaction, and f_\mathrm{xc} is the exchange-correlation kernel. VASP uses the adiabatic approximation, f_\mathrm{xc}(\mathbf r, \mathbf r'; \omega) \approx f_\mathrm{xc}(\mathbf r, \mathbf r').

Setting {{TAG|LFXC}}{{=}}.TRUE. includes the (semi-)local part of f_\mathrm{xc} in both the Casida eigenvalue problem ({{TAG|ALGO}}{{=}}TDHF) and the time-evolution TDDFT (or real-time TDDFT) ({{TAG|ALGO}}{{=}}TIMEEV).
## (Semi-)local exchange-correlation kernel
The exchange-correlation kernel is computed very differently in the Casida and time-evolution TDDFT approaches. It is defined as the second functional derivative of the exchange-correlation energy density with respect to the charge density,
::
f_\mathrm{xc}(\mathbf r, \mathbf r') = \frac{\partial^2 \varepsilon_\mathrm{xc}}{\partial n(\mathbf r) \, \partial n(\mathbf r')}\delta(\mathbf r - \mathbf r').

The Casida approach requires the derivative to be evaluated explicitly and therefore implemented for each functional. The time-evolution TDDFT does not require an explicit kernel: its contribution is included implicitly through the propagation of the charge density and the exchange-correlation potential.
### Casida TDDFT
For an LDA functional,
::
f_\mathrm{xc}^\mathrm{LDA}(\mathbf r, \mathbf r') = \frac{\partial^2 \varepsilon_\mathrm{xc}}{\partial n^2} \, \delta(\mathbf r - \mathbf r').

For a GGA functional, gradient terms appear,
::
f_\mathrm{xc}^\mathrm{GGA}(\mathbf r, \mathbf r') = \frac{\partial^2 \varepsilon_\mathrm{xc}}{\partial n^2}(\mathbf r) \, \delta(\mathbf r - \mathbf r') - \left[\nabla \frac{\partial^2 \varepsilon_\mathrm{xc}}{\partial n \, \partial \nabla n}(\mathbf r)\right] \delta(\mathbf r - \mathbf r') - \nabla_i \frac{\partial^2 \varepsilon_\mathrm{xc}}{\partial \nabla_i n \, \partial \nabla_j n}(\mathbf r) \, \nabla_j \delta(\mathbf r - \mathbf r'),

where i, j are summed Cartesian indices. In the Casida approach these gradient terms are dropped and only the density derivatives are kept. Meta-GGA kernels are not supported.
### Time-evolution TDDFT (Real-time TDDFT)
The real-time propagation applies f_\mathrm{xc} directly to the time-dependent density, so LDA and GGA kernels are used in full, including the gradient terms.

For meta-GGA functionals, the dependence of \varepsilon_\mathrm{xc} on the kinetic-energy density \tau(\mathbf r) makes \delta v_\mathrm{xc}/\delta n non-local through the orbital dependence of \tau{{cite|nazarov:vignale:2011}}. These non-local contributions are not implemented in VASP, so the 1/q^2 long-range component of f_\mathrm{xc} responsible for excitonic effects is missing.
## Hybrid functionals
For a hybrid functional, a fraction c_\mathrm{x} of the (semi-)local exchange is replaced by exact (Fock) exchange in both solvers{{cite|sander:prb:15}},
::
f_\mathrm{xc}(\mathbf r, \mathbf r') = \left(1-c_\mathrm{x}\right) \frac{\partial^2 \varepsilon_\mathrm{x}}{\partial n(\mathbf r) \, \partial n(\mathbf r')} + \frac{\partial^2 \varepsilon_\mathrm{c}}{\partial n(\mathbf r) \, \partial n(\mathbf r')} + c_\mathrm{x} \frac{\partial^2 \varepsilon_\mathrm{x}^\mathrm{Exact}}{\partial^2 n(\mathbf r, \mathbf r')},

where c_\mathrm{x} is set by {{TAG|AEXX}} and n(\mathbf r, \mathbf r') is the one-particle density matrix. {{TAG|LFXC}}{{=}}.TRUE. enables the first two terms only; the Fock contribution is enabled separately by {{TAG|LADDER}}{{=}}.TRUE..
## Compare Casida and time-evolution TDDFT results
The Casida and time-evolution approaches produce very similar results for LDA exchange-correlation. Small differences typically remain because one-center terms in the PAW method are treated differently in the two approaches. To bring the Casida results into closer agreement, increase {{TAG|ENCUTGW}} beyond its default value and set {{TAG|ANTIRES}}=2 in the Casida TDDFT calculation.
## Related tags and articles
;Tags
:{{TAG|LADDER}}, {{TAG|LHARTREE}}, {{TAG|AEXX}}, {{TAG|ENCUTGW}}
;Articles
:Time-dependent density-functional theory calculations, Time-evolution algorithm

{{sc|LFXC|Howto|Workflows that use this tag}}
## References
Category:INCAR tag
Category:Many-body perturbation theory
Category:Bethe-Salpeter equations
