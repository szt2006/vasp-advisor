{{TAGDEF|ISEARCH|0 {{!}} 1|0}}

Description: Controls the line-search algorithm used during the direct minimization of the electronic structure ({{TAG|ALGO|All}}).
----
*{{TAG|ISEARCH|0}}: Legacy line-search algorithm.
*{{TAG|ISEARCH|1}}: Improved line-search algorithm.

The line search determines the optimal step size along the conjugate gradient search direction. {{TAG|ISEARCH|0}} performs incremental steps along the search direction. It may lead to inconsistencies in total energy evaluations and slower convergence. {{TAG|ISEARCH|1}} introduces a more robust and consistent method for determining the optimal step size, leading to improved convergence behavior and more reliable energy minimization.
{{NB|important|We recommend {{TAG|ISEARCH|1}} when performing electronic minimizations with {{TAG|ALGO}} {{=}} All, as it generally improves convergence stability and reduces the total number of required SCF steps.}}
{{NB|mind|{{TAG|ISEARCH|0}} should only be used for backward compatibility or benchmarking against legacy behavior.}}
## Improved line-search algorithm (ISEARCH = 1)
The improved algorithm introduces several technical enhancements over the legacy implementation to ensure more robust convergence:

* **Absolute Reference**: Each line search step is calculated from the origin of the search direction rather than progressing incrementally. This maintains energy consistency and reduces cumulative rounding errors.
* **Intelligent Slot System**: Trial steps are managed through a "slot-in" mechanism. This system avoids redundant evaluations and strategically places new probes near the predicted minimum to provide the curvature data needed for higher-order fits.
* **Adaptive Fitting Logic**: The algorithm scales complexity based on the data density:
** *Low density (≤ 5 points)*: Uses a combined Harmonic (2nd-order) and 4th-order polynomial fit. The 4th-order result is only accepted if it is consistent with the harmonic direction.
** *High density (> 5 points)*: Employs Cubic Spline interpolation, which is more robust against the oscillations often found in high-order polynomials.
* **Hybrid Gradient-Energy Correction**: While primarily using energy, the algorithm monitors the slope. If the slope at the new point suggests the minimum was missed, it applies a Harmonic Correction to rescale the step length before attempting a polynomial fit.
* **Concave Safety Descent**: If the second derivative of the fit is negative (indicating a "hill" rather than a "valley"), the algorithm ignores the fit and automatically reverts to the step that yielded the lowest energy evaluation recorded in the current search.
## Related tags and articles
{{TAG|ALGO}}

Category:INCAR tagCategory:Electronic minimization
