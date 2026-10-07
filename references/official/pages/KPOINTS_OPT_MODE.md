{{DISPLAYTITLE:KPOINTS_OPT_MODE}}
{{TAGDEF|KPOINTS_OPT_MODE|0 {{!}} 1 {{!}} 2|1}}

Description: Selects which diagonalization algorithm to use for the optional k-points driver
{{Available|6.5.0}}
----

Sometimes, the electronic Kohn-Sham orbitals are required on an alternative k-point mesh, for example via {{FILE|KPOINTS_OPT}} or {{FILE|KPOINTS_ELPH}}.
In this case, the tag {{TAG|KPOINTS_OPT_MODE}} selects which diagonalization algorithm should be used to obtain these eigenvalues.
## Tag options
;{{TAG|KPOINTS_OPT_MODE|0}}
:The diagonalization of the Hamiltonian at the alternative k-points is skipped entirely
;{{TAG|KPOINTS_OPT_MODE|1}}
:Uses the Blocked-Davidson algorithm (same as {{TAG|ALGO|Normal}})
;{{TAG|KPOINTS_OPT_MODE|2}}
:Performs an exact diagonalization (same as {{TAG|ALGO|Exact}})
## Related tags and articles
* {{FILE|KPOINTS_OPT}}
* {{FILE|KPOINTS_ELPH}}
* {{TAG|ALGO}}

Category:INCAR tagCategory:Electron-phonon_interactionsCategory:Electronic minimization
