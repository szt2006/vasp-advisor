{{TAGDEF|LSCRPA|[logical]|.FALSE.}}

Description: {{TAG|LSCRPA}} selects the spectral-cRPA method.
----
{{Available|6.6.0}}

In constrained random-phase approximation (cRPA) calculations, the target polarizability \tilde\chi is computed from the eigenspectrum of the target-space projectors as follows
::\tilde  \chi^\sigma_{{\bf G,G}'}({\bf q},i\omega)\approx
\frac 1{N_k}\sum_{nn'{\bf k}}
\frac{
f_{n\bf k}-f_{n'\bf k-q}
}{
\epsilon_{n{\bf k}} -  \epsilon_{n'\bf k-q} - i \omega 
}
\theta_{n\bf k }^{\sigma}
\theta_{n'\bf k-p }^{\sigma'}
\langle
u_{n {\bf k  }}^{\sigma  } 
  e^{-i \bf (G+q) r}| 
u_{n'{\bf k-q}}^{ \sigma' }
\rangle
\langle
u_{n' {\bf k-q}}^{\sigma' }
  e^{-i \bf (G'-q)r'} |
u_{n'{\bf k  }}^{ \sigma  }
\rangle

Here \theta_{n{\bf k}}^\sigma are the eigenvalues of the correlated projectors 

P_{mn}^{\sigma({\bf k})} =  \sum_{i\in \cal T} T_{i m}^{*\sigma({\bf k})} T_{i n}^{\sigma({\bf k})} 
 

ordered according to their leverage scores. The s-cRPA method results in larger effective interactions compared to w-cRPA or the projector-cRPA method and conserves the number of electrons.{{cite|kaltak:prb:2025}}
## Related tags and articles
{{TAG|LDISENTANGLED}},
{{TAG|LWEIGHTED}},
{{TAG|ALGO}}

{{sc|LSCRPA|Howto|Workflows that use this tag}}
## References
Category:INCAR_tagCategory:Constrained-random-phase approximation
