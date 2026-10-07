{{TAGDEF|IPEAD|1 {{!}} 2 {{!}} 3 {{!}} 4|4}}

Description: {{TAG|IPEAD}} specifies the order of the finite difference stencil used to compute the derivative of the cell-periodic part of the orbitals w.r.t. **k**, |&nabla;**k**un**k**&rang; ({{TAG|LPEAD}}=.TRUE.), and the derivative of the polarization w.r.t. the orbitals, &delta;**P**/&delta;&lang;&psi;n**k**| for ({{TAG|LCALCEPS}}=.TRUE., or {{TAG|EFIELD_PEAD}}&ne;**0**).
----
A central finite differences formula or order {{TAG|IPEAD}} is used to compute the first-order derivative of the cell-periodic part of the orbitals w.r.t. **k**.
The coefficients for the different orders can be found here (https://en.wikipedia.org/wiki/Finite_difference_coefficient#Central_finite_difference).
## Related tags and articles
{{TAG|LPEAD}},
{{TAG|LCALCEPS}},
{{TAG|EFIELD_PEAD}},
Berry phases and finite electric fields

{{sc|IPEAD|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Linear responseCategory:Dielectric propertiesCategory:Berry phases
