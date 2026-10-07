{{TAGDEF|LSCDM|.TRUE. {{!}} .FALSE. }}
{{DEF|LSCDM|.FALSE.|}}

Description: {{TAG|LSCDM}} switches on the selected columns of the density matrix (SCDM) method. 

----

The selected columns of the density matrix (SCDM) method works by fitting a unitary matrix U_{mn\mathbf{k}} that transforms 
the basis from Bloch states |\psi_{n\mathbf{k}}\rangle obtained by VASP to a  Wannier basis |w_{m\mathbf{R}}\rangle.

::
  w_{m\mathbf{R}}\rangle =
\sum_{n\mathbf{k}}
e^{-i\mathbf{k}\cdot\mathbf{R}}
U_{mn\mathbf{k}}
  \psi_{n\mathbf{k}}\rangle.

This is done using a  one-shot method  through a singular-value decomposition as proposed by A. Damle and L. Lin {{cite|damle:mms:2018}}.

In order to obtain a good Wannierization, a certain level of freedom should be given to the localized orbitals to adequately accommodate the Bloch states. This is controlled by the cutoff function specified by the {{TAG|CUTOFF_TYPE}} tag and related parameters 
\mu ({{TAG|CUTOFF_MU}}) and
\sigma ({{TAG|CUTOFF_SIGMA}}).
## Related tags and articles
{{TAG|CUTOFF_TYPE}},
{{TAG|CUTOFF_MU}},
{{TAG|CUTOFF_SIGMA}}

{{sc|LSCDM|Examples|Examples that use this tag}}
## References
Category:INCAR tagCategory:Wannier functions
