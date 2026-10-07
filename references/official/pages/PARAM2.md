{{TAGDEF|PARAM2|[real]|1.0}}

Description: \kappa for {{TAG|GGA}}=MK, or \mu for {{TAG|GGA}}=BO.
----

The {{TAG|PARAM2}} tag determines the value corresponding to different parameters depending on the {{TAG|GGA}} functional that is chosen:
*\kappa in the optB86b{{cite|klimes:prb:2011}} (\kappa is not shown in this work since implicitly set to 1.0), B86R{{cite|hamada:prb:2014}}, and DF3-opt2{{cite|chakraborty:jctc:2020}} exchange functionals, which have the same analytical form and correspond to {{TAG|GGA}}=MK. {{TAG|PARAM2}} should in principle be set to 1.0 for the nonlocal optB86b-vdW functional{{cite|klimes:prb:2011}}, to 0.711357 for the nonlocal rev-vdW-DF2{{cite|hamada:prb:2014}} functional, or to 0.58 for the vdW-DF3-opt2 nonlocal functional{{cite|chakraborty:jctc:2020}}.
*\mu in the optB88{{cite|klimes:jpcm:2010}} and DF3-opt1{{cite|chakraborty:jctc:2020}} exchange functionals, which have the same analytical form and correspond to {{TAG|GGA}}=BO. {{TAG|PARAM2}} should in principle be set to 0.22 for the nonlocal optB88-vdW functional{{cite|klimes:jpcm:2010}} or to 10/81\approx0.1234568 for the vdW-DF3-opt1{{cite|chakraborty:jctc:2020}} nonlocal functional.

The complete {{TAG|INCAR}} file for the nonlocal van der Waals functionals mentioned above can be found at {{TAG|Nonlocal vdW-DF functionals}}.
## Related tags and articles
{{TAG|PARAM1}}, {{TAG|GGA}}, {{TAG|Nonlocal vdW-DF functionals}}

{{sc|PARAM2|Examples|Examples that use this tag}}
## References
Category:INCAR tagCategory:Exchange-correlation functionalsCategory:van der Waals functionals
