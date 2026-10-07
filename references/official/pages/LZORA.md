{{TAGDEF|LZORA|[logical]|.False.}}

Description: {{TAG|LZORA|.True.}} yields ZORA scalar-relativistic chemical shieldings in NMR.
----

The zeroth-order regular approximation (ZORA){{cite|lenthe:jcp:1993}} is a way to approximate the fully relativistic Dirac equation while keeping a two-component formalism. It captures relativistic effects without solving the full four-component Dirac equation. ZORA can be used in two flavors: scalar-relativistic ZORA (no spin dependence) and spin–orbit ZORA (includes spin-orbit coupling explicitly).

{{TAG|LZORA|.True.}} allows accounting for the ZORA K factor in the computation of nuclear magnetic resonance (NMR) chemical shielding tensors within linear response theory ({{TAG|LCHIMAG}}) on the level of the scalar-relativistic ZORA. Scalar ZORA calculations can be executed using vasp_std.
{{NB|warning|We do **not** recommend using {{TAG|LZORA|T}} and {{TAG|LSOSHIFT|T}} together, since it gives worse results, although being formally correct.{{cite|speelman:jcp:2025}}}}
{{NB|mind|This tag is only supported as of VASP.6.6.0.}}
## Related tags and articles
{{TAG|LCHIMAG}}, {{TAG|LSOSHIFT}}

{{sc|LZORA|Howto|Workflows that use this tag}}
## References
Category:INCAR tagCategory:NMRCategory:MagnetismCategory:Spin-orbit coupling
