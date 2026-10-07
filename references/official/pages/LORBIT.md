{{TAGDEF|LORBIT|0 {{!}} 1 {{!}} 2 {{!}} 5 {{!}} 10 {{!}} 11 {{!}} 12 | 0 }}

Description: Selects a projection method onto local quantum numbers (lm) and writes {{FILE|PROCAR}}/{{FILE|PROOUT}} file.
----

When {{TAG|LORBIT}} is set, VASP performs a post-processing step of the Kohn-Sham (KS) orbitals to decompose the KS orbitals into local quantum numbers (lm) and obtain local properties, e.g., the on-site charge density or on-site magnetic moments due to the spin degrees of freedom. The decomposition is achieved by means of one of several projection methods selected by {{TAG|LORBIT}}. All these projections rely on the fact that most of the charge density is close to the ion center, and interstitial regions separate them well. This is merely a qualitative approach in contrast to performing a wannierization in order to obtain a localized basis, but often it serves as a good estimate. 
{{NB|tip| As this is a post-processing step, {{TAG|LORBIT}} can be added/changed when restarting a converged calculation. To this end, set {{TAG|ALGO}}{{=}}None and the desired {{TAG|LORBIT}}, and restart from {{FILE|WAVECAR}}.}}
For VASP version < 6 with {{TAG|LORBIT}} >= 11 and {{TAG|ISYM}} = 2, see known issues. 
## Projection methods
See the table for an overview:

:{| border="1" cellspacing="0" cellpadding="5"
  {{TAG|LORBIT}} || {{TAG|RWIGS}} tag || files written
  0 || required || {{FILE|DOSCAR}} and {{FILE|PROCAR}}
  1 || required || {{FILE|DOSCAR}} and *lm*-decomposed {{FILE|PROCAR}}
  2 || required || {{FILE|DOSCAR}} and *lm*-decomposed {{FILE|PROCAR}} + phase factors
  5 || required || {{FILE|DOSCAR}} and {{FILE|PROOUT}}
  10 || ignored || {{FILE|DOSCAR}} and {{FILE|PROCAR}}
  11 || ignored || {{FILE|DOSCAR}} and *lm*-decomposed {{FILE|PROCAR}}
  12 || ignored || {{FILE|DOSCAR}} and *lm*-decomposed {{FILE|PROCAR}} + phase factors (not recommended)
  13 || ignored || {{FILE|DOSCAR}} and *lm*-decomposed {{FILE|PROCAR}} + phase factors, choose best projector for each band (not recommended)
  14 || ignored || {{FILE|DOSCAR}} and *lm*-decomposed {{FILE|PROCAR}} + phase factors, choose single projector for interval {{TAG|EMIN}},{{TAG|EMAX}} 
### For {{TAG|LORBIT}} < 10
The projection is onto spherical harmonics at each ionic site within a sphere defined by {{TAG|RWIGS}}. The radius must be specified for each atomic species, and there is some uncertainty introduced depending on the size of the sphere.
### For {{TAG|LORBIT}} >= 10
The projection uses the projector functions that are provided by the PAW method. This is, of course, still a qualitative approach because also, for the PAW projectors, the radius was somehow defined, and it is not guaranteed to be the best choice for that particular system as it depends on the chemical composition and crystal or molecular structure.
### Phase factors
For {{TAG|LORBIT}}>=12:
The **phase factors** written by VASP can usually only be used as a qualitative measure of the projection of the orbitals into the atomic sphere. The main issue is that most VASP {{FILE|POTCAR}} files have two or three projectors per l-quantum number, and projecting an orbital onto two projectors will yield two complex numbers. VASP combines these two numbers into a single number. The precise algorithms differ in different versions of VASP, and we recommend that you inspect the source code for more details. From vasp.6 onward, an improved scheme has been implemented and can be selected using {{TAG|LORBIT}}=14. In this case, VASP first selects a single projector for each l-quantum number by linearly combining all projectors with the same l-quantum number. This is done in such a way that the new projector is optimally chosen to represent the calculated orbitals in the energy interval specified by {{TAG|EMAX}} and {{TAG|EMIN}}. In the second step, VASP projects onto these optimized projectors, yielding a single complex number for each orbital, site and l-quantum number, which is written to the {{FILE|PROCAR}} file. For details we also refer to {{cite|Schuler:JPCM:2018}}.
{{TAG|LORBIT}}=12 should no longer be used except for qualitative calculations. LORBIT=13 chooses the projectors also automatically, but allows for different optimal linear combinations for each orbital.
Note that this is generally not desirable, since the  resultant projection is not compatible with the required properties of a projection operator (a projection operator needs to use energy and orbital independent projectors).
Hence, do not use {{TAG|LORBIT}}=13 for anything but a qualitative analysis.

{{TAG|LORBIT}}=13 and {{TAG|LORBIT}}=14 are only supported by version >=5.4.4. 
## On-site partial charge densities and magnetization
The partial charge densities can be found in the {{FILE|OUTCAR}}
 total charge     
 
 # of ion       s       p       d       tot
 ------------------------------------------
     1        1.514   0.000   0.000   1.514
     2        0.123   0.345   0.000   0.468
Here, the first column corresponds to the ion index \alpha, the s, p, d,... columns correspond to the partial charges for l=0,1,2,\cdots defined as

\rho_{\alpha l}=\frac{1}{N_{\bf k}} \sum_{n{\bf k}}f_{n{\bf k}} \sum_{m=-l}^{l}|\langle Y_{lm}^{\alpha}|\phi_{n\mathbf{k}}\rangle|^2

The \langle Y_{lm}^{\alpha}|\phi_{n\mathbf{k}}\rangle are obtained from the projection of the (occupied) KS orbitals |\phi_{n{\bf k}}\rangle onto spherical harmonics that are non zero within spheres of a radius {{TAG|RWIGS}} centered at ion \alpha and the last column is the sum \sum_{l}\rho_{\alpha l}. 

Note that depending on the system, an "f" column is written as well. 

*In case of spin-polarized magnetic calculations ({{TAG|ISPIN}}=2), the partial magnetization densities are written to the {{FILE|OUTCAR}}
 magnetization (x)
  
 # of ion       s       p       d       tot
 ------------------------------------------
     1        0.000   0.000   0.000   0.000
     2        0.000   0.245   0.000   0.245

Here, the magnetization density is calculated from the difference in the up and down spin channel m^{\alpha l}_z = \rho_{\alpha l}^{\uparrow}-\rho_{\alpha l}^{\downarrow}

Although the direction of the magnetization densities is meaningless in a spin-polarized calculation (no spin-orbit coupling, see {{TAG|LSORBIT}}), here the projection axis is the z-axis. This is consistent withe the behavior upon restarting a noncollinear calculation from a spin-polarized one with default {{TAG|SAXIS}}.

*In case of noncollinear calculations ({{TAG|LNONCOLLINEAR}}=.TRUE.), the lines after "total charge" correspond to the diagonal average 
 \frac{\rho_{\alpha l}^{\uparrow\uparrow} - \rho_{\alpha l}^{\downarrow \downarrow}}{2} 
of the density tensor

::
\rho_{\alpha l} = \left(\begin{matrix}
  \rho_{\alpha l}^{\uparrow \uparrow }   &  \rho_{\alpha l}^{\uparrow \downarrow}     \\
  \rho_{\alpha l}^{\downarrow \uparrow}  &  \rho_{\alpha l}^{\downarrow \downarrow}   \\
 \end{matrix}\right), 

which is determined from the projected components 

::
\rho^{\mu\nu}_{\alpha l} = \frac{1}{N_{\bf k}} \sum_{n{\bf k}}f_{n{\bf k}} \sum_{m=-l}^{l} 
\langle \chi_{n {\bf k}}^\mu | Y_{lm}^\alpha \rangle
\langle  Y_{lm}^\alpha | \chi_{n {\bf k}}^\nu \rangle 

of the spinor |\Psi_{n{\bf k}}\rangle=\left(\begin{matrix}\chi_{n{\bf k}}^\uparrow \\\chi_{n{\bf k}}^\downarrow \end{matrix}\right) 

Similarly, the lines after "magnetization (x)", "magnetization (y)", and "magnetization (z)"correspond to the partial magnetization density 

::
m_{\alpha l}^j = \frac{1}{2}\sum_{\mu,\nu=1}^2 \sigma^j_{\mu \nu} \rho_{\alpha l}^{\mu \nu}.

projected onto Pauli matrices \{\sigma_1, \sigma_2, \mathbf{\sigma}_3\}. By default, this corresponds to Cartesian directions \sigma_1=\hat x, \sigma_2 =\hat y, \sigma_3 = \hat z, but the orientation can be changed using {{TAG|SAXIS}}.
## Partial density of states (pDOS)
The partial density of states (pDOS) is the DOS projected onto specific ions or atomic orbitals. The output for it can be found in the following output files:

*{{FILE|PROCAR}}: the primary output for pDOS data. Each block lists the projection weight onto each atomic site and angular-momentum channel (s, p, d, ...) for every band and k-point.
*{{FILE|vasprun.xml}}: the pDOS is stored in the &lt;dos&gt;&lt;partial&gt; block, organized by ion and spin:

<dos>
 
  <array>
   <dimension dim="1">gridpoints</dimension>
   <dimension dim="2">spin</dimension>
   <dimension dim="3">ion</dimension>
   <field>energy</field>
   <field>s</field>
   <field>py</field>
   <field>pz</field>
   <field>px</field>
   <field>dxy</field>
   ...
   <set>
    <set comment="ion 1">
     <set comment="spin 1">
      <r> -5.0000  5.5689  1.5445  1.5445  1.5445  0.0009 ... </r>
      ...

*{{FILE|vaspout.h5}}: pDOS data is accessible via {{py4vasp}}:

import py4vasp
calc = py4vasp.Calculation.from_path(".")

# Plot pDOS projected onto specific atoms (e.g., ions 3 and 5)
calc.dos.plot(selection="3, 5")

# Plot by element and orbital character
calc.dos.plot(selection="Fe(d)")

You can learn more about plotting and calculating it in our tutorials:
*{{Tutorial|surface:e02|Ni(100) surface}}
*{{Tutorial|strong_corr:e02|NiO bulk}}
*{{Tutorial|atoms:molecules:e07|CO molecule}}
*{{Tutorial|surface:part3|STM simulations}}
## References## Related tags and articles
{{TAG|RWIGS}},
{{FILE|PROCAR}},
{{FILE|PROOUT}},
{{FILE|DOSCAR}}

{{sc|LORBIT|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Electronic ground-state propertiesCategory:Density of statesCategory:Band structureCategory:Spin-orbit coupling
