{{TAGDEF|IMIX|0 {{!}} 1 {{!}} 2 {{!}} 4|4}}

Description: {{TAG|IMIX}} specifies the type of density mixing.
----
## {{TAG|IMIX}}=0: No mixing
::\rho_{\rm mix}=\rho_{\rm out}\,
## {{TAG|IMIX}}=1: Kerker mixing
:For Kerker mixing, the mixed density is given by
::\rho_{\rm mix}\left(G\right)=\rho_{\rm in}\left(G\right)+A \frac{G^2}{G^2+B^2}\Bigl(\rho_{\rm out}\left(G\right)-\rho_{\rm in}\left(G\right)\Bigr)
:with A={{TAG|AMIX}} and B={{TAG|BMIX}}. If {{TAG|BMIX}} is very small, e.g., {{TAG|BMIX}}=0.0001, a straight mixing is obtained. 
{{NB|mind|{{TAG|BMIX}}{{=}}0 might cause floating-point exceptions on some platforms.|:}}
## {{TAG|IMIX}}=2: Variant of Tchebycheff mixing
:VASP uses a variant of the popular Tchebycheff-mixing scheme. Here, the following second order equation of motion is used:
::\ddot{\rho}_{\rm in}\left(G\right) = 2*A \frac{G^2}{G^2+B^2}\Bigl(\rho_{\rm out}\left(G\right)-\rho_{\rm in}\left(G\right)\Bigr)-\mu \dot{\rho}_{\rm in}\left(G\right)
:with A={{TAG|AMIX}}, B={{TAG|BMIX}}, and \mu={{TAG|AMIN}}. A velocity Verlet algorithm is used to integrate this equation. The discretized equation reads: 
::\dot{\rho}_{N+1/2} =  \Bigl(\left(1-\mu/2\right) \dot{\rho}_{N-1/2} + 2*F_N \Bigr)/\left(1+\mu/2\right)
:where
::F\left(G\right)=A\frac{G^2}{G^2+B^2} \Bigl(\rho_{\rm out}\left(G\right)-\rho_{\rm in}\left(G\right)\Bigr)
:and
::\rho_{N+1}=\rho_{N+1}+\dot{\rho}_{N+1/2},
:where the index *N* is the electronic iteration, and *F* is the force acting on the charge.

:For {{TAG|BMIX}}&asymp;0, no model for the dielectric matrix is used. For \mu=2 a simple straight mixing is obtained. Therefore, \mu=2 corresponds to maximal damping, while \mu=0 implies no damping. To determine the optimal parameters for \mu and {{TAG|AMIX}}, first converge to the ground state with the Pulay mixer ({{TAG|IMIX}}=4). Then, search for the the eigenvalues of the charge-dielectric matrix in the {{FILE|OUTCAR}} file at the last occurrence of
 eigenvalues of (default mixing * dielectric matrix)
:The optimal parameters are then given by:
::{|
  {{TAG|AMIX}}|| ||={\rm AMIX}({\rm as\; used\; in\; Pulay\; run})*{\rm smallest\; eigenvalue}
  {{TAG|AMIN}}|| ||=\mu=2\sqrt{{\rm smallest\; eigenvalue}/{\rm largest\; eigenvalue}}
## {{TAG|IMIX}}=4: Broyden's 2nd method and Pulay-mixing method (default)
:For {{TAG|WC}}=0, VASP uses Broyden's 2nd method, and, for {{TAG|WC}}>0, VASP uses Pulay-mixing method.
:The default is a Pulay mixer with an initial approximation for the charge-dielectric function according to Kerker
::A\times\max\left(\frac{G^2}{G^2+B^2},A_{\rm min}\right)
:where A={{TAG|AMIX}}, B={{TAG|BMIX}}, and A_{\rm min}={{TAG|AMIN}}.

:{{TAG|AMIN}}=0.4 usually yields good convergence. {{TAG|AMIX}} strongly depends on the system, for instance, it should be small, e.g., {{TAG|AMIX}}= 0.02, for metals.
:In the Broyden scheme, the functional form of the initial mixing matrix is determined by {{TAG|AMIX}} and {{TAG|BMIX}} or the {{TAG|INIMIX}} tag. The metric used in the Broyden scheme is specified through {{TAG|MIXPRE}}.
## Related tags and articles
{{TAG|INIMIX}},
{{TAG|MAXMIX}},
{{TAG|AMIX}},
{{TAG|BMIX}},
{{TAG|AMIX_MAG}},
{{TAG|BMIX_MAG}},
{{TAG|AMIN}},
{{TAG|MIXPRE}},
{{TAG|WC}}

{{sc|IMIX|Examples|Examples that use this tag}}
## References
</references>
----

Category:INCAR tagCategory:Density mixing
