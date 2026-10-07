{{TAGDEF|WRT_POTENTIAL|string|None}}
{{DISPLAYTITLE:WRT_POTENTIAL}}
Description: Select which component of the local potential to be written as a post-processing step.
----
{{TAG|WRT_POTENTIAL}} can select one or multiple local potentials on the real-space grid in the unit cell to be written, e.g.,
  {{TAGBL|WRT_POTENTIAL}} = total
or
  {{TAGBL|WRT_POTENTIAL}} = hartree ionic
The output is written to {{FILE|vaspout.h5}} and can be accessed either by {{py4vasp}} or HDF5 command-line tools (h5ls, h5dump).

  import py4vasp as pv
  calc = pv.Calculation.from_path(".")
  pot_dict = calc.potential.read("total")

The above allows the creation of a Python dictionary with the potential data.
  h5ls -r vaspout.h5
The above shows the table of contents of {{FILE|vaspout.h5}}. Depending on the keywords specified with {{TAG|WRT_POTENTIAL}} and the system it yields
  /results/potential       Group
  /results/potential/grid  Dataset {3}
  /results/potential/hartree Dataset {1, 24, 24, 24}
  /results/potential/ionic Dataset {1, 24, 24, 24}
  /results/potential/total Dataset {4, 24, 24, 24}
  /results/potential/xc    Dataset {4, 24, 24, 24}
The grid density can be increased by choosing a higher value for {{TAG|ENCUT}} or explicitly by {{TAG|NGXF}}, {{TAG|NGYF}}, {{TAG|NGZF}}.

The first dimension of the datasets in /results/potential is 1 for nonmagnetic calculation, 2 for spin-polarized calculation, and 4 for noncollinear calculations. In case the potential is scalar, i.e., has no B-field-like contribution that couples to the magnetization, only the 1st component exists. Hence, for *hartree* and *ionic*, the first dimension is 1. The components for the magnetic calculations correspond to the spinor representation with the scalar potential in the first component and the B-field in the second ({{TAG|ISPIN}}=2) or B_1, B_2 and B_3 in the 2nd, 3rd and 4th component ({{TAG|LNONCOLLINEAR}}=T) in the basis of Pauli matrices \{\sigma_1, \sigma_2, \mathbf{\sigma}_3\} given by {{TAG|SAXIS}}.
{{NB|mind| As a convention, the \mathbf{G}{{=}}0 component in reciprocal-space representations of both, the Hartree and ionic, potentials are set to zero. This implies that considering the sum of the Hartree and ionic potentials is more meaningful to visualize than either potential individually.}}

{{TAG|WRT_POTENTIAL}} can be run as a post-processing step by restarting from a converged {{FILE|CHGCAR}} and setting {{TAG|ALGO}}=None. It is available for VASP >= 6.4.3.
## Options to select
### total
::
V_{\text{total}}(\mathbf{r}) + B_{\text{total}}(\mathbf{r}) = 
V_{\text{ionic}}(\mathbf{r}) + V_{\text{hartree}}(\mathbf{r})+
V_{\text{xc}}(\mathbf{r}) + B_{\text{xc}}(\mathbf{r})

::The output is written to /results/potential/total, as well as {{FILE|LOCPOT}}.
### hartree
::
V_{\text{hartree}}(\mathbf{r}) = \int \frac{n(\mathbf{r'})}{|\mathbf{r}-\mathbf{r'}|}d\mathbf{r'}

::The output is written to /results/potential/hartree.
### ionic
::V_{\text{ionic}}(\mathbf{r}) as mimicked by the pseudopotentials of the PAW method. The output is written to /results/potential/ionic.
### xc
::
V_{\text{xc}}(\mathbf{r}) + B_{\text{xc}}(\mathbf{r})
 as defined by the selected exchange-correlation functional. The output is written to /results/potential/xc.
{{NB|mind|This only corresponds to the (semi-)local functionals, i.e., LDA, GGA, non-local vdW-DF functionals, and does not account for either the potential \mu associated with the kinetic energy density in {{TAG|METAGGA}} or the nonlocal Fock exchange considered in hybrid functionals.|:}}
### xcmu
::
\mu_{\text{xc}}(\mathbf{r}) + \mathbf{\mu}_{m,\text{xc}}(\mathbf{r})
 is the scalar and magnetic contribution of the metaGGA potential associated to the kinetic-energy density as defined by the selected exchange-correlation functional. The output is written to /results/potential/xcmu.

::This option requires a \tau-dependent functional. If the selected exchange-correlation functional does not depend on the kinetic-energy density, VASP issues a warning and no xcmu dataset is written.

::xcmu is the potential as it enters the Hamiltonian, in units of eV \AA^2, and not the dimensionless functional derivative \partial e_{\text{xc}}/\partial\tau. The two differ by the factor \hbar^2/2m_e = 3.8100199 eV \AA^2 that turns the functional derivative into the coefficient multiplying \nabla in \nabla\cdot(\mu\nabla).
## Related tags and articles
{{TAG|LVACPOTAV}},
{{TAG|LVTOT}},
{{TAG|LVHAR}},
{{TAG|LDIPOL}},
{{TAG|ENCUT}}, {{TAG|NGXF}}, {{TAG|NGYF}}, {{TAG|NGZF}},
{{TAG|WRT_DENSITY}}

Category:INCAR tagCategory:ElectrostaticsCategory:Electronic ground-state propertiesCategory:Potential
