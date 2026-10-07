{{DISPLAYTITLE:ELPH_TRANSPORT_DFERMI_TOL}}
{{TAGDEF|ELPH_TRANSPORT_DFERMI_TOL|[real]|1e-6}}

Description: choose the fraction of the integral weight of the derivative of the Fermi–Dirac distribution that is excluded when defining the energy window for the Onsager coefficients. Must be between 0 and 1, and is only used when {{TAG|ELPH_TRANSPORT_DRIVER}}=1.
{{Available|6.5.0}}

----
Using this parameter, {{TAG|ELPH_TRANSPORT_EMIN}} and {{TAG|ELPH_TRANSPORT_EMAX}} are automatically computed from the chemical potentials and the distribution -\partial f^0/\partial \epsilon.  
Formally, the integration window [\mu-e,\mu+e] is chosen such that

:
\int_{\mu-e}^{\mu+e} \left(-\frac{\partial f^0}{\partial \epsilon}\right) d\epsilon
= 1 - \alpha,

where \alpha \equiv {{TAG|ELPH_TRANSPORT_DFERMI_TOL}}.  
This gives

:
e = k_B T \, \ln\!\left(\tfrac{2-\alpha}{\alpha}\right).

A small value means that only the tails of the derivative of the Fermi-dirac distribution are excluded from the integral.
A large value means that only a small energy window around the chemical potential is used.

The integral is then discretized with a number of energy points set by {{TAG|TRANSPORT_NEDOS}} and evaluated using the Simpson's rule.
## Related tags and articles
* Transport calculations
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_TRANSPORT}}
* {{TAG|ELPH_TRANSPORT_DRIVER}}
* {{TAG|ELPH_TRANSPORT_EMIN}}
* {{TAG|ELPH_TRANSPORT_EMAX}}
* {{TAG|TRANSPORT_NEDOS}}

Category:INCAR tagCategory:Electron-phonon_interactions
