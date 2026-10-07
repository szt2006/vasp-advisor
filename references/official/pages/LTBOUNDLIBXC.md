{{TAGDEF|LTBOUNDLIBXC|.TRUE. {{!}} .FALSE. |.FALSE.}}

Description: {{TAG|LTBOUNDLIBXC}} specifies whether or not the lower bound for the Kohn-Sham kinetic-energy density \tau_{\sigma} (\tau_{\sigma}^{\textrm{W}}<\tau_{\sigma}) is enforced before \tau_{\sigma} is used in a {{TAG|METAGGA}} functional from Libxc.
----

The Kohn-Sham kinetic-energy density 
:\tau_{\sigma}=\frac{1}{2}\sum_{i}\nabla\psi_{i\sigma}^{*}\cdot\nabla\psi_{i\sigma} 
should, in principle, be larger than the von Weizsäcker kinetic-energy density{{cite|kurth:ijqc:1999}} 
:\tau_{\sigma}^{\textrm{W}}=\frac{\left\vert\nabla n_{\sigma}\right\vert^{2}}{8 n_{\sigma}}.

However, for numerical reasons \tau_{\sigma}^{\textrm{W}}<\tau_{\sigma} may not be fulfilled, which can potentially lead to problems, in particular if the meta-GGA functional is not defined for negative values of \tau_{\sigma}-\tau_{\sigma}^{\textrm{W}}. If {{TAG|LTBOUNDLIBXC}}=.TRUE. in {{FILE|INCAR}}, then \tau_{\sigma}=\max(\tau_{\sigma},\tau_{\sigma}^{\mathrm{W}}) is applied before \tau_{\sigma} is used in a meta-GGA functional from Libxc.

However, according to tests, for some of the most common meta-GGA functionals like SCAN{{cite|sun:prl:15}}, a violation of the lower bound is technically not a problem. Furthermore, it has been observed that applying \tau_{\sigma}=\max(\tau_{\sigma},\tau_{\sigma}^{\mathrm{W}}) may possibly lead to very inaccurate forces and stress tensor. Therefore, by default {{TAG|LTBOUNDLIBXC}}=.FALSE. and Libxc should be compiled  with the option --disable-fhc has explained here.

Thus, the recommendation is to set {{TAG|LTBOUNDLIBXC}}=.TRUE. only in the case convergence shows an erratic behavior. If this choice is made, then the forces and stress tensor should be carefully monitored if a geometry optimization is done.
## Related tags and articles
{{TAG|LIBXC1}},
{{TAG|LIBXC2}},
{{TAG|METAGGA}}

{{sc|LTBOUNDLIBXC|Examples|Examples that use this tag}}
## References
----

Category:INCAR tagCategory:Exchange-correlation functionals
