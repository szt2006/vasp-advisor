{{DISPLAYTITLE:LNICSALL}}
{{TAGDEF|LNICSALL|.TRUE. {{!}} .FALSE.|.FALSE.}}

Description: {{TAG|LNICSALL}}=.TRUE. calculates the NICS at the positions on the fine FFT grid {{TAG|NGXF}} x {{TAG|NGYF}} x {{TAG|NGZF}}.
{{Available|6.6.0}}
----
{{TAG|LNICSALL}}=.TRUE. ensures that the FFT grid {{TAG|NGXF}} x {{TAG|NGYF}} x {{TAG|NGZF}} is used to calculate the NICS (nucleus-independent chemical shift) points. These chemical shieldings will be printed to {{FILE|NICS}}.
{{NB|mind|If {{TAG|LNICSALL|True}} is set, and {{FILE|POSNICS}} is also present, {{TAG|LNICSALL}} will take precedent.}}
## Related tags and articles
{{FILE|LCHIMAG}},
{{TAG|NUCIND}},
{{TAG|NICS}},
tutorial (https://www.vasp.at/tutorials/latest/nmr/part3/#NMR-e11) 

Category:INCAR tagCategory:NMR
