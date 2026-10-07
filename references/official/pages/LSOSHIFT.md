{{TAGDEF| LSOSHIFT |[logical]|LSORBIT}}

Description: {{TAG| LSOSHIFT |.True.}} activates spin–orbit coupling (SOC) contributions to the calculated chemical shielding tensor in NMR.
----
{{TAG|LSOSHIFT|.True.}} allows accounting for spin-orbit coupling (SOC) for the computation of nuclear magnetic resonance (NMR) chemical shielding tensors within linear response theory ({{TAG|LCHIMAG}}). SOC contributions are essential for accurate shielding predictions for heavy elements where spin–orbit effects influence the induced magnetic responses.

The relativistic effects are included on the level of the spin-orbit zeroth-order regular approximation (ZORA) {{cite|lenthe:jcp:1993}} employing the gauge-including projector augmented waves (GIPAW) approach. The implementation and benchmarks are presented by Speelman et al.{{cite|speelman:jcp:2025}}. These calculations require the executable vasp_ncl.
{{NB|warning|We do **not** recommend using {{TAG|LZORA|T}} and {{TAG|LSOSHIFT|T}} together, since it gives worse results, although being formally correct.{{cite|speelman:jcp:2025}}}}
{{NB|mind|This tag is only supported as of VASP.6.6.0.}}
## Related tags and articles
{{TAG|LSORBIT}}, {{TAG|LCHIMAG}}, {{TAG|LZORA}}

{{sc| LSOSHIFT |Howto|Workflows that use this tag}}
## References
Category:INCAR tagCategory:NMRCategory:MagnetismCategory:Spin-orbit couplingCategory:Noncollinear magnetism
