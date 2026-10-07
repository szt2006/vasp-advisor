{{TAGDEF|PLUGINS/NEIGHBOR_CUTOFF| [real]}}

Description: {{TAG|PLUGINS/NEIGHBOR_CUTOFF}} determines the cutoff up to which the neighbor list is computed that is passed to the Python plugins. If not set, the neighbor list will be empty.
----

If set, VASP will compute pair distances between atoms in the unit cell and include all pairs below the given cutoff in a neighbor list.
You can use this neighbor list in your plugin to make decisions based on the interatomic distances.

In each plugin the neighbor_list is a list of length number of atoms, where every element of the list is an instance of

@dataclass(frozen=True)
class Neighbors:
    neighbors: IndexArray
    distances: DoubleArray
    directions: DoubleArray

Here, neigbors are the indices of the atoms in vicinity of the selected list element.
Note that this can contain itself because of the periodic boundary conditions.
distances is the norm of the vector between the atom and its neighbors.
directions is the vector describing the direction from the atom to its neighbor.
## Related tags and articles
Plugins,
{{TAG|PLUGINS/FORCE_AND_STRESS}},
{{TAG|PLUGINS/LOCAL_POTENTIAL}},
{{TAG|PLUGINS/STRUCTURE}}

{{sc|PLUGINS/NEIGHBOR_CUTOFF|Examples|Examples that use this tag}}

Category:INCAR tag
