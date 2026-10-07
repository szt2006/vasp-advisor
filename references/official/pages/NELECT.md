{{TAGDEF|NELECT|[real]|number of valence electrons}}

Description: {{TAG|NELECT}} sets the number of electrons.
----
{{NB| warning | Unless you would like to perform a charged calculation, you should not set this line.}}
The number of electrons is determined automatically from the {{FILE|POTCAR}} (ZVAL of the element) and {{FILE|POSCAR}} file (number of the atoms of the respective atom type) assuming the cell is charge-neutral.
If the number of electrons is not compatible with the number derived from the valence and the number of atoms a homogeneous background charge is assumed.
If the number of ions specified in the {{FILE|POSCAR}} file is 0 and {{TAG|NELECT}}=n, then the energy of a homogeneous electron gas is calculated.
## Charged calculations
{{NB| warning | Using the {{TAG|NELECT}} tag without the use of an appropriate correction leads to a very slow convergence of energies with respect to the size *L* of the supercell. }}

The required first-order correction to the energy caused by an excess charge is given by
::\frac{e^2q^2\alpha}{L\epsilon}
where *q* is the net charge of the system, &alpha;
the Madelung constant of a point charge *q* placed in a homogeneous background charge *-q*, and &epsilon; 
the dielectric constant of the system.
For atoms or molecules surrounded by vacuum, &epsilon; takes on the vacuum value &epsilon;=1.
VASP can automatically correct this leading error, see {{TAG|Electrostatic corrections}} for further information.

It is important to emphasize that the total energy cannot be corrected for charged slabs, since a charged slab results in an electrostatic potential that grows with the distance from the slab.
This non-convergence of the potential is a result of the interaction between the charged slab and the compensating background.
A practical consequence of this non-convergence is that the total energy depends linearly on the width of the vacuum.
{{NB|warning| Presently, no simple *a posteriori* correction scheme is implemented in VASP for slab calculations. Total energies from charged slab calculations must be used with care. In certain cases, relative energies between two charged surface calculations may be useful''}}
## Related tags and articles
{{TAG|Monopole Dipole and Quadrupole corrections}},
{{TAG|EPSILON}},
{{TAG|DIPOL}},
{{TAG|IDIPOL}},
{{TAG|LMONO}},
{{TAG|LDIPOL}},
{{TAG|EFIELD}}

{{sc|NELECT|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Electronic occupancyCategory:Electrostatics
