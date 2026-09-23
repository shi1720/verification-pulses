# Post-analysis diagnostic: terminal distribution versus mean

2026-09-23, after all 108 episodes and the four primary contrasts were analyzed.

All four adjusted primary intervals include zero. No sample extension,
replacement model, new API calls, or change in the primary comparisons is made.

The prediction audit is extended to report all-correct and all-wrong terminal
probabilities, because nano's observed endpoint occupancy is much larger than
the pooled response model predicts despite modest mean-trajectory error.
This is an explicitly post-analysis diagnostic. Propagate 5,000 whole-task
calibration bootstrap coefficient sets through the exact finite-state kernel
(seed 209231), reporting pointwise 95% intervals for predicted endpoint
occupancy. These describe calibration uncertainty in the pooled model, not
simultaneous coverage or a formal model-rejection test. All six model/schedule
cells are retained. No trajectory observations are used to fit the response.
