{{TAGDEF|ISPIN|1 {{!}} 2|1}}

Description: {{TAG|ISPIN}} specifies whether a calculation is performed with or without spin polarization.
----
In spin-polarized calculations, VASP treats spin-up and spin-down electrons separately, allowing each spin channel to develop a different charge density and occupation. This is essential for magnetic systems; for nonmagnetic systems it is generally unnecessary and increases computational cost.

*{{TAG|ISPIN}}=1: VASP performs a non-spin-polarized calculation. Spin-up and spin-down electrons share a single charge density.

*{{TAG|ISPIN}}=2: VASP performs a spin-polarized collinear calculation. Spin-up and spin-down electrons are treated separately.

Spin-polarized calculations are commonly used for magnetic materials such as Fe, Co, Ni, and magnetic oxides. To initialize magnetic moments on atoms, combine {{TAG|ISPIN}}=2 with {{TAG|MAGMOM}}.

 ISPIN = 2
 MAGMOM = 2*5.0 2*-5.0

This example initializes two atoms with positive magnetic moments and two atoms with negative magnetic moments, which may be useful for antiferromagnetic calculations.

{{NB|mind|For noncollinear calculations, {{TAG|ISPIN}} is ignored; use {{TAG|LNONCOLLINEAR}}{{=}}.TRUE. instead.|:}}

{{NB|mind|Since VASP 6.5.0, the calculation exits with an error if {{TAG|ISPIN}}{{=}}2 and {{TAG|MAGMOM}} are used together with {{TAG|LNONCOLLINEAR}}{{=}}.TRUE.|:}}
## Related tags and articles
{{TAG|MAGMOM}}
{{TAG|LNONCOLLINEAR}}

{{sc|ISPIN|Howto|Examples that use this tag}}

Category:INCAR tagCategory:Magnetism
