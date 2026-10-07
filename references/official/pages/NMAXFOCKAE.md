{{TAGDEF|NMAXFOCKAE|1{{!}}2|1}}

Description: Sets the number of shape-restoring functions used for each angular momentum quantum number L in shape restoration.
----
In shape restoration, radial functions with vanishing multipole moment are added to the PAW compensation charge for each angular momentum quantum number L. {{TAG|LMAXFOCKAE}} sets the maximum L; {{TAG|NMAXFOCKAE}} sets how many functions are used per L, and thereby the wave vectors at which the all-electron density is matched:

* {{TAG|NMAXFOCKAE|1}}: one function per L, matched at {{TAG|QMAXFOCKAE}} (default 6 Å-1, which corresponds to a plane-wave energy of approximately 140 eV).
* {{TAG|NMAXFOCKAE|2}}: two functions per L, matched at {{TAG|QMAXFOCKAE}} and twice {{TAG|QMAXFOCKAE}} (default 5 and 10 Å-1, corresponding to approximately 95 eV and 380 eV).

The wave vectors {{TAG|QMAXFOCKAE}} are the points at which the density is fitted, not a guarantee of the accuracy reached at a given cutoff. 

{{TAG|NMAXFOCKAE}} only accepts the values 1 and 2. Values outside that range are corrected to the nearest allowed one, so a larger number does not give a finer expansion.
{{NB|mind|Whenever {{TAG|LMAXFOCKAE|-1}} is set — the default for DFT and Hartree-Fock — shape restoration is inactive and {{TAG|NMAXFOCKAE}} has no effect. Shape restoration applies only to the Fock exchange and to many-body perturbation theory, i.e., GW, RPA and MP2.}}
{{NB|important|The total energies of calculations that differ in {{TAG|NMAXFOCKAE}} and/or {{TAG|LMAXFOCKAE}} cannot be compared.}}
## Recommendations
{{TAG|NMAXFOCKAE|1}}, the default, is sufficient in most cases and balances accuracy against computational cost. Refs. {{cite|shishkin:prb:2006}} and {{cite|unzog:prb:2022}} report accurate energy differences and quasiparticle energies at this setting.

{{TAG|NMAXFOCKAE|2}} is reported to give very accurate results for post-DFT methods, including for the 3*d* elements where the one-center error is largest{{cite|unzog:prb:2022}}. It is not free: the noise and the egg-box effects grow with {{TAG|NMAXFOCKAE}}, and two shape-restoring functions per L need a fine FFT grid. Set {{TAG|NGX}}, {{TAG|NGY}} and {{TAG|NGZ}} explicitly when using it. VASP issues an alert to that effect whenever two functions are requested. We recommend using it only after tests that establish the higher accuracy is needed for your application.

Two specific expectations from the literature:
* For GW calculations, going from {{TAG|NMAXFOCKAE|1}} to {{TAG|NMAXFOCKAE|2}} may shift quasiparticle energies by 100 to 200 meV for 3*d* and late 4*d* and 5*d* elements{{cite|unzog:prb:2022}}.
* For RPA and MP2 total energies, the two settings usually differ little in energy *differences*, even though the absolute correlation energies change{{cite|unzog:prb:2022}}.

The two tags are coupled: see {{TAG|LMAXFOCKAE}} for the consistency requirement that applies when energy differences are compared, and for how to read both values back from the {{FILE|OUTCAR}} file.
## Related tags and articles
{{TAG|LMAXFOCKAE}}, {{TAG|LMAXFOCK}}, {{TAG|QMAXFOCKAE}}, {{TAG|LFOCKAEDFT}}, {{TAG|LFOCKSTD}}, Projector-augmented-wave formalism

{{sc|NMAXFOCKAE|Howto|Workflows that use this tag}}
## References
Category:INCAR tag
Category:ACFDT
Category:Low-scaling GW and RPA
Category:Exchange-correlation functionals
Category:Hybrid functionals
Category:Many-body perturbation theory
Category:GW
