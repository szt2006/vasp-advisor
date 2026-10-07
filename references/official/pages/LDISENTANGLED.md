{{TAGDEF|LDISENTANGLED|[logical]|.FALSE.}}

Description: Selects the disentanglement-cRPA method.
----
Selects the cRPA method of Miyake, Aryasetiawan, and Imada{{cite|miyake:prb:80}}. Following screening is subtracted from the full RPA polarizability:
::\tilde  \chi^\sigma_{{\bf G,G}'}({\bf q},i\omega)=
\frac 1{N_k}\sum_{\bf k}\sum_{nn'\in{\cal T}} 
\frac{
f_{n\bf k}-f_{n'\bf k-q}
}{
\tilde\epsilon_{n{\bf k}} -  \tilde\epsilon_{n'\bf k-q} - i \omega 
}
\langle
\tilde u_{n {\bf k  }}^{\sigma  } 
  e^{-i \bf (G+q) r}| 
\tilde u_{n'{\bf k-q}}^{ \sigma' }
\rangle
\langle
\tilde u_{n' {\bf k-q}}^{\sigma' }
  e^{-i \bf (G'-q)r'} |
\tilde u_{n{\bf k  }}^{ \sigma  }
\rangle
,
where \tilde \epsilon_{n\bf k}^\sigma is the disentangled band structure. 
## Related tags and articles
{{TAG|LWEIGHTED}},
{{TAG|LSCRPA}},
{{TAG|ALGO}}

{{sc|LDISENTANGLED|Howto|Workflows that use this tag}}
## References
Category:INCAR_tagCategory:Constrained-random-phase approximation
