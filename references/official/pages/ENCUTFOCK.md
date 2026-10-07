{{TAGDEF|ENCUTFOCK|[real]}}

Default: none

Description: The {{TAG|ENCUTFOCK}} tag sets the energy cutoff that determines the FFT grids used by the Hartree-Fock routines.
----

The flag {{TAG|ENCUTFOCK}} is no longer supported in VASP.5.2.4 and newer versions.
Please use {{TAG|PRECFOCK}} instead.

The only sensible value for {{TAG|ENCUTFOCK}} is {{TAG|ENCUTFOCK}}=0.
This implies that the smallest possible FFT grid, which just encloses the cutoff sphere
corresponding to the plane wave cutoff, is used. 
This accelerates the calculations by roughly a factor two to three,
but causes slight changes in the total energies and  some noise in the calculated forces.
The FFT grid used internally in the exact exchange (Hartree-Fock) routines
is written to the {{TAG|OUTCAR}} file. Simply search for lines starting with

 FFT grid for exact exchange (Hartree Fock)

In many cases, a sensible approach is to determine the electronic and ionic groundstate 
using {{TAG|ENCUTFOCK}}=0, and to make one final total energy calculation
without the flag {{TAG|ENCUTFOCK}}.
## Related tags and articles
{{TAG|PRECFOCK}},
{{TAG|PREC}},
{{TAG|ENCUT}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|ENCUTFOCK|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
