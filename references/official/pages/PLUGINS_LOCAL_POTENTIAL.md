{{DISPLAYTITLE:PLUGINS/LOCAL_POTENTIAL}}
{{TAGDEF|PLUGINS/LOCAL_POTENTIAL| .True. {{!}} .False.|.False.}}

Description: {{TAG|PLUGINS/LOCAL_POTENTIAL}} calls the Python plugin for the local potential interface for each SCF step
----

When {{TAG|PLUGINS/LOCAL_POTENTIAL}}=.TRUE., VASP calls the local_potential Python function at the end of each SCF step. 
The primary use-case of this tag is to add a quantity on the real space grid to the local potential and a scalar quantity to the total energy of a VASP calculation through a Python plugin.
## Expected inputs
The local_potential Python function expects the following inputs,

def local_potential(constants, additions):
    ...

where constants and additions and Python dataclasses (https://docs.python.org/3/library/dataclasses.html).
The constants dataclass consists of the following inputs, listed here with their associated datatypes (https://numpy.org/doc/stable/user/basics.types.html)

@dataclass(frozen=True)
class ConstantsLocalPotential:
    ENCUT: float
    NELECT: float
    shape_grid: IntArray
    number_ions: int
    number_ion_types: int
    ion_types: IndexArray
    atomic_numbers: IntArray
    lattice_vectors: DoubleArray
    positions: DoubleArray
    ZVAL: DoubleArray
    charge_density: Optional[DoubleArray] = None
    hartree_potential: Optional[DoubleArray] = None
    ion_potential: Optional[DoubleArray] = None
    dipole_moment: Optional[DoubleArray] = None
    neighbor_list: List[Neighbors] = field(default_factory=list)

Note that the {{FILE|INCAR}} tags are capitalized.
shape_grid is a three dimensional integer array which stores the shape of the real space grid, {{TAG|NGXF}}, {{TAG|NGYF}} and {{TAG|NGZF}},
number_ions is the total number of ions listed in the {{FILE|POSCAR}} file,
number_ion_types is the number of ion corresponding to each ion type in the convention of the {{FILE|POSCAR}} file,
ion_types stores the total number of ion types,
atomic_numbers contains the atomic number for each atom type,
lattice_vectors and positions contain the lattice vectors and positions of the current SCF step
charge_density,hartree_potential,ion_potential contains the charge density, the hartree potential and the ion potential respectively on the real space grid.
dipole_moment stores an array with three elements consisting of the dipole moment along x, y and z cartesian directions.
{{NB| mind | The dipole moment is provided only if {{TAG|LDIPOL}}{{=}}.TRUE.}}
neighbor_list contains a list of all neighbors near an atom up to a cutoff {{TAG|PLUGINS/NEIGHBOR_CUTOFF}}.

The additions dataclass consists of the following modifiable outputs

@dataclass
class AdditionsLocalPotential:
    total_energy: float
    total_potential: DoubleArray
## Modifying quantities
Modify the quantities listed in additions by adding to them. For example, if you wanted to add one to every real space local potential grid point,

import numpy as np
def local_potential(constants, additions)
    additions.total_potential += np.ones(constants.shape_grid)

{{WARN_PLUGINS_CONSTANTS}}
## Related tags and articles
Plugins,
{{TAG|PLUGINS/FORCE_AND_STRESS}},
{{TAG|PLUGINS/NEIGHBOR_CUTOFF}},
{{TAG|PLUGINS/OCCUPANCIES}},
{{TAG|PLUGINS/STRUCTURE}}

{{sc|PLUGINS/LOCAL_POTENTIAL|Examples|Examples that use this tag}}

Category:INCAR tag
