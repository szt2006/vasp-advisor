{{DISPLAYTITLE:NUM_WANN}}
{{TAGDEF|NUM_WANN|[integer]|{{TAG|NBANDS}}}}

Description: Controls the number of Wannier orbitals to be constructed.

----

This tag is used to determine the number of Wannier orbitals to be constructed in the SCDM method.

Since VASP 6.2.0, {{TAG|NUM_WANN}} also determines the number of Wannier orbitals to be used with wannier90.
Note that the num_wann value written to the wannier90.win file is always the value of {{TAG|NUM_WANN}} known by vasp.

When using {{TAG|LOCPROJ}} for Wannierization, it is not necessary to set {{TAG|NUM_WANN}}.
In this case, the number of Wannier orbitals is automatically set equal to the number of local functions.
## Related tags and articles
{{TAG|LWANNIER90}},
{{TAG|LSCDM}},
{{TAG|CUTOFF_TYPE}}
----

Category:INCAR tagCategory:Wannier functionsCategory:Constrained-random-phase approximation
