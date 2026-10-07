{{TAGDEF|LWANNIER90|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LWANNIER90}}=.TRUE. switches on the interface between VASP and WANNIER90 (http://www.wannier.org).

**N.B.**: This feature is only present if VASP is compiled with -DVASP2WANNIER90 or -DVASP2WANNIER90v2.
----

For {{TAG|LWANNIER90}}=.TRUE., VASP will write the input files for a WANNIER90 run: **wannier90.win**, **wannier90.mmn**, **wannier90.eig**, **wannier90.amn**, and if {{TAG|LWRITE_UNK}}=.TRUE. **wannier90.UNKp.s**. This is done by running wannier_setup in library mode as described in Chapter 6 of the WANNIER90 manual (http://www.wannier.org/doc/user_guide.pdf). For documentation of these files and tags therein, please refer to the WANNIER90 manual (http://www.wannier.org/doc/user_guide.pdf).

The following cases may occur:

* If **wannier90.win** does not exist, VASP will write the following template

 num_wann = {{TAG|NBANDS}}
 
 begin unit_cell_cart
   ... ... ...
   ... ... ...
   ... ... ...
 end unit_cell_cart
 
 begin atoms_cart
    ... ... ...
    ... ... ...
    ... ... ...
    ... ... ...  
 end atoms_cart
 
 mp_grid = .. .. ..
 
 begin kpoints
    ... ... ...
    ... ... ...
    ... ... ...
    ... ... ...
 end kpoints
:Here, the unit_cell_cart, atoms_cart, and kpoints blocks, and mp_grid array, will be set in accordance with the setup of the VASP calculation. This basically corresponds to the information given in the {{FILE|POSCAR}} and {{FILE|KPOINTS}} files. 
* If the **wannier90.win** file already exists, VASP will only add the aforementioned information if it is not already present. This means that VASP will check, for instance, whether or not the **wannier90.win** file contains a kpoints block, and add one if not. **Mind**: If it finds a kpoints block, VASP will not check whether this block agrees with the k points used in the VASP calculation!

The user may create a **wannier90.win** file prior to running VASP with {{TAG|LWANNIER90}}=.TRUE., and specify any tag and/or block that is understood by wannier_setup and/or wannier_run. For instance, one can specify the projections block in the **wannier90.win** file that controls the initial guess for the maximally localized Wannier functions.
Then, VASP writes the projections of the Bloch functions onto the relevant projectors to the **wannier90.amn** file. See Chapter 3 of the WANNIER90 manual (http://www.wannier.org/doc/user_guide.pdf) for more information.
## Related tags and articles
{{TAG|LWRITE_UNK}},
{{TAG|LWRITE_MMN_AMN}},
{{TAG|LWRITE_SPN}},
{{TAG|LWANNIER90_RUN}},
{{TAG|NUM_WANN}},
{{TAG|WANNIER90_WIN}}

{{sc|LWANNIER90|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Wannier functionsCategory:Constrained-random-phase approximation
