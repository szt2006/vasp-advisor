{{DISPLAYTITLE:LIBMBD_METHOD}}
{{TAGDEF|LIBMBD_METHOD|[string]|mbd-rsscs (default in libMBD)}}

Description: {{TAG|LIBMBD_METHOD}} selects one of the methods available in the library libMBD of many-body dispersion methods{{cite|libmbd_1}}{{cite|libmbd_2}}{{cite|hermann:jcp:2023}}. Only used when {{TAG|IVDW|14}}.
----
{{TAG|LIBMBD_METHOD}} can be set to a label (string) corresponding to one of the methods listed on the libMBD website (see **method** at the page {{cite|libmbd_input}}).
{{NB|mind| Note that the use of the mbd-nl method{{cite|hermann:prl:2020}} is currently not possible, since the associated atomic polarizabilities and semilocal functional are currently not implemented in VASP.}}
{{NB|important| This feature is available from VASP.6.4.3 onwards that needs to be compiled with -DLIBMBD.}}
{{NB|warning|
*There is a severe bug in VASP.6.5.1 and previous versions: during a geometry relaxation, the new atomic positions and cell parameters are not passed to libMBD. See known issue 55 for a patch.
*It is recommended to compile libMBD without ScaLAPACK/MPI, otherwise nudged elastic bands (NEB) calculations will not run properly and produce wrong results.}}
libMBD is a separate library package that has to be downloaded{{cite|libmbd_2}} and compiled before VASP is compiled with the corresponding precompiler options and links to the libraries.
## Related tags and articles
{{TAG|LIBMBD_XC}},
{{TAG|LIBMBD_TS_D}},
{{TAG|LIBMBD_TS_SR}},
{{TAG|LIBMBD_MBD_A}},
{{TAG|LIBMBD_MBD_BETA}},
{{TAG|LIBMBD_VDW_PARAMS_KIND}},
{{TAG|LIBMBD_ALPHA}},
{{TAG|LIBMBD_C6AU}},
{{TAG|LIBMBD_R0AU}},
{{TAG|LIBMBD_N_OMEGA_GRID}},
{{TAG|LIBMBD_K_GRID}},
{{TAG|LIBMBD_K_GRID_SHIFT}},
{{TAG|LIBMBD_PARALLEL_MODE}},
Tkatchenko-Scheffler method,
Many-body dispersion energy

{{sc|LIBMBD_METHOD|Examples|Examples that use this tag}}
## References
----
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:van der Waals functionals
