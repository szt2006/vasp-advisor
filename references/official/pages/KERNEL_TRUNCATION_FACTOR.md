{{TAGDEF|KERNEL_TRUNCATION/FACTOR| real}}
{{DEF|KERNEL_TRUNCATION/FACTOR|$\sqrt{3}$|if {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY|0}}|1|if {{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY|2}}}}
{{DISPLAYTITLE:KERNEL_TRUNCATION/FACTOR}}
**Description:**  
Determines the spatial extent of the truncated Coulomb interaction relative to the computational cell dimension along the truncation direction.  

----

{{TAG|KERNEL_TRUNCATION/FACTOR}} defines the cutoff distance of the Coulomb-kernel-truncation boundary. It is expressed as a fraction of the simulation-cell length along the truncated axis (e.g., the surface normal for 2D systems {{TAG|KERNEL_TRUNCATION/ISURFACE}}).  
{{NB|mind|
*If{{TAG|KERNEL_TRUNCATION/LTRUNCATE|F}}, {{TAG|KERNEL_TRUNCATION/FACTOR}} is ignored.
*Available as of VASP.6.5.0.}}
## Related tags and articles
{{TAG|KERNEL_TRUNCATION/LTRUNCATE}},  
{{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}},  
{{TAG|KERNEL_TRUNCATION/LCOARSEN}},  
{{TAG|KERNEL_TRUNCATION/IPAD}},  
{{TAG|KERNEL_TRUNCATION/ISURFACE}}

Category:INCAR tag
Category:Electrostatics
