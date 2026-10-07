{{TAGDEF|KSPACING_OPT|[real]|0.5}}
{{DISPLAYTITLE:KSPACING_OPT}}
Description: Spacing between **k** points in the automatically generated mesh for the {{TAG|KPOINTS_OPT}} driver if the {{FILE|KPOINTS_OPT}} file is not present.

----

{{TAG|KSPACING_OPT}} is used to define the **k**-point mesh of the {{TAG|KPOINTS_OPT}} driver, where the wave functions are computed non-self-consistently. This is useful to obtain the density of states on a mesh finer than the one used in the SCF run.

{{TAG|KSPACING_OPT}} is the smallest allowed spacing between **k** points in units of \AA^{-1}. The number of **k** points increases when the spacing is decreased.
The number of **k** points in the direction of the first, second and third reciprocal lattice
vector is determined by  N_i= \mathrm{max}(1, \mathrm{ceiling}( | \mathbf{b}_i| 2\pi / \mathrm{KSPACING\_OPT} )),
where \mathrm{ceiling}( x ) returns the least integer that is equal or larger than x. Here,  \mathbf{b}_i  are the reciprocal lattice vectors  \mathbf{b}_i \mathbf{a}_j = \delta_{ij} .
The generated grid is centered at the \Gamma point if {{TAG|KGAMMA|T}} (default), i.e., includes the \Gamma point. For {{TAG|KGAMMA|F}}, the grid is shifted away from the \Gamma point as done for Monkhorst-Pack grids.
{{Available|6.6.0}}
## Related tags and articles
Tags: {{TAG|KSPACING}}, {{TAG|KGAMMA}}, {{TAG|LKPOINTS_OPT}}

Files: {{FILE|KPOINTS}}, {{FILE|KPOINTS_OPT}}

{{sc|KSPACING_OPT|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:Crystal momentum
