{{TAGDEF|KGAMMA|[logical]|.TRUE.}}

Description: Whether the automatically generated **k**-point mesh is centered at the \Gamma point.

----

If {{TAG|KGAMMA|.TRUE.}} (default), the **k**-point mesh is centered at the \Gamma point, i.e., it always includes the \Gamma point. If {{TAG|KGAMMA|.FALSE.}}, the mesh is shifted away from the \Gamma point as in a Monkhorst-Pack grid. The number of **k** points on the mesh is controlled by {{TAG|KSPACING}} and {{TAG|KSPACING_OPT}}.
{{NB|important|If a {{FILE|KPOINTS}} file is present, VASP ignores the {{TAG|KGAMMA}} and {{TAG|KSPACING}} tags. Likewise, if a {{FILE|KPOINTS_OPT}} file is present, VASP ignores {{TAG|KGAMMA}} and {{TAG|KSPACING_OPT}}.}}
## Related tags and articles
{{TAG|KSPACING}}, {{TAG|KSPACING_OPT}}

{{sc|KGAMMA|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:Crystal momentum
