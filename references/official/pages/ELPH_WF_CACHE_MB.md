{{DISPLAYTITLE:ELPH_WF_CACHE_MB}}
{{TAGDEF|ELPH_WF_CACHE_MB|real|1000}}

Description: Maximum memory (in MB) allocated for caching wavefunctions during electron-phonon matrix element calculations.
{{Available|6.5.1}}
----

Electron-phonon matrix elements are sandwiches of the form
:\langle \psi_{n\mathbf{k}} | \Delta V_{\mathbf{q}} | \psi_{m\mathbf{k}'} \rangle,
where \mathbf{k}' = \mathbf{k} + \mathbf{q}. Because k-points are distributed across MPI ranks, the wavefunction \psi_{n\mathbf{k}} needed to form the bra may reside on a different rank than the one computing the matrix element. {{TAG|ELPH_WF_CACHE_MB}} sets the maximum memory (in megabytes) used to cache these remotely fetched wavefunctions locally, avoiding repeated inter-rank MPI communication.

A separate cache for the PAW projections is also sized proportionally to {{TAG|ELPH_WF_CACHE_MB}}.

The wavefunction cache works together with {{TAG|ELPH_WF_CACHE_PREFILL}} (default: .TRUE.), which pre-populates the cache before the main electron-phonon loop begins. When pre-fill succeeds, almost all subsequent wavefunction accesses are served from the cache without MPI communication.
## Related tags and articles
* {{TAG|ELPH_WF_CACHE_PREFILL}}
* {{TAG|ELPH_WF_COMM_OPT}}
* {{TAG|ELPH_WF_REDISTRIBUTE}}
* {{TAG|ELPH_RUN}}

Category:INCAR tagCategory:Electron-phonon interactions
