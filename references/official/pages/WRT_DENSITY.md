{{DISPLAYTITLE:WRT_DENSITY}}
{{TAGDEF|WRT_DENSITY|string|None}}

Description: Select which densities associated to the local potential are written as a post-processing step.
----
{{TAG|WRT_DENSITY}} can select one or multiple densities on the real-space grid in the unit cell to be written, e.g.,
  {{TAGBL|WRT_DENSITY}} = gradient
or
  {{TAGBL|WRT_DENSITY}} = density gradient laplacian
It writes the augmented total (core + valence) pseudo densities (charge and magnetization, their gradient, and their laplacian) that enter the XC functional on the plane-wave grid to {{FILE|vaspout.h5}} in VASP units. That is \AA^{-3} for charge and \mu_B for the magnetization. Correspondingly,  \AA^{-4} for the gradient, etc. 

With {{TAG|LWRT_AUGMENTED_DENSITY|F}} the densities can be written without augmentation (compensation charge=0). Mind that the augmented densities are still used during electronic minimization to evaluate the XC functional (unlike for the MGGA specific tag {{TAG|LNOAUGXC}}).

The output is written to {{FILE|vaspout.h5}} and can be accessed by HDF5 command-line tools (h5ls, h5dump).
  h5ls -r vaspout.h5
The above shows the table of contents of {{FILE|vaspout.h5}}. Depending on the keywords specified with {{TAG|WRT_DENSITY}} and the system it yields
  /results/gradient        Group
  /results/gradient/grid   Dataset {3}
  /results/gradient/structure Group
  /results/gradient/structure/position Group
  /results/gradient/structure/position/direct_coordinates Dataset {SCALAR}
  /results/gradient/structure/position/ion_sha256 Dataset {1}
  /results/gradient/structure/position/ion_types Dataset {1}
  /results/gradient/structure/position/lattice_vectors Dataset {3, 3}
  /results/gradient/structure/position/number_ion_types Dataset {1}
  /results/gradient/structure/position/position_ions Dataset {1, 3}
  /results/gradient/structure/position/scale Dataset {SCALAR}
  /results/gradient/structure/position/system Dataset {SCALAR}
  /results/gradient/values Dataset {12, 20, 20, 20}
The grid density can be increased by choosing a higher value for {{TAG|ENCUT}} or explicitly by {{TAG|NGXF}}, {{TAG|NGYF}}, {{TAG|NGZF}}.

The first dimension of the datasets in /results/charge_density is 1 for nonmagnetic calculation, 2 for spin-polarized calculation, and 4 for noncollinear calculations. For the datasets in /results/gradient the first dimension is multiplied by three to account for the three Cartesian directions. The components for the magnetic calculations correspond to the spinor representation with the scalar part in the first component and the magnetic part in the second ({{TAG|ISPIN}}=2) or m_1, m_2 and m_3 in the 2nd, 3rd and 4th component ({{TAG|LNONCOLLINEAR}}=T) in the basis of Pauli matrices \{\sigma_1, \sigma_2, \mathbf{\sigma}_3\} given by {{TAG|SAXIS}}.
{{Available|6.6.0}}
## Related tags and articles
{{TAG|WRT_POTENTIAL}},
{{TAG|ENCUT}}, {{TAG|NGXF}}, {{TAG|NGYF}}, {{TAG|NGZF}}

{{sc|WRT_DENSITY|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:Charge densityCategory:Electronic ground-state properties
