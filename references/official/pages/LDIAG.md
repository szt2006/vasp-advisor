{{TAGDEF|LDIAG|[logical]|.TRUE.}}

Description: Determines whether a subspace diagonalization is performed within the algorithm selected by {{TAG|ALGO}} or {{TAG|IALGO}}.
----
For {{TAG|ALGO}} = Normal, Fast, and VeryFast, VASP performs a diagonalization in the subspace spanned by all orbitals. This is often referred to as the Rayleigh–Ritz method (https://en.wikipedia.org/wiki/Rayleigh%E2%80%93Ritz_method). 
This step increases the convergence rate and thus is expedient in most cases.
Furthermore, the subspace diagonalization sorts the orbital/eigenvalues in ascending order.

For the direct optimization algorithms (for instance {{TAG|ALGO}} = All or Damped),
a subspace diagonalization is usually not performed, but in order to improve the accuracy of the calculated forces,
after convergence has been reached one single diagonalization in the subspace spanned by all orbitals is performed.

For {{TAG|ALGO}} = VeryFast and Damped it is possible to switch off the subspace diagonalization by specifying {{TAG|LDIAG}} = .FALSE. in the {{FILE|INCAR}} file.
Specifically, for {{TAG|ALGO}} = VeryFast, {{TAG|LDIAG}} = .FALSE. changes from an exact Rayleigh–Ritz diagonalization to Loewdin perturbation theory.

Note, Loewdin perturbation theory strictly conserves the orbital order, *i.e.*, the *n*-th orbital will remain stored in the *n*-th storage slot and only small rotations into that orbital can occur.
For {{TAG|ALGO}} = Damped and All, the final subspace diagonalization is simply skipped if {{TAG|LDIAG}} = .FALSE. is set.
Generally using {{TAG|LDIAG}} = .FALSE. is only advised, if one wants to maintain a certain orbital order, for instance, when reading the orbitals from an existing {{FILE|WAVECAR}} file.

For the algorithms {{TAG|ALGO}} = Normal or Fast, by construction it is not possible to switch off subspace diagonalization, as these algorithms require subspace diagonalizations during the iterative refinement of the orbitals.
Furthermore, algorithms that minimize the total energy ({{TAG|ALGO}} = All) are often too "greedy" and tend to alternate the orbital order in the course of the SCF cycle and energy optimization.  

In summary, the following combinations are potentially useful: 

 ALGO = VeryFast ; LDIAG = .FALSE.

 ALGO = Damped ; LDIAG = .FALSE.

Other combinations using {{TAG|LDIAG}} = .FALSE. are likely to yield undesirable results.
{{NB|warning| {{TAG|ALGO}} {{=}} VeryFast is not supported for hybrid functionals. }}
## Related tags and articles
{{TAG|IALGO}},
{{TAG|ALGO}}

{{sc|LDIAG|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Electronic minimization
