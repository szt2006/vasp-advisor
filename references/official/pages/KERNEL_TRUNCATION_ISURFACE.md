{{TAGDEF|KERNEL_TRUNCATION/ISURFACE| 1 {{!}} 2 {{!}} 3 }}
{{DISPLAYTITLE:KERNEL_TRUNCATION/ISURFACE}}
Description: Specifies the non-periodic dimension when performing calculations with the Coulomb-kernel-truncation method for 2D materials.
----

When performing Coulomb-kernel truncation ({{TAG|KERNEL_TRUNCATION/LTRUNCATE|T}}) with {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY|2}}, {{TAG|KERNEL_TRUNCATION/ISURFACE}} specifies which direction is non-periodic.
If the surface normal points in the direction of the x-axis set {{TAG|KERNEL_TRUNCATION/ISURFACE|1}}, if it is along the y-axis set {{TAG|KERNEL_TRUNCATION/ISURFACE|2}}, and along the z-axis set {{TAG|KERNEL_TRUNCATION/ISURFACE|3}}.
{{NB|mind|
*IF {{TAG|KERNEL_TRUNCATION/LTRUNCATE|F}}, all other KERNEL_TRUNCATION tags including {{TAG|KERNEL_TRUNCATION/ISURFACE}} are ignored.
*Available as of VASP.6.5.0.}}
## Related tags and articles
{{TAG|KERNEL_TRUNCATION/LTRUNCATE}},
{{TAG|KERNEL_TRUNCATION/LCOARSEN}},
{{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}},
{{TAG|KERNEL_TRUNCATION/IPAD}},
{{TAG|KERNEL_TRUNCATION/FACTOR}}

Category:INCAR tagCategory:ElectrostaticsCategory:2D materials
