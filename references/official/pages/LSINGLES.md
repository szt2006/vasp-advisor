{{TAGDEF|LSINGLES|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: Switch on singles contribution to correlation energy for GW algorithms.{{cite|klimes:jcp:143}}
----
{{TAG|LSINGLES}} enables the calculation of the singles contributions to the correlation energy that can be represented by the following Feynman (time-ordered) diagrams:{{cite|kaltak:thesis2015}}{{cite|klimes:jcp:143}}

320px

{{TAG|LSINGLES}} is used in combination with the low-scaling ACFDT/RPA and GW algorithms.  

If the ACFDT/RPA algorithm is selected with {{TAG|ALGO}}=RPAR|ACFDTR and {{TAGBL|LSINGLES}} is set, the code calculates two singles contributions and writes following lines to {{FILE|OUTCAR}}

 HF single shot energy change        -1.23182672
 renormalized HF singles             -1.23310555

Here, **renomalized HF singles** corresponds to the renormalized singles contribution suggested by Ren and coworkers:{{cite|ren:prb:88}}

E^{rSE}_c = -\sum_{a\in virt, i\in occ} \frac{|\langle i| V^{HF} - V_0^{KS}|a\rangle|^2 }{\epsilon_a-\epsilon_i}

This contribution accounts for the change of the mean-field exchange energy and can be derived consistently within the AC-FDT framework as described in Sec. II D Eq. (28) of Klimeš et al.{{cite|klimes:jcp:143}}

In contrast, the **HF single shot energy change** line contains the somewhat simpler contribution{{cite|klimes:jcp:143}}

E_c^{rSE} = \mathrm{Tr}\left[ (\gamma_{HF} - \gamma_{DFT})\hat h_{HF} \right],

where \gamma_{HF} is the Hartree-Fock density matrix, determined for the Hartree-Fock Hamiltonian \hat h_{HF} and \gamma_{DFT} is the Kohn-Sham density matrix.
In all practical calculations, we found that both values, the single-shot HF and renormalized singles contributions, are exceedingly close to each other.

If the GW algorithm is selected with {{TAG|ALGO}}=G0W0R, the {{FILE|OUTCAR}} contains also the singles contribution beyond the Hartree-Fock level

E_c^{GWSE} = \mathrm{Tr}\left[ (\gamma_{RPA} - \gamma_{DFT})\hat h_{HF} \right],

where \gamma_{RPA} is the RPA density matrix.{{cite|klimes:jcp:143}}
For versions <= 6.4.2, this contribution is not directly printed to file. However, the first and second term is printed to {{FILE|OUTCAR}}:
 Energies using frozen KS orbitals
 Hartree-Fock free energy of the ion-electron system (eV)
  ...
  eigenvalues         EBANDS =       -88.61789695   <--------Tr{ gam_DFT h_HF}---------
  ... 
 Energies after update of density matrix 
 Hartree-Fock free energy of the ion-electron system (eV) 
  ...
  eigenvalues         EBANDS =       -89.68870320   <--------Tr{ gam_RPA h_HF}---------
  ...
Version >6.4.2 writes the GWSE singles contribution to {{FILE|OUTCAR}}: 
  GWSE singles contribution:        -1.07080625
{{NB|mind|The singles contribution is calculated correctly only for the default {{TAG|NATURALO}}{{=}}2.}}
The ACFDT total energy in the limit of infinite energy cutoff is then obtained by adding the singles contribution to the value of 

HF+E_corr(extrapolated)    =      -153.98810072 eV
## Related tags and articles
*{{TAG|NATURALO}} natural orbital selection for *RPA* and *GW* calculations
*{{TAG|ALGO}} for response functions and *RPA* calculations
* for an overview on total energies using the ACFDT/RPA formalism
* for a practical guide to GW calculations
* Basis set convergence of ACFDT/RPA calculations
## References
----
Category:INCAR tagCategory:Many-body perturbation theoryCategory:GWCategory:ACFDTCategory:Low-scaling GW and RPA
