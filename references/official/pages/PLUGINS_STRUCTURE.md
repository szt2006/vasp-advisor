{{TAGDEF|PLUGINS/STRUCTURE| .True. {{!}} .False.|.False.}}

Description: {{TAG|PLUGINS/STRUCTURE}} calls the Python plugin for the structure interface for each ionic relaxation step
----

When {{TAG|PLUGINS/STRUCTURE}}=.TRUE., VASP calls the structure Python function at the end of each ionic relaxation step. 
The primary use-case of this tag is to modify the structure based on the computed energy, force and stress tensor.
## Expected inputs
The structure Python function expects the following inputs,

def structure(constants, additions):
    ...

where constants and additions and Python dataclasses (https://docs.python.org/3/library/dataclasses.html).
The constants dataclass consists of the following inputs, listed here with their associated datatypes (https://numpy.org/doc/stable/user/basics.types.html)

@dataclass(frozen=True)
class ConstantsStructure:
    number_ions: int
    number_ion_types: int
    ion_types: IndexArray
    atomic_numbers: IntArray
    lattice_vectors: DoubleArray
    positions: DoubleArray
    POMASS: DoubleArray
    total_energy: float
    forces: DoubleArray
    stress: DoubleArray
    shape_grid: IntArray
    charge_density: DoubleArray
    neighbor_list: List[Neighbors] = field(default_factory=list)

Note that the {{FILE|INCAR}} tags are capitalized.
number_ions is the total number of ions listed in the {{FILE|POSCAR}} file,
number_ion_types is the number of ion corresponding to each ion type in the convention of the {{FILE|POSCAR}} file,
ion_types stores the total number of ion types,
atomic_numbers contains the atomic number for each atom type,
lattice_vectors and positions contain the lattice vectors and positions of the current SCF step
forces and stress are the computed forces and stress tensor and charge_density contains the charge density on the real space grid. shape_grid is a three dimensional integer array which stores the shape of the real space grid, {{TAG|NGXF}}, {{TAG|NGYF}} and {{TAG|NGZF}} and charge_density is the charge density on this real space grid.
neighbor_list contains a list of all neighbors near an atom up to a cutoff {{TAG|PLUGINS/NEIGHBOR_CUTOFF}}.

The additions dataclass consists of the following modifiable outputs

@dataclass
class AdditionsStructure:
    lattice_vectors: DoubleArray
    positions: DoubleArray
## Modifying quantities
Modify the quantities listed in additions by adding to them.

def structure(constants, additions)
    additions.positions += np.ones((constants.number_ions,3))

{{WARN_PLUGINS_CONSTANTS}}
## Related tags and articles
Plugins,
{{TAG|PLUGINS/FORCE_AND_STRESS}},
{{TAG|PLUGINS/LOCAL_POTENTIAL}},
{{TAG|PLUGINS/NEIGHBOR_CUTOFF}}

{{sc|PLUGINS/STRUCTURE|Examples|Examples that use this tag}}

Category:INCAR tag
