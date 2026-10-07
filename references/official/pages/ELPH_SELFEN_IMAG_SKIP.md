{{DISPLAYTITLE:ELPH_SELFEN_IMAG_SKIP}}
{{TAGDEF|ELPH_SELFEN_IMAG_SKIP|[logical]| .FALSE.}}

Description:  
Use the tetrahedron method to skip the computation of electron-phonon matrix elements for which the energy-conserving delta functions are zero.  
{{Available|6.5.0}}
----
It is strongly recommended to enable this option when only the imaginary part of the electron self-energy (linewidths) are required, for instance in transport or scattering rate calculations.  
Using this tag can reduce the computational cost by orders of magnitude, depending on the electronic band structure.

When using this option, it is also recommended to set {{TAG|ELPH_WF_REDISTRIBUTE}} = .TRUE.
## Related tags and articles
{{TAG|ELPH_WF_REDISTRIBUTE}},
{{TAG|ELPH_SCATTERING_APPROX}},
{{TAG|ELPH_RUN}}, 
((TAG|ELPH_SELFEN_G_SKIP}}

Category:INCAR tagCategory:Electron-phonon_interactions
