{{TAGDEF|LCALCEPS|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: for {{TAG|LCALCEPS}}=.TRUE. the macroscopic ion-clamped static dielectric tensor, Born effective charge tensors, and the ion-clamped piezoelectric tensor of the system are determined from the response to finite electric fields.
----
For {{TAG|LCALCEPS}}=.TRUE., VASP calculates the ion-clamped static dielectric tensor

:
\epsilon^\infty_{ij}=\delta_{ij}+
\frac{4\pi}{\epsilon_0}\frac{\partial P_i}{\partial \mathcal{E}_j},
\qquad
{i,j=x,y,z}

the Born effective charge tensors

:
Z^*_{ij}=\frac{\Omega}{e}\frac{\partial P_i}{\partial u_j}
        =\frac{1}{e}\frac{\partial F_j}{\partial \mathcal{E}_i},
\qquad
{i,j=x,y,z}

and the ion-clamped piezoelectric tensor of the system

:
e^{(0)}_{ij}=-\frac{\partial \sigma_i}{\partial \mathcal{E}_j},
\qquad
{i=xx, yy, zz, xy, yz, zx}\quad{j=x,y,z}

from the self-consistent response to a finite electric field *&epsilon;*.
In this case, the "response" of the system is the change in the polarization **P**, the Hellmann-Feynman forces **F**, and the stress tensor &sigma;. Mind the definition/sign convention of the stress tensor.

If this is combined with {{TAG|IBRION}}=6, the contribution from the ionic relaxations to the piezoelectric and dielectric tensors are calculated as well.

To this end VASP will perform essentially three successive calculations, with: 

 {{TAG|EFIELD_PEAD}}= *&epsilon;*x 0 0

 {{TAG|EFIELD_PEAD}}= 0 *&epsilon;*y 0

 {{TAG|EFIELD_PEAD}}= 0 0 *&epsilon;*z 

where, by default, VASP chooses *&epsilon;*x=*&epsilon;*y=*&epsilon;*z=0.01 eV/&Aring;.

This default may be overwritten by specifying

 {{TAG|EFIELD_PEAD}}= *&epsilon;*x *&epsilon;*y *&epsilon;*z

in the {{FILE|INCAR}} file.

The relevant output is found in the {{FILE|OUTCAR}} file, immediately following the lines (see the description of {{TAG|LEPSILON}}=.TRUE. as well):

 MACROSCOPIC STATIC DIELECTRIC TENSOR (including local field effects) 

 BORN EFFECTIVE CHARGES (including local field effects) 

 PIEZOELECTRIC TENSOR (including local field effects) 

In the above, "including local field effects" pertains to the fact that changes in the orbitals due to the electric field induce changes in the Hartree- and exchange-correlation potential. One may choose to limit this to changes in the Hartree potential alone, by specifying:

 {{TAG|LRPA}}=.TRUE.

This is commonly referred to as the response within the "Random Phase Approximation" (RPA), or the "neglect of local field effects". The OUTCAR file will now contain additional sections, headed by the lines: 

 MACROSCOPIC STATIC DIELECTRIC TENSOR (excluding local field effects) 

 BORN EFFECTIVE CHARGES (excluding local field effects) 

 PIEZOELECTRIC TENSOR (excluding local field effects)

----
{{NB|important|For standard DFT functionals, &epsilon;&infin;, *Z**, and *e*(0) may be more easily calculated from density functional perturbation theory (see {{TAG|LEPSILON|.TRUE.}}). For functionals that depend not only on the density but also explicitly on the orbitals, like hybrid functionals, density functional perturbation theory is presently not implemented and {{TAG|LEPSILON|.TRUE.}} is not applicable.}}
{{NB|warning|The piezoelectric tensor has the wrong sign in Vasp 5.4.4 and older. The bug is fixed with patch.5.4.4.16052018.gz (http://cms.mpi.univie.ac.at/patches/patch.5.4.4.16052018.gz).}}
## Related tags and articles
{{TAG|LEPSILON}},
{{TAG|LCALCPOL}},
{{TAG|EFIELD_PEAD}},
{{TAG|LPEAD}},
{{TAG|IPEAD}},
{{TAG|LBERRY}},
{{TAG|IGPAR}},
{{TAG|NPPSTR}},
{{TAG|DIPOL}},
{{TAG|IBRION}},
Berry phases and finite electric fields

{{sc|LCALCEPS|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Linear responseCategory:Dielectric propertiesCategory:Berry phasesCategory:Howto
