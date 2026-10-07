{{DISPLAYTITLE:EWALD_CUTOFF}}
{{TAGDEF|EWALD_CUTOFF| [real] }}
{{DEF|EWALD_CUTOFF|4.0|}}

Description: {{TAG|EWALD_CUTOFF}} sets the unified cutoff radius for the Ewald summation of the electrostatic interaction. It controls both the number of cells that contribute (in real space) as well as the number of G-vectors that are considered (in reciprocal space).
----

The default value of {{TAG|EWALD_CUTOFF}} is a safe choice in nearly all cases.
For bulk systems, increasing it will not change the total energy by more than a few $\mu$eV.

For surface calculations with large cells and thick vacuum regions, however, some necessary G-vectors may be cut off for the default value of {{TAG|EWALD_CUTOFF}}, and variations in total energy might increase to the order of 10 meV.
This can spoil convergence with respect to the number of layers or the size of the vacuum for weakly bound surfaces.
{{NB|tip|For highly accurate slab calculations, set {{TAG|EWALD_CUTOFF|6.0}}.}}
{{available|6.6.0}}
## Related tags and articles
2D materials,
electrostatics

{{sc|EWALD_CUTOFF|HowTo|Workflows that use this tag}}

Category:INCAR tag
