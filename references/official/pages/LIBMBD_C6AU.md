{{DISPLAYTITLE:LIBMBD_C6AU}}
{{TAGDEF|LIBMBD_C6AU|[real array]}}

Description: {{TAG|LIBMBD_C6AU}} defines the free-atom C_6 parameters (\mathrm{Hartree} \mathrm{bohr}^{6}) used in the Tkatchenko-Scheffler and Many-body dispersion energy methods as implemented in the library libMBD of many-body dispersion methods{{cite|libmbd_1}}{{cite|libmbd_2}}{{cite|hermann:jcp:2023}}.
----
{{TAG|LIBMBD_C6AU}} allows to set values for the free-atom C_6 parameters (\mathrm{Hartree} \mathrm{bohr}^{6}) used in the Tkatchenko-Scheffler and Many-body dispersion energy methods as implemented in the library libMBD of many-body dispersion methods{{cite|libmbd_1}}{{cite|libmbd_2}}{{cite|hermann:jcp:2023}}. For each atom listed in the {{TAG|POSCAR}} file, a value has to be provided. The values are internally passed to the second column of the libMBD input **free_values** described at the page {{cite|libmbd_input}}.
{{NB|important| This feature is available from VASP.6.4.3 onwards that needs to be compiled with -DLIBMBD.}}
libMBD is a separate library package that has to be downloaded{{cite|libmbd_2}} and compiled before VASP is compiled with the corresponding precompiler options and links to the libraries.
## Related tags and articles
{{TAG|LIBMBD_METHOD}},
{{TAG|LIBMBD_ALPHA}},
{{TAG|LIBMBD_R0AU}},
Tkatchenko-Scheffler,
Many-body dispersion energy

{{sc|LIBMBD_C6AU|Examples|Examples that use this tag}}
## References
----
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:van der Waals functionals
