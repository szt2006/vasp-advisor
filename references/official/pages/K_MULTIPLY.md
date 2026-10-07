{{DISPLAYTITLE:K_MULTIPLY}}
{{TAGDEF|K_MULTIPLY|[integer array]}}
{{DEF|K_MULTIPLY|-1 -1 -1|if not set in {{FILE|INCAR}}}}

Description: {{TAG|K_MULTIPLY}} sets the per-direction k-point grid multiplier for downsampling from a denser {{FILE|WAVECAR}}
----

{{TAG|K_MULTIPLY}} specifies the ratio between the denser k-point grid stored in the {{FILE|WAVECAR}} (or {{FILE|vaspwave.h5}}) and the coarser grid of the current calculation, for each of the three reciprocal-lattice directions independently.

When {{TAG|K_MULTIPLY}} is set, {{TAG|LDOWNSAMPLE}} is automatically set to {{TAGO|LDOWNSAMPLE|.TRUE.}}.

By default, {{TAG|LDOWNSAMPLE}} triggers an automatic search that tries the *same* multiplier in all three directions. This works for isotropic grids but fails for anisotropic ones, e.g., when the {{FILE|WAVECAR}} contains a 24&times;24&times;1 grid and the current calculation uses a 2&times;2&times;1 grid (requiring multipliers 12, 12, 1). In such cases, {{TAG|K_MULTIPLY}} must be set explicitly.
{{NB| tip | For isotropic grids the automatic search is fast and {{TAG|K_MULTIPLY}} is not required. Use {{TAG|K_MULTIPLY}} when the grid ratio differs between directions.}}
{{Available|6.6.1}}
## Usage
### Single value
 K_MULTIPLY = 2
The value is replicated to all three directions, equivalent to K_MULTIPLY = 2 2 2.
### Three values (anisotropic)
 K_MULTIPLY = 12 12 1
Each value specifies the multiplier for the first, second, and third reciprocal-lattice direction, respectively. This is required when the dense-to-coarse grid ratio is not the same in every direction.
{{NB| warning | All values must be positive integers. Providing any number of values other than 1 or 3 will cause an error.}}
## Related tags and articles
{{TAG|LDOWNSAMPLE}}

{{sc|K_MULTIPLY|Examples|Examples that use this tag}}
## References
Category:INCAR tagCategory:Wannier functionsCategory:Constrained-random-phase approximationCategory:Many-body perturbation theory
