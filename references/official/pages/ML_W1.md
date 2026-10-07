{{DISPLAYTITLE:ML_W1}}
{{TAGDEF|ML_W1|[real]|0.1}}

Description: This tag defines the weight \beta for the radial (and angular) descriptor within the machine learning force field method (see this section).
----
The weight for the angular descriptor W_{2} is internally computed from the weight of the radial descriptor W_{1} as:

W_{2}=1.0-W_{1}.

The value for {{TAG|ML_W1}} must be chosen in the interval [0, 1].

By default, the angular and radial descriptors are both used although the latter is weighed less. In principle a weight of 0 for one of them is selectable which allows the code to internally skip the respective computation. However, it is generally recommended to use both descriptors to achieve satisfying training results.
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_RCUT1}}, {{TAG|ML_RCUT2}}, {{TAG|ML_SION1}}, {{TAG|ML_SION2}}

{{sc|ML_W1|Examples|Examples that use this tag}}
----

Category:INCAR tagCategory:Machine-learned force fields
