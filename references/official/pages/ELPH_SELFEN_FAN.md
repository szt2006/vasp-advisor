{{DISPLAYTITLE:ELPH_SELFEN_FAN}}
{{TAGDEF|ELPH_SELFEN_FAN|[logical]|.FALSE.}}

Description: Controls whether the Fan-Migdal contribution is included in the calculation of the phonon-induced electron self-energy.
{{Available|6.5.0}}

----

The phonon-induced electron self-energy has two contributions at second order in perturbation theory, the Fan-Migdal self-energy and the real-valued Debye-Waller self-energy.
{{TAG|ELPH_SELFEN_FAN}} controls the computation of the former, while the latter can be computed via {{TAG|ELPH_SELFEN_DW}}.

The result is reported individually for each self-energy accumulator in the {{FILE|vaspout.h5}} file as

/results/electron_phonon/electrons/self_energy_1/selfen_fan
## Related tags and articles
* Bandstructure renormalization
* Transport calculations
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_SELFEN_DW}}
* {{TAG|ELPH_SELFEN_STATIC}}

Category:INCAR tagCategory:Electron-phonon_interactions
