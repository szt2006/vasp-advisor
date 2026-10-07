{{DISPLAYTITLE:LIBMBD_TS_D}}
{{TAGDEF|LIBMBD_TS_D|[real]|20}}

Description: {{TAG|LIBMBD_TS_D}} sets the value of the damping parameter d in the Tkatchenko-Scheffler method{{cite|tkatchenko:prl:09}} as implemented in the library libMBD of many-body dispersion methods{{cite|libmbd_1}}{{cite|libmbd_2}}{{cite|hermann:jcp:2023}}.
----
{{TAG|LIBMBD_TS_D}} allows to choose the value of the damping parameter d in the Tkatchenko-Scheffler method{{cite|tkatchenko:prl:09}} as implemented in the library libMBD of many-body dispersion methods{{cite|libmbd_1}}{{cite|libmbd_2}}{{cite|hermann:jcp:2023}}. The value is internally passed to the libMBD input **ts_d** described at the page {{cite|libmbd_input}}. {{TAG|LIBMBD_TS_D}} is the same as the {{TAG|VDW_D}} tag that is used for the VASP implementation of the Tkatchenko-Scheffler method.
{{NB|mind| {{TAG|LIBMBD_TS_D}} can be set only if {{TAG|LIBMBD_XC}}{{=}}none.}}
{{NB|important| This feature is available from VASP.6.4.3 onwards that needs to be compiled with -DLIBMBD.}}
libMBD is a separate library package that has to be downloaded{{cite|libmbd_2}} and compiled before VASP is compiled with the corresponding precompiler options and links to the libraries.
## Related tags and articles
{{TAG|LIBMBD_METHOD}},
{{TAG|LIBMBD_XC}},
{{TAG|LIBMBD_TS_SR}},
Tkatchenko-Scheffler method

{{sc|LIBMBD_TS_D|Examples|Examples that use this tag}}
## References
----
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:van der Waals functionals
