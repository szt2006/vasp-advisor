{{DISPLAYTITLE:ELPH_SELFEN_BAND_STOP_KP}}
{{TAGDEF|ELPH_SELFEN_BAND_STOP_KP|[integer]|-1}}

Description: Index of the last k' band included in the electron self-energy sum; -1 uses all bands up to {{TAG|ELPH_NBANDS}}, and -2 activates automatic determination based on energy conservation.
{{Available|6.6.0}}

----
The Fan-Migdal self-energy involves a sum over intermediate scattering states at k' = k + q:

:\Sigma^{\text{FM}}_{n\mathbf{k}}(T) = \frac{1}{N_q}\sum_{m\nu\mathbf{q}} |g_{mn\mathbf{k},\nu\mathbf{q}}|^2 \left[\frac{\cdots}{\varepsilon_{n\mathbf{k}} - \varepsilon_{m\mathbf{k}+\mathbf{q}} \pm \omega_{\nu\mathbf{q}} + i\delta}\right]

{{TAG|ELPH_SELFEN_BAND_START_KP}} and {{TAG|ELPH_SELFEN_BAND_STOP_KP}} control the range of band indices m (at k') included in this sum.
This is distinct from {{TAG|ELPH_SELFEN_BAND_START}} and {{TAG|ELPH_SELFEN_BAND_STOP}}, which select the bands v at kfor which the self-energy is computed.

The following values are accepted:

* -1 (default): include all bands up to {{TAG|ELPH_NBANDS}}.
* -2: determine the upper bound automatically from energy conservation. Only k' bands whose eigenvalues fall within ±ωmax of the target k bands are included, where ωmax is the maximum phonon energy. This can significantly reduce the cost when {{TAG|ELPH_NBANDS}} is large.
* Positive integer: use the specified band index as the upper bound.

Setting both {{TAG|ELPH_SELFEN_BAND_START_KP}} and {{TAG|ELPH_SELFEN_BAND_STOP_KP}} to -2 is recommended when a large number of bands is required for convergence but most of them lie far from the relevant energy window.
## Related tags and articles
* {{TAG|ELPH_SELFEN_BAND_START_KP}}
* {{TAG|ELPH_SELFEN_BAND_STOP}}
* {{TAG|ELPH_NBANDS}}
* {{TAG|ELPH_RUN}}

Category:INCAR tagCategory:Electron-phonon_interactions
