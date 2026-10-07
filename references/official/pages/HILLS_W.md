{{DISPLAYTITLE:HILLS_W}}{{TAGDEF|HILLS_W|[Real]|10^{-3}}}

Description: {{TAG|HILLS_W}} specifies the width of the Gaussian hill (in units of the corresponding collective variable) used in metadynamics (in case VASP was compiled with -Dtbdyn).
----
In metadynamics ({{TAG|MDALGO}}=11 {{!}} 21), the bias potential is given as 
:
\tilde{V}(t,\xi) = h \sum_{i=1}^{\lfloor t/t_G \rfloor} \exp{\left\{ -\frac{|\xi^{(t)}-\xi^{(i \cdot t_G)}|^2}{2
w^2} \right\}}.

Thre parameters ({{TAG|HILLS_H}}, {{TAG|HILLS_W}}, and {{TAG|HILLS_BIN}}) must be provided by the user.

The width of the Gaussian hills  w (in units of the corresponding collective variable) is set by {{TAG|HILLS_W}}.
## Related tags and articles
Metadynamics,
{{TAG|HILLS_H}},
{{TAG|HILLS_BIN}},
{{FILE|HILLSPOT}},
{{TAG|MDALGO}}

{{sc|HILLS_W|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Advanced molecular-dynamics sampling
