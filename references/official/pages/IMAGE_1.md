{{DISPLAYTITLE:IMAGE_1}}
{{TAGDEF|IMAGE_1|block construct|None}}

Description: Group {{FILE|INCAR}} settings for calculations using {{TAG|IMAGES}}. 
----
{{TAG|IMAGE_1}} defines the {{FILE|INCAR}} settings used for a calculation in an image calculation, e.g., 01 for nudged elastic band calculations, parallel tempering, and thermodynamic integration, cf. {{TAG|IMAGES}} for use cases of the tag. 
{{NB|important|Replace _1, _2, ... with the desired image index (the same index VASP uses for the per-image subdirectories 01, 02, ...). The number of usable indices is bounded by {{TAG|IMAGES}}.}}
## Related tags and articles
{{TAG|IMAGES}}, {{TAG|NCORE_IN_IMAGE1}}, {{TAG|IMAGES}}, {{TAG|VCAIMAGES}}
## References
Category:INCAR tagCategory:Advanced molecular-dynamics sampling
