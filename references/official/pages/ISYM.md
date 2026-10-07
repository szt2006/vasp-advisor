{{TAGDEF|ISYM|-1 {{!}} 0 {{!}} 1 {{!}} 2 {{!}} 3}}
{{DEF|ISYM|1|if VASP runs with USPPs|3|if {{TAG|LHFCALC}}{{=}}.TRUE.|2| else}}

Description: {{TAG|ISYM}} determines the way VASP treats symmetry.
----
{{TAG|ISYM}}=1 {{!}} 2 {{!}} 3, switches on the use of symmetry.
For {{TAG|ISYM}}=-1 {{!}} 0, the use of symmetry is switched off.

For {{TAG|ISYM}}=2 a more efficient, memory conserving symmetrization of the charge density is used (than for {{TAG|ISYM}}=1). This reduces memory requirements in particular for the parallel version.

For {{TAG|ISYM}}=3, VASP does not directly symmetrize the charge density. Instead, the charge density is constructed by applying the relevant symmetry operations to the orbitals at the **k**-points in the irreducible part of the Brillouin zone. This method of symmetrization is used when {{TAG|LHFCALC}}=.TRUE.

For {{TAG|ISYM}}=0, VASP does not use symmetry, but it will assume that &Psi;**k**=&Psi;***-k** and reduces the sampling of the Brillouin zone accordingly. This value should be set for molecular dynamics, i.e. {{TAG|IBRION}}=0. 

For {{TAG|ISYM}}=-1 the use of symmetry is switched off completely.
 
When the use of symmetry is switched on, VASP determines the point group symmetry and the space group consistent with the structure and initial velocities found on the {{FILE|POSCAR}} file (this is written out to the {{TAG|OUTCAR}} file for each {{TAG|NWRITE}} option), and the initial magnetic moments specified through the {{TAG|MAGMOM}} tag in the {{TAG|INCAR}} file. The {{TAG|SYMPREC}}-tag (VASP.4.4.4 and newer versions) determines by how much atomic positions may differ and still be judged to be equivalent by the symmetry detection algorithms. The default is 10-5, which is usually sufficiently large even if the {{FILE|POSCAR}} file has been generated with a single precision program. Increasing the {{TAG|SYMPREC}} tag means, that the positions in the {{FILE|POSCAR}} file can be less accurate. During the symmetry analysis, VASP determines

*the Bravais lattice type of the supercell,
*the point group symmetry and the space group of the supercell with basis (static and dynamic) - and prints the names of the group (space group: only 'family'),
*the type of the generating elementary (primitive) cell if the supercell is a non-primitive cell,
*all 'trivial non-trivial' translations (= trivial translations of the generating elementary cell within the supercell) -- needed for symmetrization of the charge,
*the symmetry-irreducible set of k-points if automatic k-mesh generation was used and additionally the symmetry-irreducible set of tetrahedra if the tetrahedron method was chosen together with the automatic k-mesh generation and of course also the corresponding weights ('symmetry degeneracy'),
*and tables marking and connecting symmetry equivalent ions.

The symmetry analysis is done in four steps:
*First the point group symmetry of the lattice (as supplied by the user) is determined.
*Then tests are performed, on whether the basis breaks the symmetry. Accordingly, these symmetry operations are removed.
*The initial velocities are checked for symmetry breaking.
*Finally, it is checked whether {{TAG|MAGMOM}} breaks the symmetry. Correspondingly the magnetic symmetry group is determined.

The program symmetrizes automatically:

*The total charge density according to the determined space group
*The forces on the ions according to the determined space group.
*The stress tensor according to the determined space group

Why is symmetrization necessary: Within LDA the symmetry of the supercell and the charge density is always the same. This symmetry is broken because a symmetry-irreducible set of **k** points is used for the calculation. To restore the correct charge density and the correct forces it is necessary to symmetrize these quantities.

It must be stressed that VASP does not determine the symmetry elements of the primitive cell. If the supercell has a lower symmetry than the primitive cell only the lower symmetry of the supercell is used in the calculation. In this case, one should not expect that forces that should be zero according to symmetry will be precisely zero in actual calculations. The symmetry of the primitive cell is in fact broken in several places in VASP:

*Local potential:
:In reciprocal space, the potential *V*(**G**) should be zero, if **G** is not a reciprocal lattice vector of the primitive cell. For {{TAG|PREC}}=Medium, this is not guaranteed due to "aliasing" or wrap around and the charge density (and therefore the Hartree potential) might violate this point. But even for {{TAG|PREC}}=High, small errors are introduced, because the exchange-correlation potential is calculated in real space.

***k**-points:
:In most cases, the automatic **k**-point grid does not have the symmetry of the primitive cell.

{{NB|tip|If symmetry is switched on then {{TAG|NWRITE}}{{=}}3 writes out the symmetry operations to the {{TAG|OUTCAR}} file.}}
## Related tags and articles
{{TAG|OUTCAR}}, {{TAG|IALGO}}, {{TAG|IBRION}}, {{TAG|MDALGO}}, {{TAG|ISIF}}, {{TAG|NWRITE}}

{{sc|ISYM|Examples|Examples that use this tag}}

Category:INCAR tagCategory:SymmetryCategory:Memory
