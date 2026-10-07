{{TAGDEF|LRPAFORCE|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LRPAFORCE}}=.TRUE. calculates forces in the random-phase approximation (RPA).
----
Available as of VASP.6.1.

This tag can be optionally set in low-scaling RPA calculations or  GW calculations. It allows computing the RPA forces{{cite|ramberger:prl:118}} on each ion. 
Setting
 {{TAGBL|ALGO}} = RPAR ;  LRPAFORCE = .TRUE. 
or equivalently 
 {{TAGBL|ALGO}} = G0W0R ; LRPAFORCE = .TRUE. 
determines the RPA total energy with corresponding forces and the quasiparticle energies within the GW approximation. 

The {{TAG|LRPAFORCE}} tag can be used in combination with the standard relaxation options {{TAG|IBRION}} and {{TAG|NSW}} as explained in the corresponding RPA calculations guide.

Generally, the energy calculated by the RPA can be quite noisy as a function of the ionic positions, in particular, if {{TAG|PRECFOCK}} = FAST and {{TAG|NMAXFOCKAE}} = 1 is set
(these are the default values for RPA calculations). Most of the noise is related to the exact exchange energy, and we are working on methods to improve this issue.
Currently, to reduce the noise in the energy and forces, it is sensible to set {{TAG|PRECFOCK}} = Normal (typically doubling the execution time and memory requirement). It is also possible to set {{TAG|LMAXFOCKAE}} = -1 (which implicitly sets {{TAG|NMAXFOCKAE}} = 0). This makes the correlation energies and the related forces less noisy, but technically less accurate (i.e. part of the correlation energy will be missing at high transition energies).  
Overall, RPA forces must be used carefully and only after extensive testing of all relevant parameters. 
{{NB|mind|The RPA stress tensor is not available.}}  
{{NB|warning|Only {{TAG|ISIF}}{{=}}0 is supported.}}
{{NB|warning|Using {{TAG|LDAU|.TRUE.}} with {{TAG|LRPAFORCE}} introduces double counting errors prior to version 6.6.0.}}
## Related tags and articles
{{TAG|IBRION}},
{{TAG|NSW}},
{{TAG|ALGO}},
{{TAG|NBANDS}},
{{TAG|NMAXFOCKAE}},
RPA calculations, 
 GW calculations
{{sc|LRPAFORCE|Examples|Examples that use this tag}}
----
Category:INCAR tagCategory:GWCategory:Molecular dynamicsCategory:Ionic minimizationCategory:ForcesCategory:Low-scaling GW and RPA
## References
