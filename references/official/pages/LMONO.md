{{TAGDEF|LMONO|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LMONO}} switches on monopole-monopole corrections for the total energy.
----
The flag switches on monopole corrections for charged systems, and monopole corrections only. The correction is calculated only a posteriori for the total energy.  Corrections related to dipole-dipole interactions or to the potential are not calculated.
{{NB|tip|  If corrections related to dipoles are desired, use {{TAG|IDIPOL}} instead. Furthermore, for the potential corrections, please also set {{TAG|LDIPOL}}. When using {{TAG|IDIPOL}}, VASP determines whether the system is charged and activates the monopole corrections automatically. Do not set {{TAG|LMONO}}, if dipole corrections are required.}}

The primary use of this flag is for defect calculations in charged supercells, or whenever the dipole corrections cannot be reliably determined. Specifically, for supercells using periodic boundary conditions,  it is often not possible to determine the dipole at the defect site accurately,
whereas for 0D systems (i.e. atoms and molecules) and sufficiently large supercells, the dipole can usually be determined accurately.
## Related tags and articles
{{TAG|Monopole Dipole and Quadrupole corrections}},
{{TAG|NELECT}},
{{TAG|EPSILON}},
{{TAG|IDIPOL}},
{{TAG|DIPOL}},
{{TAG|LDIPOL}},
{{TAG|EFIELD}}

{{sc|LMONO|Examples|Examples that use this tag}}

----

Category:INCAR tagCategory:MoleculesCategory:Electrostatics
