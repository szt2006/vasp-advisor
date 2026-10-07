{{DISPLAYTITLE:ML_MODE}}
{{TAGDEF|ML_MODE|train {{!}} select {{!}} refit {{!}} refitbayesian {{!}} run {{!}} delta {{!}} none | none}}

Description: String-based tag selecting operation mode for machine learning force fields.
{{NB|mind|This tag is only available as of VASP.6.4.0.}}
----
This tag acts as a "super tag" and selects the operation mode by selecting the defaults for all other tags. Every tag that is affected by this "super tag" can be overwritten by the user by simply specifying the value for that tag.
The following options are available for this tag:

<ul>
<li>{{TAG|ML_MODE|train}}**: On-the-fly training**
Force predictions from the machine learning force field are used to drive the molecular dynamics (MD) simulation. However, if the error estimation performed in each time step indicates a high force error an ab initio calculation is performed instead and the collected energy, forces, and stress are used to improve the machine learning force field. There are two possible cases depending on, whether an {{TAG|ML_AB}} is present in the calculation folder or not:
<ol>
<li>
No {{FILE|ML_AB}} file found:
On-the-fly training is starting from scratch. Note that at the beginning of the MD run, when there is no force field available or it is still poorly trained, *ab initio* calculations will happen frequently. For VASP versions prior to 6.4.0 this corresponds to {{TAG|ML_ISTART|0}}.
</li>
<li>
{{FILE|ML_AB}} file present:
Restart on-the-fly training from existing training database. Before the MD run starts the {{FILE|ML_AB}} file (a copy of the {{FILE|ML_ABN}} from a previous training run!) is read and the *ab initio* data (energies, forces, and stresses) and local reference configurations it contains are used to generate an initial force field. Subsequently, the on-the-fly training MD is started. For VASP versions prior to 6.4.0 this corresponds to {{TAG|ML_ISTART|1}}.{{NB|tip|None of the structures in the {{FILE|ML_AB}} file need to match he {{FILE|POSCAR}} file for the current MD training run in terms of the simulation box, elements, or number of atoms. However, if the same elements appear the initial force field is used for predictions in the current MD run.

The training data contained in the {{FILE|ML_AB}} file is included in the final machine learning force field, i.e., the {{FILE|ML_FFN}} file will define a force field applicable to both the structures on the {{FILE|ML_AB}} file as well as to the current MD simulation. This means that by restarting repeatedly with {{TAG|ML_MODE|train}}, and copying the {{FILE|ML_ABN}} file from the previous run to {{FILE|ML_AB}}(!), it is possible to iteratively extend the applicability of the a machine learning force field, e.g., by exploring different temperature ranges or element compositions.}}
</li>
</ol>
</li>
<li>
{{TAG|ML_MODE|select}}**: Re-selection of local reference configurations**
A new machine learning force field is generated from the *ab initio* data provided in the {{FILE|ML_AB}} file. The structures are read and processed one by one as if harvested in an MD simulation. In other words, the same steps are performed as in on-the-fly training but the source of the data are not actual *ab initio* calculations in an MD run but the series of structures available in the {{FILE|ML_AB}} file. The list of local reference configurations on the {{FILE|ML_AB}} file will be ignored. Instead a new collection of local reference configurations is determined and written to the resulting {{FILE|ML_ABN}} file.
{{NB|important|This operation mode allows to generate a {{VASP}} machine learning force field from pre-computed or external *ab initio* data sets. In contrast to {{TAG|ML_MODE|refit}} also the local reference configurations are selected from the entire data set. For example, an {{FILE|ML_AB}} file created manually by extracting *ab initio* data (energies, forces, stresses) from {{FILE|OUTCAR}} files (or even other external sources) can be processed in this mode without prior knowledge of local reference configurations (only a dummy section must be added to the {{FILE|ML_AB}} file, see its documentation). Similar to on-the-fly training this mode generates {{FILE|ML_FFN}} files and {{FILE|ML_ABN}} **with** local reference configurations.}}
A new iteration through the training structures can lead to a frequent update of the force field. This is quite time-consuming. Hence, for this mode the default value of {{TAG|ML_CDOUB}} is automatically increased from 2 to 4 which will result in a much less frequent update of the force field. This leads to much more efficient calculations while practically not changing the results.
{{NB|tip|If calculations for {{TAG|ML_MODE|select}} are too time-consuming, it is useful to increase {{TAG|ML_MCONF_NEW}} to values around 10-16. Together with {{TAG|ML_CDOUB|4}}, this often accelerates the calculations by a factor of 2-4.}}
The {{FILE|ML_AB}} file may contain values for CTIFOR for each training structure. These are the thresholds used to sample that structure from the previous training. The thresholds found on the {{FILE|ML_AB}} will be re-used unless a threshold is explicitly specified in the {{FILE|INCAR}} file, by means of the {{TAG|ML_CTIFOR}} tag. In the latter case the thresholds from the {{TAG|ML_AB}} file are ignored. In case the {{FILE|ML_AB}} contains **no** CTIFOR information and **no** threshold is specified in the {{FILE|INCAR}} file, the default value for {{TAG|ML_CTIFOR}} is used.
This mode automatically sets {{TAG|NSW|1}} and {{TAG|ML_CDOUB|4}}.For VASP versions prior to 6.4.0 this corresponds to {{TAG|ML_ISTART|3}}.
{{NB|warning|{{TAG|ML_MODE|select}} ignores the structure in the {{TAG|POSCAR}} and hence no error, force and stress predictions are made at the end of this calculation (instead zeros are written to stdout, {{TAG|OSZICAR}} and {{TAG|OUTCAR}}).}}
</li>
<li>{{TAG|ML_MODE|refit}}**: Refit a force field for "fast" evaluation**
Similar to {{TAG|ML_MODE|select}}, refitting is done based on an existing {{TAG|ML_AB}} file, but the number of local reference configurations for each species is taken from the {{TAG|ML_AB}} file. Sparsification is performed on the local reference configurations, so the resulting {{TAG|ML_ABN}} file will contain the same number or fewer local reference configurations than the {{TAG|ML_AB}} file.
By default the resulting force field is geared towards "fast" evaluation to speed up production runs ({{TAG|ML_LFAST|.TRUE.}}). This comes at the cost of not being able to evaluate Bayesian error estimates.
{{NB|warning|We strongly advise to use {{TAG|ML_MODE|refit}} if no Bayesian error estimates are required during production runs.}}
This mode automatically sets {{TAG|ML_LFAST|.TRUE.}}, {{TAG|NSW|1}}, {{TAG|ML_IALGO_LINREG|4}}, {{TAG|ML_SIGW0|1E-7}}, {{TAG|ML_SIGV0|1}} and {{TAG|ML_EPS_LOW|1E-11}}. For VASP versions prior to 6.4.0 this corresponds to {{TAG|ML_ISTART|4}}.
</li>
<li>{{TAG|ML_MODE|refitbayesian}}**: Refit a force field with Bayesian regression (deprecated)**
Same as {{TAG|ML_MODE|refit}}, but Bayesian regression is employed. This results in lower accuracy and much slower force fields than using {{TAG|ML_MODE|refit}} and should be used with caution. On the other hand, this mode allows the generation of {{TAG|ML_FFN}} files that can calculate Bayesian error estimates in addition to predictions.
This modes sets {{TAG|NSW|1}}, {{TAG|ML_IALGO_LINREG|1}} and {{TAG|ML_LFAST|.FALSE.}}. For VASP versions prior to 6.4.0 this corresponds to {{TAG|ML_ISTART|4}}.
</li>
<li>{{TAG|ML_MODE|run}}**: Perform only force field predictions**
A previously trained machine learning force field is read from the {{FILE|ML_FF}} file, and the MD simulation is driven with predictions from the force field only. **No** *ab initio* calculations are performed and **no** learning is executed. This setting is typically used when the machine learning force field is considered mature and ready for production runs.
Optionally, if the force field was refitted using {{TAG|ML_MODE|refitbayesian}}, the Bayesian error estimate of the energies, forces, and stress can be computed and logged in the {{FILE|ML_LOGFILE}}. The output frequency of the Bayesian errors can be set via the {{TAG|ML_IERR}} tag, the default is 0.
For VASP versions prior to 6.4.0 this corresponds to {{TAG|ML_ISTART|2}}.
<li>{{TAG|ML_MODE|delta}}**: Performs ab-initio calcutions and force field predictions**
A previously trained machine learning force field is read from the {{FILE|ML_FF}} file, and the MD simulation is driven by the sum of *ab initio* forces and machine learning predictions. The machine learning force field ideally has been trained to predict the difference between two levels of *ab initio* theory — referred to as the target and reference levels — so that the combined result approximates the target level of theory at the computational cost of the reference level.
Typical use cases include correcting a low-cost exchange-correlation functional (e.g., PBE) toward a higher-accuracy one (e.g., a hybrid functional such as HSE06), or bridging differences in k-mesh density, plane-wave energy cutoff, or other convergence parameters. In this way, near-hybrid accuracy can be achieved at a cost approaching that of a semi-local DFT calculation.
This mode is available for VASP version 6.6.0 or higher.
</li>
<li>{{TAG|ML_MODE|none}}**: The tag is ignored**
</ul>
{{NB|warning|If any option other than the above is chosen or there is a spelling error (be careful to write everything in upper case or lower case letters) the code will exit with an error.}}
{{NB|tip|Some choices of {{TAG|ML_MODE}} will automatically set other machine-learned force field tags. However, it is still possible to overwrite the defaults by specifying the corresponding tags in the {{FILE|INCAR}} file.}}
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_ISTART}}, {{TAG|ML_LFAST}}, {{TAG|ML_IERR}}, {{TAG|ML_OUTBLOCK}}, {{TAG|ML_OUTPUT_MODE}}, {{TAG|ML_IALGO_LINREG}}, {{TAG|ML_MCONF_NEW}}, {{TAG|ML_CDOUB}}, {{TAG|ML_CTIFOR}}, {{TAG|ML_IERR}}
----

Category:INCAR tagCategory:Machine-learned force fields
