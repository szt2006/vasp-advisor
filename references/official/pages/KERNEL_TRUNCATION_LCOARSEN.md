{{TAGDEF|KERNEL_TRUNCATION/LCOARSEN| .True. {{!}} .False.|.False.}}
{{DISPLAYTITLE:KERNEL_TRUNCATION/LCOARSEN}}
Description: Coarsen the charge density before padding to speed up the computation of the local potential in the Coulomb-kernel-truncation method.
----
The Coulomb-kernel-truncation method ({{TAG|KERNEL_TRUNCATION/LTRUNCATE}}) modifies the electrostatic potential to remove spurious interactions between periodic images in systems with reduced dimensionality (e.g. molecules or surfaces). 
{{TAG|KERNEL_TRUNCATION/LCOARSEN|T}} avoids significantly increasing FFT-grid sizes by using a *coarsen-before-padding* approach:

* The full electrostatic potential is first computed under standard 3D periodic boundary conditions.
* A coarse representation of the charge density on a reduced FFT-grid which is constructed by retaining only the long-wavelength (low-|G|) components responsible for long-range interactions.
* The truncated Coulomb kernel is applied only to this coarse density using a padded grid (see {{TAG|KERNEL_TRUNCATION/IPAD}}).
* The final potential is obtained by subtracting the long-range periodic contribution and replacing it with the correctly truncated one.

This procedure exploits the fact that long-range electrostatics depends only on low-frequency components of the charge density, allowing the expensive padded FFTs to be performed on a much smaller grid with minimal loss of accuracy.
{{NB|mind|If {{TAG|KERNEL_TRUNCATION/LTRUNCATE|F}}, all other KERNEL_TRUNCATION tags including {{TAG|KERNEL_TRUNCATION/LCOARSEN}} are ignored.}}
## Related tags and articles
{{TAG|KERNEL_TRUNCATION/LTRUNCATE}},
{{TAG|KERNEL_TRUNCATION/IDIMENSIONALITY}},
{{TAG|KERNEL_TRUNCATION/ISURFACE}},
{{TAG|KERNEL_TRUNCATION/IPAD}},
{{TAG|KERNEL_TRUNCATION/FACTOR}}

Category:INCAR tagCategory:ElectrostaticsCategory:2D materials
