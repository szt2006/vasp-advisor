{{TAGDEF|LTAU|.True. {{!}} .False.}}
{{DEF| LTAU |.False.| |.True.|if the XC functional depends on the kinetic energy density (see metaGGAs).}}

Description: Request evaluation of the kinetic energy density.
----

By default only metaGGAs that depend on the kinetic energy density compute it. However, setting {{TAG|LTAU|T}} in the {{FILE|INCAR}} file alows to write the kinetic energy density to file even in case the XC functional is independent of the kinetic energy density. {{TAG|LCHARG}} controls whether the charge density and the kinetic energy density are written.
## Related tags and articles
Restart and output files cheat sheet

{{TAG|LCHARG}}, {{TAG|LH5}}, {{TAG|LCHARGH5}}, {{FILE|TAUCAR}}, {{FILE|vaspwave.h5}}

{{sc|LCHARG|Howto|Workflows that use this tag}}

Category:INCAR tag
