{{DISPLAYTITLE:KPOINT_BSE}}
{{TAGDEF|KPOINT_BSE|[integer] (optionally [integer],[integer],[integer])}}

Description: {{TAG|KPOINT_BSE}}  specifies the k-point index at which VASP calculates the dielectric matrix.
----
In the simplest form, one can specify

  KPOINT_BSE = index_of_k-point

Select the desired k point from the list of k points in the {{TAG|OUTCAR}} file. Additionally, a shift by an arbitrary reciprocal lattice vector can be supplied by specifying three additional integer numbers:

  KPOINT_BSE = index_of_k-point  n1 n2 n3

This allows calculating the dielectric function at a k point outside of the first Brillouin zone corresponding to

: \mathbf{k} + n_{1} \mathbf{b}_{1}+ n_{2} \mathbf{b}_{2} + n_{3} \mathbf{b}_{3} 

where \mathbf{b}_{i} are the reciprocal-lattice vectors of the unit cell.
{{NB|warning|We strongly recommend using {{TAG|ANTIRES}}{{=}}2 for the finite wavevector calculations. The Tamm-Dancoff approximation can lead to unphysical results for the dielectric function at a finite wavevector.|}}
## Related tags and articles
BSE calculations, 

{{sc|KPOINT_BSE|HowTo|Workflows that use this tag}}

Category:INCAR tagCategory:Many-body perturbation theoryCategory:Bethe-Salpeter equations
