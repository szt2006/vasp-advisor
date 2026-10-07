{{TAGDEF|LSCK|[logical]| .FALSE.}}                            
{{NB|important|Up to vasp.6.2, the default was {{TAG|LSCK}}{{=}} .TRUE.}}
----Description: {{TAG|LSCK}}=.True. switches on the squeezed Coulomb kernel.
If {{TAG|LSCK}} is set to .TRUE., the squeezed Coulomb kernel is used instead of the cosine window {{cite|riemelmoser:jcp:2020}}:

v_{G} = 4 \pi e^2 \frac{
(G_{max}-G_{min})(G_{max}-G)
}{
(G_{min}^2 - G(2G_{min}-G_{max}))^2
}  
\qquad \mbox{for} \quad  \mathrm{ENCUTGWSOFT}=\frac{\hbar^2G_{min}^2}{2m_e}<\frac{\hbar^2 G^2}{2m_e}<\frac{\hbar^2G_{max}^2}{2m_e}=\mathrm{ENCUTGW} 

This kernel 'squeezes' the contributions from large wave vectors G>G_{max} into the window given by {{TAG|ENCUTGWSOFT}}. Effectively, this extrapolates the random-phase-approximation&ndash;correlation energy to the {{TAG|ENCUTGW}} \to \infty limit, assuming that the basis-set-incompleteness error falls off as 1/{{TAG|ENCUTGW}}^{3/2}.
## Related tags and articles
{{TAG|ENCUTGW}},
{{TAG|GW calculations}}
{{TAG|ACFDT/RPA calculations}}

{{sc|LSCK|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Many-body perturbation theoryCategory:GWCategory:ACFDT
