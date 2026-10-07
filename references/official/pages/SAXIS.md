{{TAGDEF|SAXIS|[real array]| (0, 0, 1)}}

Description: Set the global spin-quantization axis w.r.t. Cartesian coordinates.
----
{{TAG|SAXIS}} specifies the relative orientation of spinor space spanned by the Pauli matrices \{\sigma_1, \sigma_2, \mathbf{\sigma}_3\} with respect to Cartesian coordinates \{\hat x, \hat y, \hat z\} . The default is  \sigma_1=\hat x, \sigma_2 =\hat y, \sigma_3 = \hat z.
The direction of the spin-quantization axis \sigma_3 with respect to Cartesian coordinates is set

  {{TAG|SAXIS}} =   sx sy sz    ! global spin-quantization axis
such that \sigma_3=\mathbf{s}/|\mathbf{s}|, i.e., \sigma_3 points along \mathbf{s}=(s_x,s_y,s_z)^T. The directions of \sigma_1 and \sigma_2 are a consequence of rotating \sigma_3 to point along \mathbf{s} as described below. 

The relative orientation of spinor space with respect to real space becomes important in case spin-orbit coupling is included ({{TAG|LSORBIT}}=True). All magnetic moments and spinor-like quantities written or read by VASP are given in the basis of the spinor space \{\sigma_1, \sigma_2, \mathbf{\sigma}_3\}. This includes the {{TAG|MAGMOM}} tag in the {{FILE|INCAR}} file, the total and local magnetizations in the {{FILE|OUTCAR}} and {{FILE|PROCAR}} file, the spinor-like orbitals in the {{TAG|WAVECAR}} file, and the magnetization density in the {{FILE|CHGCAR}} file.
{{NB|warning|**SAXIS** &ne; 0 0 1, is not supported for Hartree-Fock calculations and hybrid functionals (**LHFCALC** {{=}} .TRUE.)! These methods set **ISYM** {{=}} 3, which only works with the default **SAXIS**. You can still use **SAXIS** with **ISYM** {{=}} -1., but in most cases it is computationally more efficient to change **MAGMOM** instead.}}
## Coordinate system
[[File:Saxis-angles.png|300px|thumb|Fig 1. Euler angles \alpha and  \beta defined by \mathbf{s}=(s_x,s_y,s_z)^T.]]

The default orientation is \sigma_1=\hat x, \sigma_2 =\hat y, \sigma_3 = \hat z. 
To set \hat{\sigma}_3=s/|s|, VASP applies two rotations with Euler angles

:
\begin{align}
\alpha&=\arctan2\left(\frac{s_y}{s_x}\right) \in [-\pi,\pi]\\
\beta&=\arctan2\left(\frac{\sqrt{s_x^2+s_y^2}}{s_z}\right) \in [0,\pi].
\end{align}

Here, \alpha is the angle between the projection of {{TAG|SAXIS}} onto the *xy* plane (sx,sy,0) and the Cartesian vector \hat x, and \beta is the angle between the vector {{TAG|SAXIS}} and the Cartesian vector \hat z, see Fig. 1. Search for `Euler angles` in the {{FILE|OUTCAR}} file to see what VASP uses. For the default \mathbf{s}=(0,0,1), \alpha=0 and \beta=0.

The transformation of a vector \mathbf{m}=(m_1,m_2,m_3)^T given in the basis \{\sigma_1, \sigma_2, \mathbf{\sigma}_3\} into \mathbf{m}'=(m_x,m_y,m_z)^T in Cartesian coordinates and its inverse transformation read
:
\begin{align}
\mathbf{m}&= m_1 \sigma_1 + m_2 \sigma_2 + m_3 \sigma_3 \\
\mathbf{m}'&= m_x \hat x + m_y \hat y + m_z \hat z \\
\mathbf{m}'&= R_z^\alpha R_y^\beta \mathbf{m} \\
\mathbf{m} &=  R_y^{-\beta} R_z^{-\alpha} \mathbf{m}' \\
\end{align}

where the rotation matrices are
:
R_z^\alpha = \left(\begin{matrix}
  \cos(\alpha) & -\sin(\alpha) & 0 \\
  \sin(\alpha) & \cos(\alpha)  & 0 \\
         0     & 0             & 1 \\
 \end{matrix}\right), \quad
R_y^\beta = \left(\begin{matrix}
  \cos(\beta)  &  0 & \sin(\beta) \\
       0       &  1 &    0        \\
  -\sin(\beta) &  0 & \cos(\beta) \\
 \end{matrix}\right).

{{NB|mind|Apply the proper basis transformation when comparing vector-like quantities and spinor-like quantities.|}}
For instance, when {{TAG|LORBMOM}}=True the orbital angular momentum is written to the {{FILE|OUTCAR}} file in Cartesian coordinates. Thus, when comparing the orbital angular momentum (vector-like quantity) and the magnetization (spinor-like quantity), one has to perform a basis transformation on one of the quantities unless the bases agree (default).
## Example
* In case the bases have the same orientation, i.e., \sigma_1=\hat x, \sigma_2 =\hat y, \sigma_3 = \hat z (default)

:
\begin{align}
m_x & = & m_1, \\ 
m_y & = & m_2, \\ 
m_z & = & m_3. 
\end{align}

:For a single site this implies setting

 {{TAG|MAGMOM}} = mx my mz ! magnetic moment in Cartesian coordinates
 {{TAG|SAXIS}} =  0 0 1   ! default

[[File:Spinor-space-example-saxis.png|300px|thumb|Fig 2. Example with \mathbf{s}=(1,1,0)^T and Euler angles \alpha=\pi/4 and \beta=\pi/2.]]

* Another good choice is setting \mathbf{s} to point along the direction of the on-site magnetic moment such that 

:
\begin{align}
m_x & = & \sin(\beta)\cos(\alpha) m &= m\, s_x / \sqrt{s_x^2+s_y^2+s_z^2} \\
m_y & = & \sin(\beta)\sin(\alpha) m &= m\, s_y / \sqrt{s_x^2+s_y^2+s_z^2} \\
m_z & = & \cos(\beta) m &= m\, s_z / \sqrt{s_x^2+s_y^2+s_z^2},
\end{align}

:where m is the total on-site magnetic moment.
:For a single site, this case implies setting

 {{TAG|MAGMOM}} = 0 0 m   ! magnetic moment along sigma3
 {{TAG|SAXIS}} =  sx sy sz ! direction of sigma3
:Thus, there are two methods to rotate the initial magnetization in an arbitrary direction: either by changing the initial magnetic moments {{TAG|MAGMOM}} or by changing {{TAG|SAXIS}}. Both methods should, in principle, yield exactly the same energy, but for implementation reasons, the second method might be more precise. 

* In case 

 {{TAG|SAXIS}} =  1 1 0   ! alpha=pi/4, beta=pi/2
:the spinor space \{\sigma_1, \sigma_2, \mathbf{\sigma}_3\} will be rotated with respect to real space \{\hat x, \hat y, \hat z\}  as shown in Fig. 2.
## Related tags and articles
{{TAG|LNONCOLLINEAR}},
{{TAG|MAGMOM}},
{{TAG|LSORBIT}}

{{sc|SAXIS|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:MagnetismCategory:Noncollinear magnetismCategory:Spin-orbit coupling
