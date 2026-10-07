{{TAGDEF|KERNEL_TRUNCATION/IDIMENSIONALITY| 0 {{!}} 2 {{!}} 3 | 3}}
{{DISPLAYTITLE:KERNEL_TRUNCATION/IDIMENSIONALITY}}
Description: Specifies the boundary condition used to compute the hartree and ionic potential. 
----

If {{TAG|KERNEL_TRUNCATION/LTRUNCATE}} = T, {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}} determines the boundary condition that is used to compute the local potential.
Setting {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}} to either 0 or 2 uses the 0D and 2D truncated kernel respectively.{{cite|vijay:prb:2025}}{{cite|rozzi:prb:2006}}{{cite|sohier:prb:2017}}
These kernels create 0D (i.e. no periodic interactions, as is the case of molecules) and 2D (i.e. periodic interactions only in two dimensions, as in the case for surfaces).
{{NB|mind|
*If {{TAG|KERNEL_TRUNCATION/LTRUNCATE}} is switched off, all other KERNEL_TRUNCATION tags including {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}} will be ignored.
*Available as of VASP.6.5.0.}}
## {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}} = 0
Consider using the option when computing energies and forces of atoms and molecules.
Recommended {{FILE|INCAR}} tags to be used with option are
  {{TAGBL|KERNEL_TRUNCATION/LTRUNCATE}} = T
  {{TAGBL|KERNEL_TRUNCATION/IDIMENSIONALITY}} = 0
  {{TAGBL|KERNEL_TRUNCATION/LCOARSEN}} = T
## {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}} = 2
Use this option when computing the energies and forces of 2D and quasi-2D systems, such as 2D materials and surfaces. We suggest setting the following {{FILE|INCAR}} tags for a surface that is oriented along the z-axis
  {{TAGBL|KERNEL_TRUNCATION/LTRUNCATE}} = T
  {{TAGBL|KERNEL_TRUNCATION/IDIMENSIONALITY}} = 2
  {{TAGBL|KERNEL_TRUNCATION/LCOARSEN}} = T
  {{TAGBL|KERNEL_TRUNCATION/ISURFACE}} = 3
## {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}} = 3 (default)
The system is periodic in all dimensions, i.e. there is no influence of the Coulomb-kernel truncation on the resulting energies and forces.
## Related tags and articles
{{TAG|KERNEL_TRUNCATION/LTRUNCATE}},
{{TAG|KERNEL_TRUNCATION/LCOARSEN}},
{{TAG|KERNEL_TRUNCATION/ISURFACE}},
{{TAG|KERNEL_TRUNCATION/FACTOR}},
{{TAG|KERNEL_TRUNCATION/IPAD}}
## References
Category:INCAR tagCategory:ElectrostaticsCategory:2D materials
