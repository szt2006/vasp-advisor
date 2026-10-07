{{TAGDEF|PLUGINS/OCCUPANCIES| .True. {{!}} .False.|.False.}}

Description: {{TAG|PLUGINS/OCCUPANCIES}} calls the Python plugin for the occupancies interface for each ionic relaxation step
----

When {{TAG|PLUGINS/OCCUPANCIES}}=.TRUE., VASP calls the occupancies Python function at the end of each ionic relaxation step. 
The primary use-case of this tag to recompute the occupancies after performing modifications through other plugins such as {{TAG|PLUGINS/LOCAL_POTENTIAL}}. It also allows changing {{TAG|NELECT}}, {{TAG|EFERMI}}, {{TAG|NUPDOWN}}, {{TAG|ISMEAR}}, {{TAG|SIGMA}}, {{TAG|EMIN}} and {{TAG|EMAX}} at the end of each SCF step, to be reflected in the next step.
## Expected inputs
The occupancies Python function expects the following inputs,

def occupancies(constants, additions):
    ...

where constants and additions and Python dataclasses (https://docs.python.org/3/library/dataclasses.html).
The constants dataclass consists of the following inputs, listed here with their associated datatypes (https://numpy.org/doc/stable/user/basics.types.html)

@dataclass(frozen=True)
class ConstantsOccupancies:
    NELECT: float
    EFERMI: float
    NUPDOWN: float
    ISMEAR: int
    SIGMA: float
    EMIN: float
    EMAX: float

The additions dataclass consists of the same quantities as the constants tag.
{{NB| mind | Calling this interface implicitly triggers a recalculation of the occupancies}}
## Modifying quantities
Modify the quantities listed in additions by adding to them.

import numpy as np
def structure(constants, additions)
    additions.NELECT += 1

{{WARN_PLUGINS_CONSTANTS}}
## Related tags and articles
Plugins,
{{TAG|PLUGINS/FORCE_AND_STRESS}},
{{TAG|PLUGINS/LOCAL_POTENTIAL}},
{{TAG|PLUGINS/STRUCTURE}}

{{sc|PLUGINS/OCCUPANCIES|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Electronic occupancy
