{{DISPLAYTITLE:ELPH_TRANSPORT_EMAX_PLOT}}
{{TAGDEF|ELPH_TRANSPORT_EMAX_PLOT|[real]| \max(\varepsilon_{n\mathbf{k}})+5}}

Description:  
Specifies the maximum energy (in eV) to be considered when computing the  transport distribution function for plotting.  
{{Available|6.5.0}}
----

By default, the upper energy limit is set to \max(\varepsilon_{n\mathbf{k}}) + 5 eV, where \varepsilon_{n\mathbf{k}} are the electronic eigenvalues computed in the k-point mesh defined by the {{FILE|KPOINTS_ELPH}} file.
The transport function for plotting is evaluated on a linear energy grid of energies between {{TAG|ELPH_TRANSPORT_EMIN_PLOT}} and {{TAG|ELPH_TRANSPORT_EMAX_PLOT}} and with {{TAG|ELPH_TRANSPORT_NEDOS_PLOT}} points.  
The transport function for plotting is computed additionally to the one that is used to evaluate the  Onsager coefficients but allows choosing a different energy range, thus not compromising the accuracy of the transport calculations.

The transport function and corresponding energy grids are written to {{FILE|vaspout.h5}}

 $ h5ls -r vaspout.h5 | grep plot
 /results/electron_phonon/electrons/transport_1/energy_plot Dataset {501}
 /results/electron_phonon/electrons/transport_1/transport_function_plot Dataset {7, 1, 3, 3, 501}
## Related tags and articles
* {{TAG|ELPH_TRANSPORT}}
* {{TAG|ELPH_TRANSPORT_EMIN_PLOT}}
* {{TAG|ELPH_TRANSPORT_NEDOS_PLOT}}
* {{TAG|ELPH_SCATTERING_APPROX}}
* {{TAG|TRANSPORT_RELAXATION_TIME}}
Category:INCAR tagCategory:Electron-phonon_interactions
