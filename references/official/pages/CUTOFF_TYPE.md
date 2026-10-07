{{DISPLAYTITLE:CUTOFF_TYPE}}
{{TAGDEF|CUTOFF_TYPE|erfc {{!}} gaussian {{!}} fermi {{!}} num_wann}}
{{DEF|CUTOFF_TYPE|erfc|}}

Description: {{TAG|CUTOFF_TYPE}} chooses the type of cutoff function to be used before performing the singular-value decomposition (SVD) of the initial projections matrix.
 
----

This tag governs how much weight should be given in the SVD during the  one-shot Wannierization to a certain orbital with energy \epsilon_{n\mathbf{k}}.
If the weight is zero the orbital is not included in the fitting while if it is one it is included with the maximum importance.
This behavior is similar to the wannier90 disentanglement window.

In order to obtain a good Wannierization, a certain level of freedom should be given to the localized orbitals to adequately accommodate the Bloch states.
Applying a smooth cutoff function from the following table can help achieve this goal by including more states beyond the relevant energy range.
This is particularly important for systems with entangled states.
  CUTOFF_TYPE !! Function
  erfc || \frac{1}{2}\text{erfc}\left[(\epsilon_{n\mathbf{k}}-\mu)/\sigma\right]
  gaussian || e^{-(\epsilon_{n\mathbf{k}}-\mu)^2/\sigma}
  fermi || \frac{1}{e^{(\epsilon_{n\mathbf{k}}-\mu)/\sigma}+1}

with \sigma specified by the {{TAG|CUTOFF_SIGMA}} tag and \mu by {{TAG|CUTOFF_MU}}.

In addition to the aforementioned cutoff functions, it is also possible to select {{TAG|CUTOFF_TYPE|num_wann}}.
This mode is identical to {{TAG|CUTOFF_TYPE|erfc}} with the exception that \mu is set to \epsilon_{N \mathbf{k}} at each individual k-point, where N is the number of Wannier orbitals specified via {{TAG|NUM_WANN}}.
In this case, {{TAG|CUTOFF_MU}} is ignored.
## Related tags and articles
{{TAG|CUTOFF_MU}},
{{TAG|CUTOFF_SIGMA}},
{{TAG|LSCDM}},
{{TAG|LOCPROJ}}

{{sc|CUTOFF_TYPE|Examples|Examples that use this tag}}

Category:INCAR tagCategory:Wannier functions
