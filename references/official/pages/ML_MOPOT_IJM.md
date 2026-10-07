{{DISPLAYTITLE:ML_MOPOT_IJM}}
{{TAGDEF|ML_MOPOT_IJM|[integer array]|none}}

Description: Specifies the list of Morse potential pairs used as auxiliary potentials in thermodynamic integration ({{TAG|VCAIMAGES}}).
----
This parameter specifies the pairs for which the following Morse potential will be used

V(r) = D_e (1-e^{-\beta(r-r_{e})})^2 - 1.

The number of pairs must be equal to {{TAG|ML_MOPOT_NM}}. Each pair is defined with the atom indices from the POSCAR file one after the other.

**Example**:
 {{TAG|ML_MOPOT_NM}} = 3
 {{TAG|ML_MOPOT_IJM}} = 7 8 10 11 13 14
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_LCOUPLE}}, {{TAG|ML_ICOUPLE}}, {{TAG|ML_RCOUPLE}}, {{TAG|ML_NATOM_COUPLED}}, 
{{TAG|ML_LEMPPOT}}, {{TAG|ML_EMPPOT_RCUT}}, {{TAG|ML_SRPOT_B0}}, {{TAG|ML_SRPOT_N0}}, 
{{TAG|ML_SRPOT_S0}}, {{TAG|ML_MOPOT_NM}}, {{TAG|ML_MOPOT_DM}}, 
{{TAG|ML_MOPOT_RM}}, {{TAG|ML_MOPOT_RKM}}

{{sc|ML_LCOUPLE|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
