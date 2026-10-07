{{TAGDEF|KSPACING|[real]|0.5}}

Description: Spacing between **k** points in automatically generated mesh if the {{FILE|KPOINTS}} file is not present.

----

{{TAG|KSPACING}} is the smallest allowed spacing between **k** points in units of \AA^{-1}. The number of **k** points increases when the spacing is decreased.

The number of **k** points in the direction of the first, second and third reciprocal lattice
vector is determined by  N_i= \mathrm{max}(1, \mathrm{ceiling}( | \mathbf{b}_i| 2\pi / \mathrm{KSPACING} )),
where \mathrm{ceiling}( x ) returns the least integer that is equal or
larger than x. Here,  \mathbf{b}_i   are the reciprocal lattice vectors  \mathbf{b}_i \mathbf{a}_j = \delta_{ij} .

The generated grid is centered at the \Gamma point if {{TAG|KGAMMA|T}} (default), i.e., includes the \Gamma point. For {{TAG|KGAMMA|F}}, the grid is shifted away from the \Gamma point as done for Monkhorst-Pack grids.
{{NB|mind|The definition of  N_i is not entirely identical with the deprecated automatic k-point generation used in the {{FILE|KPOINTS}} file. We recommend using the {{TAG|KSPACING}} tag and avoiding the automatic mode via the {{FILE|KPOINTS}} file.}}
## Related tags and articles
Tags: {{TAG|KGAMMA}}, {{TAG|KSPACING_OPT}}

Files: {{FILE|KPOINTS}}, {{FILE|KPOINTS_OPT}}

{{sc|KSPACING|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:Crystal momentum
