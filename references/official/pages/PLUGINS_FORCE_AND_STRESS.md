{{TAGDEF|PLUGINS/FORCE_AND_STRESS| .True. {{!}} .False.|.False.}}

Description: {{TAG|PLUGINS/FORCE_AND_STRESS}} calls the Python plugin for the force and stress interface for each ionic relaxation step
----

When {{TAG|PLUGINS/FORCE_AND_STRESS}}=.TRUE., VASP calls the force_and_stress Python function at the end of each ionic relaxation step. 
You can use this tag to modify forces and the stress tensor to be consistent with modifications to the potential performed with {{TAG|PLUGINS/LOCAL_POTENTIAL}}.
Furthermore, you could implement new force corrections like van-der-Waals functionals or use it to run a machine-learned interatomic potential as the force engine in VASP.
Usually the forces and stress are added to ones obtained by VASP, but you can set {{TAG|PLUGINS/ML_MODE}} to overwrite them instead.
## Expected inputs
The force_and_stress Python function expects the following inputs,

def force_and_stress(constants, additions):
    ...

where constants and additions and Python dataclasses (https://docs.python.org/3/library/dataclasses.html).
The constants dataclass consists of the following inputs, listed here with their associated datatypes (https://numpy.org/doc/stable/user/basics.types.html)

@dataclass(frozen=True)
class ConstantsForceAndStress:
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
    POMASS: DoubleArray
    forces: DoubleArray
    stress: DoubleArray
    charge_density: Optional[DoubleArray] = None
    neighbor_list: List[Neighbors] = field(default_factory=list)

Note that the {{FILE|INCAR}} tags are capitalized.
shape_grid is a three dimensional integer array which stores the shape of the real space grid, {{TAG|NGXF}}, {{TAG|NGYF}} and {{TAG|NGZF}},
number_ions is the total number of ions listed in the {{FILE|POSCAR}} file,
number_ion_types is the number of ion corresponding to each ion type in the convention of the {{FILE|POSCAR}} file,
ion_types stores the total number of ion types,
atomic_numbers contains the atomic number for each atom type,
lattice_vectors and positions contain the lattice vectors and positions of the current SCF step
forces and stress are the computed forces and stress tensor and charge_density contains the charge density on the real space grid.
neighbor_list contains a list of all neighbors near an atom up to a cutoff {{TAG|PLUGINS/NEIGHBOR_CUTOFF}}.

The additions dataclass consists of the following modifiable outputs

@dataclass
class AdditionsForceAndStress:
    total_energy: float
    forces: DoubleArray
    stress: DoubleArray
## Modifying quantities
Modify the quantities listed in additions by adding to them. For example, if you wanted to add one to the forces

import numpy as np
def force_and_stress(constants, additions)
    additions.forces += np.ones((constants.number_ions,3))

{{WARN_PLUGINS_CONSTANTS}}

We provide a special helper class if you want to interface ASE calculators with VASP.
This class makes these use cases almost trivial

from vasp.force_field import AseForceField

def force_and_stress(constants, additions):
    calculator = ...  # setup your ASE calculator
    force_field = AseForceField(calculator)
    force_field.force_and_stress(constants, additions)
## Related tags and articles
Plugins,
{{TAG|PLUGINS/LOCAL_POTENTIAL}},
{{TAG|PLUGINS/OCCUPANCIES}},
{{TAG|PLUGINS/ML_MODE}},
{{TAG|PLUGINS/NEIGHBOR_CUTOFF}},
{{TAG|PLUGINS/STRUCTURE}}

{{sc|PLUGINS/FORCE_AND_STRESS|Examples|Examples that use this tag}}

Category:INCAR tag
