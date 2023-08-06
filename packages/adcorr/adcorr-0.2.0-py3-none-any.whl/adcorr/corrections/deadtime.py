from typing import Any, cast

from numpy import (
    atleast_1d,
    complexfloating,
    dtype,
    expand_dims,
    floating,
    ndarray,
    number,
)
from scipy.special import lambertw

from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames, VectorOrSingle


def correct_deadtime(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    count_times: ndarray[VectorOrSingle[NumFrames], dtype[floating]],
    minimum_pulse_separation: float,
    minimum_arrival_separation: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Correct for detector deadtime by scaling counts to account for overlapping events.

    Correct for detector deadtime by iteratively solving for the number of incident
    photons required to produce the observed value in a given time period subject to
    detector characteristics, as detailed in section 3.3.4 of 'Everything SAXS: small-
    angle scattering pattern collection and correction'
    [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        frames: A stack of frames to be corrected.
        count_times: The period over which photons are counted for each frame.
        minimum_pulse_separation: The minimum time difference required between a prior
            pulse and the current pulse for the current pulse to be recorded correctly.
        minimum_arrival_separation: The minimum time difference required between the
            current pulse and a subsequent pulse for the current pulse to be recorded
            correctly.

    Returns:
        The corrected stack of frames.
    """
    if (count_times <= 0).any():
        raise ValueError("Count times must be positive.")
    if minimum_pulse_separation < 0:
        raise ValueError("Minimum Pulse Separation must be non-negative.")
    if minimum_arrival_separation < 0:
        raise ValueError("Minimum Arrival Separation must be non-negative.")

    if minimum_pulse_separation == 0 and minimum_arrival_separation == 0:
        return frames

    deadtime_proportion = expand_dims(
        atleast_1d(
            (minimum_pulse_separation + minimum_arrival_separation) / count_times
        ),
        (1, 2),
    )
    return (
        -cast(
            ndarray[Any, dtype[complexfloating]],
            lambertw(-deadtime_proportion * frames),
        ).real
        / deadtime_proportion
    )
