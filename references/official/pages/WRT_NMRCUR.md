{{DISPLAYTITLE:WRT_NMRCUR}}
{{TAGDEF|WRT_NMRCUR|0 {{!}} 1 {{!}} 2 {{!}} 3 {{!}} 4| 0 }}

Description: Allows to write the NMR current response in atomic units to file.
{{Available|6.6.0}}
----
In conjunction with {{TAG|LCHIMAG|True}}, {{TAG|WRT_NMRCUR}} allows to write the current response on the fine grid {{TAG|NGXF}} x {{TAG|NGYF}} x {{TAG|NGZF}} in atomic units (hartree bohr^{-2}) to an external magnetic field within linear response NMR. 
{{NB|important|The fine FFT grid is only the plane-wave contribution to the current response; the one-center diamagnetic and paramagnetic contributions are calculated on radial grids and not the fine FFT grid. This does not affect the chemical shieldings, which include the contribution from all three parts.}}
The output is written to {{FILE|NMRCURBX}}, {{FILE|NMRCURBY}}, and/or {{FILE|NMRCURBZ}} depending on the selected direction of the perturbing \mathbf{B} field:

* {{TAG|WRT_NMRCUR|0}}: no current response written to file (default)
* {{TAG|WRT_NMRCUR|1}}: B_x
* {{TAG|WRT_NMRCUR|2}}: B_y
* {{TAG|WRT_NMRCUR|3}}: B_z
* {{TAG|WRT_NMRCUR|4}}: all three directions of \mathbf{B}=(B_x,B_y,B_z)^T

It is also written to {{FILE|vaspout.h5}}, if compiled with HDF5 support. You can find the data groups

  /results/nmrcurbx        Group
  /results/nmrcurbx/grid   Dataset {3}
  /results/nmrcurbx/structure Group
  /results/nmrcurbx/structure/position Group
  /results/nmrcurbx/structure/position/direct_coordinates Dataset {SCALAR} 
  /results/nmrcurbx/structure/position/ion_sha256 Dataset {1}
  /results/nmrcurbx/structure/position/ion_types Dataset {1}
  /results/nmrcurbx/structure/position/lattice_vectors Dataset {3, 3}
  /results/nmrcurbx/structure/position/number_ion_types Dataset {1}
  /results/nmrcurbx/structure/position/position_ions Dataset {2, 3}
  /results/nmrcurbx/structure/position/scale Dataset {SCALAR}
  /results/nmrcurbx/structure/position/system Dataset {SCALAR}
  /results/nmrcurbx/values Dataset {3, 24, 24, 24}

and use {{py4vasp}} to access these, e.g., using 

import py4vasp as pv
calc = pv.Calculation.from_path(".")
calc.current_density.to_contour("NMR(x)", a=0.5) + calc.current_density.to_quiver("NMR(x)", a=0.5)

to select the current response triggered by B_x. It will result in a contour plot showing the magnitude of the current density and a quiver plot with the projected current in the selected plane. The plane is selected as a fraction x of the lattice vector. Here, x=0.5 along \mathbf{a}. For the other lattice vectors use b=x or c=x.
{{NB|warning|For bulk calculations you must switch off the use of symmetry. In other words, set {{TAG|ISYM|0|op=<=}} if there is more than a single k point at zero (the Γ point).}}
{{NB|tip|Consider switching on current augmentation ({{TAG| LLRAUG|True}}).}}
## Related tags and articles
{{TAG|LCHIMAG}}, {{TAG|LLRAUG}}, {{FILE|NMRCURBX}}

Category:INCAR tagCategory:NMR
