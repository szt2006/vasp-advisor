{{DISPLAYTITLE:LNMRLEG}}
{{TAGDEF|LNMRLEG|.TRUE.{{!}} .FALSE.}}

{{DEF|LNMRLEG|.FALSE.|}}
{{Available|6.6.0}}

Description: {{TAG|LNMRLEG}} controls whether VASP prints NMR properties to {{FILE|OUTCAR}} according to the old format (pre-version 6.6.0).
----

In version 6.6.0, the output format for NMR properties was updated. The legacy format is as presented below (see {{TAG|LCHIMAG}} for the current version). The chemical shielding tensors, UNSYMMETRIZED TENSORS and SYMMETRIZED TENSORS are printed. From the three diagonal values of the symmetrized tensor, the isotropic chemical "shift" \delta_{\mathrm{iso}}\mathrm{[VASP]}, span \Omega, and skew \kappa are calculated and printed, see Ref. {{Cite|mason:ssn:1993}} for unambiguous definitions. Note that \kappa is ill-defined if \Omega = 0. Units are ppm, except for the skew. A typical output is given below:

                                                                                                          
   ---------------------------------------------------------------------------------
    CSA tensor (J. Mason, Solid State Nucl. Magn. Reson. 2, 285 (1993))
   ---------------------------------------------------------------------------------
               EXCLUDING G=0 CONTRIBUTION             INCLUDING G=0 CONTRIBUTION
           -----------------------------------   -----------------------------------
    ATOM    ISO_SHIFT        SPAN        SKEW     ISO_SHIFT        SPAN        SKEW
   ---------------------------------------------------------------------------------
    (absolute, valence only)
       1    4598.8125      0.0000      0.0000     4589.9696      0.0000      0.0000
       2     291.5486      0.0000      0.0000      282.7058      0.0000      0.0000
       3     736.5979    344.8803      1.0000      727.7550    344.8803      1.0000
       4     736.5979    344.8803      1.0000      727.7550    344.8803      1.0000
       5     736.5979    344.8803      1.0000      727.7550    344.8803      1.0000
   ---------------------------------------------------------------------------------
    (absolute, valence and core)
       1   -6536.1417      0.0000      0.0000    -6547.9848      0.0000      0.0000
       2   -5706.3864      0.0000      0.0000    -5718.2296      0.0000      0.0000
       3   -2369.4015    344.8803      1.0000    -2381.2446    344.8803      1.0000
       4   -2369.4015    344.8803      1.0000    -2381.2446    344.8803      1.0000
       5   -2369.4015    344.8803      1.0000    -2381.2446    344.8803      1.0000
   ---------------------------------------------------------------------------------
    IF SPAN.EQ.0, THEN SKEW IS ILL-DEFINED
   ---------------------------------------------------------------------------------

The isotropic chemical shielding for each atom, excluding and including G=0 contributions, as well as the span and skew (descriptions of asymmetry), follow. Finally, core contributions are taken into account for the ISO_SHIFT, SPAN, and SKEW. 
{{NB|important|
*The columns excluding the \mathbf{G=0} contribution are useful for supercell calculations on molecules.
*The columns including the \mathbf{G=0} contribution are for crystals.
*The upper block gives the shielding due to only the electrons included in the SCF calculation.
*The lower block has the contributions due to the frozen PAW cores added. These core contributions are rigid  {{Cite|gregor:jcp:1999}}. They depend on {{FILE|POTCAR}} and are isotropic, i.e. affect neither SPAN nor SKEW.}}
{{NB|mind|In legacy mode, the chemical shift (the negative of the chemical shielding) is always printed, even if {{TAG|LNMRSHIELD}} {{=}} .TRUE..}}
## Related tags and articles
{{TAG|LCHIMAG}}, {{TAG|INMRPRINT}}
## References
Category:INCAR tagCategory:NMR
