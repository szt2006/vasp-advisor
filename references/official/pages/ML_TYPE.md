{{DISPLAYTITLE:ML_TYPE}}
{{TAGDEF|ML_TYPE|kernel {{!}} vasp {{!}} grace | kernel}}

Description: String-based tag selecting type of machine-learned force field to use. {{available|6.6.0}}
----
Given that machine-learned force fields are enabled ({{TAG|ML_LMLFF|.TRUE.}}) this tag selects which type of force field is used.

<ul>
<li>{{TAG|ML_TYPE|kernel, vasp}}: Use {{VASP}}'s native machine-learned force fields with theoretical background described here. The strings kernel and vasp are synonymous in this context.
<li>{{TAG|ML_TYPE|grace}}: Use GRACE force fields, available only for {{TAG|ML_MODE|run}} if GRACE support is enabled at compile time.
</ul>
## Related tags and articles
{{TAG|ML_LMLFF}}, {{TAG|ML_MODE}}, {{TAG|ML_GRACE_MODEL}}
----

Category:INCAR tagCategory:Machine-learned force fields
