{{DISPLAYTITLE:ELPH_WF_REDISTRIBUTE}}
{{TAGDEF|ELPH_WF_REDISTRIBUTE|[logical]| .FALSE.}}

Description:  
After computing the electronic states, they are redistributed among the CPUs such that the workload to compute the electron self-energy is similar among the different CPUs.  
{{Available|6.5.0}}
----
The computational effort for each Kohn–Sham state is first estimated, and then the states are distributed among MPI ranks to balance the workload as evenly as possible.  This redistribution is most relevant when used in combination with {{TAG|ELPH_SELFEN_IMAG_SKIP|.TRUE.}}.
When {{TAG|ELPH_MODE|TRANDPORT}}, the default value is {{TAG|ELPH_WF_REDISTRIBUTE|.TRUE.}}.
## Related tags and articles
{{TAG|ELPH_MODE}},
{{TAG|ELPH_SELFEN_IMAG_SKIP}},
{{TAG|ELPH_RUN}},
{{TAG|ELPH_WF_COMM_OPT}},
{{TAG|ELPH_WF_CACHE_PREFILL}}

Category:INCAR tagCategory:Electron-phonon_interactions
