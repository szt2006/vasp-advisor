{{TAGDEF|KERNEL_TRUNCATION/LTRUNCATE| .True. {{!}} .False.|.False.}}
{{DISPLAYTITLE:KERNEL_TRUNCATION/LTRUNCATE}}
Description: Truncates the Coulomb kernel to remove electrostatic interactions along non-periodic dimensions.
----
Setting {{TAG|KERNEL_TRUNCATION/LTRUNCATE}} = T  switches on the Coulomb-kernel-truncation method{{cite|vijay:prb:2025}}{{cite|rozzi:prb:2006}}{{cite|sohier:prb:2017}}. It effectively removes interactions with periodic replicas in non-periodic directions. In other words, the interactions are removed along the surface normal for 2D materials, and along all directions for 0D systems, i.e. for isolated atoms and molecules.

In the simplest implementation of the Coulomb-kernel-truncation method ({{TAG|KERNEL_TRUNCATION/LCOARSEN|F}}), the computational cell provided in the {{FILE|POSCAR}} file is internally padded by an additional vacuum (see {{TAG|KERNEL_TRUNCATION/IPAD}}). This implies increasing the FFT-grid sizes by a certain factor and thus leads to a significant increase in computational cost.
{{NB|tip|Use the {{TAG|KERNEL_TRUNCATION/LCOARSEN|T}} to avoid the increased FFT-grid sizes.}}
{{NB|mind|
*{{TAG|KERNEL_TRUNCATION/LTRUNCATE}} acts as a "super-tag", i.e. unless this tag is switched on further options in KERNEL_TRUNCATION will be ignored.
*This tag is only available as of VASP.6.5.0.}}
Detailed information about the setting are documented on respective related tags.
{{NB|warning|When padding is used, the vaccum is added on the edges of the cell, therefore it is very important there are no atoms on the cell boundary in the non-periodic direction. We recommend centering the motif in the simulation box. If you encounter problems using Coulomb truncation with padding, try the same calculations without padding (see examples bellow).}}
## Example
KERNEL_TRUNCATION {
     LTRUNCATE       = T
     IDIMENSIONALITY = 2
     ISURFACE        = 3
     LCOARSEN        = F
}

In this case, we pad the cell along the surface normal direction.
The Coulomb interaction is truncated beyond the boundaries of the cell along this direction.

KERNEL_TRUNCATION {
     LTRUNCATE       = T
     IDIMENSIONALITY = 2
     ISURFACE        = 3
     IPAD            = 1
     FACTOR          = 0.5
}

This setup corresponds to truncating the Coulomb interaction along the surface normal direction (say, along z) for a 2D material, using no vacuum padding and a truncation length of z/2. In this case, half of the simulation box is effectively unused and will produce a potential that is not desired.
However, the algorithm is much simpler.
We recommend this configuration for debugging purposes.
## Related tags and articles
{{TAG|KERNEL_TRUNCATION/LCOARSEN}},
{{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}},
{{TAG|KERNEL_TRUNCATION/ISURFACE}},
{{TAG|KERNEL_TRUNCATION/FACTOR}},
{{TAG|KERNEL_TRUNCATION/IPAD}}
## References
Category:INCAR tagCategory:ElectrostaticsCategory:2D materials
