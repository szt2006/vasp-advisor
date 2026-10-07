{{TAGDEF|VELOCITY|[logical]|.false.}}

Description: Determines whether the ionic velocities are written to the {{FILE|vaspout.h5}} file during an MD run.
{{NB|mind|This tag is only available as of VASP.6.4.0.}}
----

You can use {{py4vasp|url=calculation/velocity/}} to read the velocities into a Python dictionary

from py4vasp import calculation
calculation.velocity.read()

or to visualize the velocity in the crystal structure

from py4vasp import calculation
calculation.velocity.plot()
## Related tags and articles
Sampling phonon spectra from molecular-dynamics simulations

{{sc|VELOCITY|Howto|Workflows that use this tag}}

Category:INCAR tagCategory:Molecular dynamics
