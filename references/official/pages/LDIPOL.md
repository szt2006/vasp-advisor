{{TAGDEF|LDIPOL|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LDIPOL}} switches on corrections to the potential and forces. Can be applied for charged molecules and slabs or any system possessing a net dipole moment.
----

The presence of a dipole in combination with periodic boundary conditions leads to a slow convergence of the total energy with the size of the supercell.
Furthermore, finite-size errors affect the potential and the forces.
This effect can be counterbalanced by setting {{TAG|LDIPOL}}=.TRUE. in the {{FILE|INCAR}} file. 
For {{TAG|LDIPOL}}=.TRUE., a linear correction, and for charged cells, a quadratic electrostatic potential is added to the local potential in order to correct the errors introduced by the periodic boundary conditions. When activating this tag, the tag {{TAG|IDIPOL}} has to be specified, and optionally the tag {{TAG|DIPOL}} as well. 
{{NB|mind| This is in the spirit of Neugebauer *et al.* {{cite|neugebauer:prb:1992}}, though more general. Note that the total energy is correctly implemented, whereas Ref. {{cite|neugebauer:prb:1992}} contains an erroneous factor 2 in the total energy. }}

The decisive advantage of this mode is that leading errors in the forces are corrected and that the work function can be evaluated for asymmetric slabs. The disadvantage is that the convergence to the electronic ground state might slow down considerably, i.e., more electronic iterations might be required to obtain the required precision.
{{NB|important|Dipole corrections can lead to slow convergence, since charge often needs to be moved from one side of a slab to the other. The convergence rate often improves by setting AMIN to a smaller value, for instance {{TAG|AMIN}} {{=}} 0.01, since this dampens charge sloshing (charge moving back and forth from one to the other side of the slab in consecutive steps).  Sometimes, it might also be necessary to increase the number of electronic steps using {{TAG|NELM}} and to tighten the energy convergence {{TAG|EDIFF}} {{=}} 1E-6. An unconverged dipole correction can lead to erroneous forces https://vasp.at/forum/viewtopic.php?t=20300.}}
{{NB|warning| For charged systems, the potential correction is currently only implemented for cubic supercells. VASP will stop if the supercell is not cubic and {{TAG|LDIPOL}} is used.}}
## Related tags and articles
{{TAG|Monopole Dipole and Quadrupole corrections}},
{{TAG|NELECT}},
{{TAG|EPSILON}},
{{TAG|IDIPOL}},
{{TAG|DIPOL}},
{{TAG|LMONO}},
{{TAG|EFIELD}}

{{sc|LDIPOL|Examples|Examples that use this tag}}
## References
Category:INCAR tagCategory:Ionic minimizationCategory:ForcesCategory:Electrostatics
