{{DISPLAYTITLE:ELPH_TRANSPORT_DRIVER}}
{{TAGDEF|ELPH_TRANSPORT_DRIVER|[integer]|2}}

Description: choose method to compute the Onsager coefficients, which are then used to compute the transport coefficients.
{{Available|6.5.0}}

----
The Onsager coefficients can be computed using either of the options below, each with its own advantages and disadvantages.
They are defined as
:
L_{ij} = \int d\epsilon \, \mathcal{T}(\epsilon) \,
(\epsilon-\mu)^{i+j-2}
\left( -\frac{\partial f^0}{\partial \epsilon} \right),

where \mathcal{T}(\epsilon) is the  transport distribution function,  
\mu the  chemical potential, and f^0 the Fermi–Dirac distribution.

; {{TAG|ELPH_TRANSPORT_DRIVER|1|op==}}
: The discretized Onsager coefficient is evaluated as
::
L_{ij} \;\approx\; \sum_{k=1}^{N} w_k \;
\mathcal{T}(\epsilon_k)\;
(\epsilon_k - \mu)^{\,i+j-2}\;
\left( -\frac{\partial f^0}{\partial \epsilon} \right).

:with \epsilon_k = \epsilon_\text{min}+(k-1)\Delta \epsilon,\;\; k=1,\dots,N and \Delta \epsilon = \tfrac{\epsilon_\text{max}-\epsilon_\text{min}}{N-1} and \epsilon_\text{min}={{TAG|ELPH_TRANSPORT_EMIN}} and \epsilon_\text{max}={{TAG|ELPH_TRANSPORT_EMAX}} or alternatively both \epsilon_\text{min} and \epsilon_\text{max} are set by {{TAG|ELPH_TRANSPORT_DFERMI_TOL}}, w_k the weights due to the Simpson integration rule and N={{TAG|TRANSPORT_NEDOS}}.

; {{TAG|ELPH_TRANSPORT_DRIVER|2|op==}}
: Use Gauss-Legendre integration to evaluate the Onsager coefficients. The convergence of the integral can be checked by performing a convergence study with respect to N={{TAG|TRANSPORT_NEDOS}} alone. In this case the Onsager coefficients are evaluated using the following discretization
::
L_{ij} \;\approx\; \tfrac{1}{2} \sum_{k=1}^N
w_k \,
\left( \frac{k_B T}{-e} \ln \frac{1+x_k}{1-x_k} \right)^{i+j-2}
\mathcal{T}\!\left(\mu + k_B T \ln\frac{1+x_k}{1-x_k}\right),

:with w_k and x_k the weights and abcissae of the Gauss-Legendre quadrature rule.
## Related tags and articles
* Transport calculations
* {{TAG|ELPH_RUN}}
* {{TAG|ELPH_TRANSPORT}}
* {{TAG|TRANSPORT_NEDOS}}
* {{TAG|ELPH_TRANSPORT_DFERMI_TOL}}
* {{TAG|ELPH_TRANSPORT_EMIN}}
* {{TAG|ELPH_TRANSPORT_EMAX}}

Category:INCAR tagCategory:Electron-phonon_interactions
