{{TAGDEF|LWEIGHTED|[logical]|.FALSE.}}

Description: {{TAG|LWEIGHTED}} selects the weighted-cRPA method.
----
Selects the cRPA method of Sasioglu, Friedrich and Blügel{{cite|sasioglu:prb:83}} where the following screening contribution is subtracted from the full RPA polarizability:
::\tilde  \chi^\sigma_{{\bf G,G}'}({\bf q},i\omega)\approx
\frac 1{N_k}\sum_{nn'{\bf k}}
\frac{
f_{n\bf k}-f_{n'\bf k-q}
}{
\epsilon_{n{\bf k}} -  \epsilon_{n'\bf k-q} - i \omega 
}
p_{n\bf k }^{\sigma}
p_{n'\bf k-p }^{\sigma'}
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
## Related tags and articles
{{TAG|LDISENTANGLED}},
{{TAG|LSCRPA}},
{{TAG|ALGO}}

{{sc|LWEIGHTED|Howto|Workflows that use this tag}}
## References
Category:INCAR_tagCategory:Constrained-random-phase approximation
