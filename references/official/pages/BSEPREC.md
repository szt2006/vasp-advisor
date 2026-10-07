{{TAGDEF|BSEPREC|Low {{!}} Medium {{!}} High {{!}}  Accurate | Medium}}

Description: Determines the precision of the time-evolution algorithm, where it controls the timestep and the number of steps, and the precision of the Lanczos algorithms, where it sets the convergence threshold for the dielectric function. 

-----
## Time-evolution algorithm
The timestep in the time-evolution calculation is inversely proportional to the maximum transition energy {{TAG|OMEGAMAX}} and the number of steps is inversely proportional to the broadening {{TAG|CSHIFT}}. Depending on the {{TAG|BSEPREC}}  stable these parameters are scaled depending on the precision tag {{TAG|BSEPREC}}.

::{| cellpadding="5" cellspacing="5" style="width: 50%; border-spacing: 5px;"
  style="text-align:center; background-color:#DEC4EB;"| {{TAG|BSEPREC}} || style="text-align:center; background-color:#DEC4EB;"| {{TAG|OMEGAMAX}} || style="text-align:center; background-color:#DEC4EB;"| {{TAG|CSHIFT}}
  style="background-color:#D9F8F5;"| Accurate (a) ||style="background-color:#D9F8F5;"| \times 4 ||style="background-color:#D9F8F5;"| \times 1/10 
  style="background-color:#D9F8F5;"| High (h) ||style="background-color:#D9F8F5;"| \times 3 ||style="background-color:#D9F8F5;"| \times 1/7.5 
  style="background-color:#D9F8F5;"| Medium (m) ||style="background-color:#D9F8F5;"| \times 2.5 ||style="background-color:#D9F8F5;"| \times1/6.25
  style="background-color:#D9F8F5;"| Low (l)  ||style="background-color:#D9F8F5;"| \times 2 ||style="background-color:#D9F8F5;"| \times1/5

For example, the number of steps N_{\rm steps} for {{TAG|BSEPREC}} = Low can be found via N_{\rm steps}=\frac{{\rm OMEGAMAX}\times 2}{{\rm CSHIFT}/5}
## Lanczos algorithm
{{NB|mind|Replaces {{TAG|LANCZOSTHR}} as of version 6.5.1}}
The Lanczos algorithm stops once the imaginary part of the dielectric function computed in two consecutive iterations differs bellow a certain threshold for the root-mean-square, i.e. once after n iterations the value of 

::
\mathrm{RMS}[\epsilon_n] = \sqrt{\frac{1}{N_\omega}\sum_{i=1}^{N_\omega}\left(\Im[\epsilon_n(\omega_i)]-\Im[\epsilon_{n-1}(\omega_i)]\right)^2}

is below a certain value defined by **BSEPREC**.

::{| cellpadding="5" cellspacing="5" style="width: 50%; border-spacing: 5px;"
  style="text-align:center; background-color:#DEC4EB;"|  BSEPREC || style="text-align:center; background-color:#DEC4EB;"| \mathrm{RMS}[\epsilon_n] 
  style="background-color:#D9F8F5;"| Accurate (a) ||style="background-color:#D9F8F5;"| 10^{-5} 
  style="background-color:#D9F8F5;"| High (h) ||style="background-color:#D9F8F5;"| 10^{-4}  
  style="background-color:#D9F8F5;"| Medium (m) ||style="background-color:#D9F8F5;"| 10^{-3} 
  style="background-color:#D9F8F5;"| Low (l)  ||style="background-color:#D9F8F5;"| 10^{-2} 

To prevent the algorithm from being too slow, the number of frequencies during the convergence loop is set to N_\omega = INT(SQRT(NOMEGA)), where {{TAG|NOMEGA}} is set in the {{TAG|INCAR}}.
## Related tag and articles
{{TAG|IBSE}},
{{TAG|NBANDSV}},
{{TAG|NBANDSO}},
{{TAG|CSHIFT}},
{{TAG|OMEGAMAX}}

BSE calculations

Time-dependent density-functional theory calculations

Bethe-Salpeter equations

----
Category:INCAR tag Category:Many-body perturbation theoryCategory:Bethe-Salpeter equations
