{{DISPLAYTITLE:ELPH_SELFEN_NW}}
{{TAGDEF|ELPH_SELFEN_NW|[integer]|1}}

Description: Number of energies to use when computing the phonon-induced electron self-energy.
{{Available|6.5.0}}

----

The electron self-energy, \Sigma_{n \mathbf{k}}(\omega), depends on the frequency \omega (or energy \hbar \omega).
{{TAG|ELPH_SELFEN_NW}} controls the number and location of frequencies when computing the self-energy in the following way:
; {{TAG|ELPH_SELFEN_NW|0|op=>}}
: The self-energy is computed at {{TAG|ELPH_SELFEN_NW}} equally spaced energies between \varepsilon_{n \mathbf{k}} - \frac{1}{2} E^{\text{W}} and \varepsilon_{n \mathbf{k}} + \frac{1}{2} E^{\text{W}}. The interval is centered around each Kohn-Sham eigenvalue, \varepsilon_{n \mathbf{k}}, and its width, E^{\text{W}}, is controlled via {{TAG|ELPH_SELFEN_WRANGE}}. If {{TAG|ELPH_SELFEN_NW}} is an even number, it is automatically increased by one so that the center-most energy in each interval always coincides with the corresponding Kohn-Sham eigenvalue.
; {{TAG|ELPH_SELFEN_NW|0|op=<}}
: The self-energy is computed at |{{TAG|ELPH_SELFEN_NW}}| equally spaced energies between \varepsilon^{\text{min}}_{\mathbf{k}} - \frac{1}{2} E^{\text{W}} and \varepsilon^{\text{max}}_{\mathbf{k}} + \frac{1}{2} E^{\text{W}}, where \varepsilon^{\text{min}}_{\mathbf{k}} and \varepsilon^{\text{max}}_{\mathbf{k}} are the minimum and maximum Kohn-Sham eigenvalues of the calculation, respectively. Once again, E^{\text{W}} is controlled via {{TAG|ELPH_SELFEN_WRANGE}} and allows to extend the interval in both directions.
## Related tags and articles
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_SELFEN_FAN}}
* {{TAG|ELPH_SELFEN_DW}}
* {{TAG|ELPH_SELFEN_WRANGE}}

Category:INCAR tagCategory:Electron-phonon_interactions
