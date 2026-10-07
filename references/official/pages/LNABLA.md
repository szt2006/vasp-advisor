{{TAGDEF|LNABLA|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LNABLA}}=.TRUE. evaluates the transversal expression for the frequency dependent dielectric matrix.
----
Usually VASP uses the longitudinal expression for the frequency dependent dielectric matrix.
It is however possible to switch to the computationally somewhat simpler transversal expressions by selecting {{TAG|LNABLA}}=.TRUE. (Eqs. 17 and 20 in Ref.).
In this simplification the imaginary part of the macroscopic dielectric function is given by

:
\epsilon^{(2)}_{\alpha \beta} (\omega) = \frac{4 \pi^2 e^2  \hbar^4}{\Omega \omega^2 m_e^2} 
 \mathrm{lim}_{\mathbf{q} \rightarrow 0} \sum_{c,v, \mathbf{k}} 2 w_\mathbf{k} 
  \delta( \epsilon_{c\mathbf{k+q}} - \epsilon_{v\mathbf{k}} - \omega)  
  \times  \langle u_{c\mathbf{k}} | i{\mathbf{\nabla}_{\alpha} - \mathbf{k}}_{\alpha} | u_{v\mathbf{k}} \rangle
             \langle u_{c\mathbf{k}} | i{\mathbf{\nabla}_{\beta}  - \mathbf{k}}_{\beta}  | u_{v\mathbf{k}} \rangle^*.

Except for the purpose of testing, there is however hardly ever a reason
to use the transversal expression, since it is less accurate.
## Related tags and articles
{{TAG|LOPTICS}},
{{TAG|CSHIFT}}

{{sc|LNABLA|Examples|Examples that use this tag}}
## References
</references>
----

Category:INCAR tagCategory:Linear responseCategory:Dielectric properties
