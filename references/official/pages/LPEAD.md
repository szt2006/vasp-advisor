{{TAGDEF|LPEAD|.TRUE. {{!}} .FALSE|.FALSE.}}

Description: for {{TAG|LPEAD}}=.TRUE., the derivative of the cell-periodic part of the orbitals w.r.t. **k**, |&nabla;**k**un**k**&rang;, is calculated using finite differences ("perturbation expansion after discretization" (PEAD)).
----
The derivative of the cell-periodic part of the orbitals w.r.t. **k**, **k**, |&nabla;**k**un**k**&rang;, may be written as:

:
  \mathbf{\nabla_{k}} \tilde{u}_{n\mathbf{k}} \rangle =
\sum_{n\neq n'}
\frac{| \tilde{u}_{n'\mathbf{k}} \rangle \langle \tilde{u}_{n'\mathbf{k}} |
\frac{\partial\left[H(\mathbf{k})-\epsilon_{n\mathbf{k}}S(\mathbf{k})\right]}{\partial \mathbf{k}}
  \tilde{u}_{n\mathbf{k}} \rangle}{\epsilon_{n\mathbf{k}}-\epsilon_{n'\mathbf{k}}}

where H(**k**) and S(**k**) are the Hamiltonian and overlap operator for the cell-periodic part of the orbitals, and the sum over *n*&acute; must include a sufficiently large number of unoccupied states.

It may also be found as the solution to the following linear Sternheimer equation (see {{TAG|LEPSILON}}):

:
\left[H(\mathbf{k})-\epsilon_{n\mathbf{k}}S(\mathbf{k})\right]
  \mathbf{\nabla_{k}} \tilde{u}_{n\mathbf{k}} \rangle
=-\frac{\partial\left[H(\mathbf{k})-\epsilon_{n\mathbf{k}}S(\mathbf{k})\right]}
{\partial \mathbf{k}}|\tilde{u}_{n\mathbf{k}} \rangle

Alternatively one may compute \nabla_{\mathbf{k}} \tilde{u}_{n\mathbf{k}} from finite differences ({{TAG|LPEAD}}=.TRUE.):

:
\frac{\partial | \tilde{u}_{n\mathbf{k}_j} \rangle}{\partial k}=
\frac{ie}{2\Delta k} \sum^N_{m=1}
\left[ | \tilde{u}_{m\mathbf{k}_{j+1}} \rangle
S^{-1}_{mn}(\mathbf{k}_j,\mathbf{k}_{j+1})\rangle -
  \tilde{u}_{m\mathbf{k}_{j-1}} \rangle
S^{-1}_{mn}(\mathbf{k}_j,\mathbf{k}_{j-1})\rangle\right]

where *m* runs over the *N* occupied bands of the system, &Delta;*k*=**k**j+1-**k**j, and

:
S_{nm}(\mathbf{k}_j,\mathbf{k}_{j+1})=
\langle \tilde{u}_{n\mathbf{k}_{j}}| \tilde{u}_{m\mathbf{k}_{j+1}}\rangle
.

As mentioned in the context of the self-consistent response to finite electric fields one may derive analoguous expressions for |&nabla;**k**un**k**&rang; using higher-order finite difference approximations.

When {{TAG|LPEAD}}=.TRUE., VASP will compute |&nabla;**k**un**k**&rang; using the aforementioned finite difference scheme. The order of the finite difference approximation can be specified by means of the {{TAG|IPEAD}}-tag (default: {{TAG|IPEAD}}=4).

These tags may be used in combination with {{TAG|LOPTICS}}=.TRUE. and {{TAG|LEPSILON}}=.TRUE..
----
*N.B. Please note that {{TAG|LPEAD}} = .TRUE. **is not supported for metallic systems**. 
## Related tags and articles
{{TAG|IPEAD}},
{{TAG|LEPSILON}},
{{TAG|LOPTICS}},
{{TAG|LCALCEPS}},
{{TAG|EFIELD_PEAD}},
Berry phases and finite electric fields

{{sc|LPEAD|Examples|Examples that use this tag}}
## References
</references>
----
----

Category:INCAR tagCategory:Linear responseCategory:Dielectric propertiesCategory:Berry phases
