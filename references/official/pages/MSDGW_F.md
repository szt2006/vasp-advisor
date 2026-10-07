{{TAGDEF|MSDGW_F|[real]|-1}}

Description: A positive value of {{TAG|MSDGW_F}} triggers the mixed stochastic-deterministic compression algorithm of Altman and co-workers.{{cite|altman:prl:2024}}
----
{{TAG|MSDGW_F}} is the constant energy ratio F of the compression algorithm. If set to a positive value, energies beyond the protected space defined by {{TAG|MSDGW_NP}} are subdivided into energy bins of width \Delta E_i and replaced by other energies E_i, such that F=\Delta E_i/E_i. The original orbitals are replaced by {{TAG|MSDGW_NXI}} randomly linear combined orbitals. Larger values of {{TAG|MSDGW_F}} increase the compression level at the expense of accuracy. The same holds true for smaller values of {{TAG|MSDGW_NXI}}.

This compression algorithm has been developed to reduce the large number of unoccupied states required for the calculation of the screened interaction in GW calculations. It has been demonstrated that one can reduce the unoccupied manifold by more than 50 per cent and speed up the GW step by a factor of 2 or more with a resulting error of only 50 meV or less on the quasi-particle band gap.{{cite|altman:prl:2024}}
{{NB| mind | Available as of VASP.6.6.0.|:}}
{{NB| warning | Not recommended for {{TAG|LRPAFORCE}}{{=}}T.|:}}
## Use cases
*Recommended for {{TAG|ALGO}}=EVG0W[R|RK]|CRPA[R|RK]: 
The compression can be used for all type of GW calculations regardless if the calculation is performed in steps or in the all-in-one mode. Following lines in stdout and {{TAG|OUTCAR}} indicate that the compression has been performed:
  => avg. energy ratio F (%):  1.00                                                                                                                                                                                                                                                                                          
  bands after compression:      240  

To test different compression settings, it is recommended perform the GW/CRPA calculation in steps and to set {{TAG|MSDGW_F}} only in the actual GW step. This avoids repeating the expensive exact diagonalization of the Kohn-Sham Hamiltonian.
## Caveats
Care must be taken for GW/(c)RPA calculations that are performed in steps and include the long-wave limit stored in {{FILE|WAVEDER}}. After band compression, this limit must be re-calculated by setting {{TAG|LOPTICS}} in combination with {{TAG|LPEAD}}.
## Related tags and articles
{{TAG|MSDGW_NXI}},
{{TAG|MSDGW_SEED}},
{{TAG|MSDGW_NP}}
## References
----
Category:INCAR tagCategory:GWCategory:Constrained-random-phase_approximation
