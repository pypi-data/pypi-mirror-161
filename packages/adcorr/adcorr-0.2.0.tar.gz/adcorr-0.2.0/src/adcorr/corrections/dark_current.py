from numpy import atleast_1d, dtype, expand_dims, floating, ndarray, number

from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames, VectorOrSingle


def correct_dark_current(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    count_times: ndarray[VectorOrSingle[NumFrames], dtype[floating]],
    base_dark_current: float,
    temporal_dark_current: float,
    flux_dependant_dark_current: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Correct by subtracting base, temporal and flux-dependant dark currents.

    Correct for incident dark current by subtracting a baselike, time dependant and a
    flux dependant count rate from frames, as detailed in section 3.3.6 of 'Everything
    SAXS: small-angle scattering pattern collection and correction'
    [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        frames: A stack of frames to be corrected.
        count_times: The period over which photons are counted for each frame.
        base_dark_current: The dark current flux, irrespective of time.
        temporal_dark_current: The dark current flux, as a factor of time.
        flux_dependant_dark_current: The dark current flux, as a factor of incident
            flux.

    Returns:
        The corrected stack of frames.
    """
    if (count_times <= 0).any():
        raise ValueError("Count times must be positive.")
    if base_dark_current < 0:
        raise ValueError("Base Dark Current must be non-negative.")
    if temporal_dark_current < 0:
        raise ValueError("Temporal Dark Current must be non-negative.")
    if flux_dependant_dark_current < 0:
        raise ValueError("Flux Dependant Dark Current must be non-negative.")

    temporal = temporal_dark_current * expand_dims(atleast_1d(count_times), (1, 2))
    flux_dependant = flux_dependant_dark_current * frames
    return frames - base_dark_current - temporal - flux_dependant
