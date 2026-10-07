{{DISPLAYTITLE:ELPH_SCATTERING_APPROX}}
{{TAGDEF|ELPH_SCATTERING_APPROX|[string]| SERTA MRTA_LAMBDA}}

Description: Select which type of approximation is used to compute the electron scattering lifetimes due to electron-phonon coupling
{{Available|6.5.0}}

----
There are different approximations to compute the electronic lifetimes due to electron-phonon scattering.
Each of these can lead to significantly different transport coefficients.
It is possible to select more than one approximation in {{TAG|ELPH_SCATTERING_APPROX}}.
In this case, additional  electron-phonon accumulators are created for each scattering approximation.
## Options to select
;{{TAG|ELPH_SCATTERING_APPROX|CRTA}} - <u>C</u>onstant <u>R</u>elaxation-<u>T</u>ime <u>A</u>pproximation
:The relaxation time is assumed constant. It needs to be specified via {{TAG|TRANSPORT_RELAXATION_TIME}}. In this case, the computation of electron-phonon matrix elements is skipped entirely, which is a huge performance boost compared to the other relaxation-time approximations.
{{NB|warning|While the CRTA can be a reasonable approximation for metals, it will generally fail for insulators.}}

;{{TAG|ELPH_SCATTERING_APPROX|SERTA}} - <u>S</u>elf-<u>E</u>nergy <u>R</u>elaxation-<u>T</u>ime <u>A</u>pproximation
:Computes the relaxation time from the imaginary part of the Fan self-energy, evaluated on the electronic eigenenergy:
:
\frac{1}{\tau^{\mathrm{SERTA}}_{n\mathbf{k}}} = \frac{2\pi}{\hbar} \sum_{n'\nu\mathbf{k}'} w_{n\mathbf{k},n'\mathbf{k}'} \, |g^{\nu}_{n\mathbf{k},n'\mathbf{k}'}|^2 \left[ (n_{\nu\mathbf{q}} + 1 - f_{n'\mathbf{k}'}) \, \delta(\varepsilon_{n\mathbf{k}} - \varepsilon_{n'\mathbf{k}'} - \hbar\omega_{\nu\mathbf{q}}) + (n_{\nu\mathbf{q}} + f_{n'\mathbf{k}'}) \, \delta(\varepsilon_{n\mathbf{k}} - \varepsilon_{n'\mathbf{k}'} + \hbar\omega_{\nu\mathbf{q}}) \right]

:where {\tau^{\mathrm{SERTA}}_{n\mathbf{k}}} is the relaxation time (or scattering time, or lifetime) for state (n,\mathbf{k}), w_{n\mathbf{k},n'\mathbf{k}'} is the scattering weight, g^{\nu}_{n\mathbf{k},n'\mathbf{k}'} is the electron-phonon coupling matrix element, f_{n\mathbf{k}} is the population of the electronic state (Fermi-Dirac distribution), n_{\nu\mathbf{q}} is the population of the phononic state (Bose-Einstein distribution), \varepsilon_{n\mathbf{k}} is the energy of an electron band, \omega_{\nu\mathbf{q}} is the phonon frequency, and \delta is the Dirac delta function.

:For SERTA, the scattering weight is:
:
w_{n\mathbf{k},n'\mathbf{k}'} = 1

;{{TAG|ELPH_SCATTERING_APPROX|ERTA_LAMDBA}} - <u>E</u>nergy <u>R</u>elaxation-<u>T</u>ime <u>A</u>pproximation (mean-free path approximation)
:Applies an energy-projected weight scaled by mean-free path (where \mu is the chemical potential):
:
w_{n\mathbf{k},n'\mathbf{k}'} = \left(1 - \frac{\mathbf{v}_{n\mathbf{k}} \cdot \mathbf{v}_{n'\mathbf{k}'}}{|\mathbf{v}_{n\mathbf{k}}| |\mathbf{v}_{n'\mathbf{k}'}|} \left| \frac{\varepsilon_{n'\mathbf{k}'} - \mu}{\varepsilon_{n\mathbf{k}} - \mu} \right|\right)

{{NB|warning|The formula above is correct and used from the next release of VASP onwards. In VASP 6.5.0 and 6.5.1, the following formula is used:
:
w_{n\mathbf{k},n'\mathbf{k}'} = \left(1 - \frac{\mathbf{v}_{n\mathbf{k}} \cdot \mathbf{v}_{n'\mathbf{k}'}}{|\mathbf{v}_{n\mathbf{k}}| |\mathbf{v}_{n'\mathbf{k}'}|}\right) \left| \frac{\varepsilon_{n'\mathbf{k}'} - \mu}{\varepsilon_{n\mathbf{k}} - \mu} \right|

}}
;{{TAG|ELPH_SCATTERING_APPROX|ERTA_TAU }} - <u>E</u>nergy <u>R</u>elaxation-<u>T</u>ime <u>A</u>pproximation (lifetime approximation)
:
w_{n\mathbf{k},n'\mathbf{k}'} = \left(1 - \frac{\mathbf{v}_{n\mathbf{k}} \cdot \mathbf{v}_{n'\mathbf{k}'}}{|\mathbf{v}_{n\mathbf{k}}|^2} \left| \frac{\varepsilon_{n'\mathbf{k}'} - \mu}{\varepsilon_{n\mathbf{k}} - \mu} \right|\right)

{{NB|warning|The formula above is correct and used from the next release of VASP onwards. In VASP 6.5.0 and 6.5.1, the following formula is used:
:
w_{n\mathbf{k},n'\mathbf{k}'} = \left(1 - \frac{\mathbf{v}_{n\mathbf{k}} \cdot \mathbf{v}_{n'\mathbf{k}'}}{|\mathbf{v}_{n\mathbf{k}}|^2}\right) \left| \frac{\varepsilon_{n'\mathbf{k}'} - \mu}{\varepsilon_{n\mathbf{k}} - \mu} \right|

}}
;{{TAG|ELPH_SCATTERING_APPROX|MRTA_LAMDBA}} - <u>M</u>omentum <u>R</u>elaxation-<u>T</u>ime <u>A</u>pproximation (mean-free path approximation)
:
w_{n\mathbf{k},n'\mathbf{k}'} = \left(1 - \frac{\mathbf{v}_{n\mathbf{k}} \cdot \mathbf{v}_{n'\mathbf{k}'}}{|\mathbf{v}_{n\mathbf{k}}|  |\mathbf{v}_{n'\mathbf{k}'}|}\right)

;{{TAG|ELPH_SCATTERING_APPROX|MRTA_TAU }} - <u>M</u>omentum <u>R</u>elaxation-<u>T</u>ime <u>A</u>pproximation (lifetime approximation)
:
w_{n\mathbf{k},n'\mathbf{k}'} = \left(1 - \frac{\mathbf{v}_{n\mathbf{k}} \cdot \mathbf{v}_{n'\mathbf{k}'}}{|\mathbf{v}_{n\mathbf{k}}|^2}\right)
## Related tags and articles
* Transport calculations
* Electronic transport coefficients
* Electron-phonon accumulators
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_TRANSPORT}}
* {{TAG|ELPH_TRANSPORT_DRIVER}}
* {{TAG|TRANSPORT_RELAXATION_TIME}}

Category:INCAR tagCategory:Electron-phonon_interactions
