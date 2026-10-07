{{DISPLAYTITLE:ELPH_WF_CACHE_PREFILL}}
{{TAGDEF|ELPH_WF_CACHE_PREFILL|logical|.TRUE.}}

Description: Pre-fills the wavefunction cache before the main electron-phonon loop begins.
{{Available|6.5.0}}
----

When computing electron-phonon matrix elements, VASP caches wavefunctions fetched from remote MPI ranks (see {{TAG|ELPH_WF_CACHE_MB}}). With ELPH_WF_CACHE_PREFILL = .TRUE. (the default), all required wavefunctions are gathered into the cache in a single communication phase before the main loop starts. This means the loop itself runs with little or no inter-rank MPI traffic.

Setting ELPH_WF_CACHE_PREFILL = .FALSE. disables pre-filling; wavefunctions are then fetched on demand during the loop. This reduces the upfront communication cost but increases total MPI traffic and is generally slower.
## Related tags and articles
* {{TAG|ELPH_WF_CACHE_MB}}
* {{TAG|ELPH_WF_REDISTRIBUTE}}
* {{TAG|ELPH_WF_COMM_OPT}}
Category:INCAR tagCategory:Electron-phonon_interactions
