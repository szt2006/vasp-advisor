{{TAGDEF|LFOCKACE|.TRUE. {{!}} .FALSE. | .TRUE.}}
{{DEF|LFOCKACE|.TRUE.|for VASP.6|N/A|for VASP.5.X and older}}

Description: {{TAG|LFOCKACE}} determines whether the Adaptively Compressed Exchange Operator is used.{{cite|linlin:jctc:2016}} 

*N.B.:Available for CPU and OpenACC version of VASP.6 when compiled with -Dfock_dblbuf.
----
For {{TAG|LFOCKACE}}=.TRUE. the Cholesky decomposition X=LL^\dagger of the Fock exchange matrix X_{ij} = \langle \tilde\psi_i \mid \tilde V_X \mid \tilde\psi_j \rangle  is calculated and the adaptively compressed exchange operator \tilde V_{ACE} = -\sum_i \mid \tilde X_i \rangle \langle \tilde X_i \mid  is used for the action of the Fock exchange on the pseudo orbitals. This method can be used for hybrid functionals in combination with the Davidson algorithm ({{TAGBL|ALGO}}=Normal) to save a factor of \approx 3 in computation time.  

For {{TAG|LFOCKACE}}=.FALSE. the conventional orbital representation is used. 

Note: it is good scientific practice to cite the original publication (Ref. {{cite|linlin:jctc:2016}}) if you use this feature. The feature is used by default, if the Davidson algorithm ({{TAG|ALGO}} = Normal) is used; ACE is not used for {{TAG|ALGO}} = Damped or {{TAG|ALGO}} = All.  
## Related tags and articles
{{TAG|AEXX}},
{{TAG|AEXX}},
{{TAG|AGGAX}},
{{TAG|AGGAC}},
{{TAG|LHFCALC}},
List of hybrid functionals,
Hybrid functionals: formalism

{{sc|LHFCALC|Examples|Examples that use this tag}}
## References
----

Category:INCAR tagCategory:Exchange-correlation functionalsCategory:Hybrid_functionals
