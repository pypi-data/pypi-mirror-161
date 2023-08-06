from typing import Tuple, cast

from numpy import (
    broadcast_to,
    cos,
    divide,
    dtype,
    expand_dims,
    floating,
    log,
    logical_and,
    ndarray,
    number,
    ones_like,
    power,
)

from ..utils.geometry import scattering_angles
from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames, VectorOrSingle


def correct_self_absorption(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    incident_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    transmitted_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    beam_center: Tuple[float, float],
    pixel_sizes: Tuple[float, float],
    distance: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Correct for transmission loss due to differences in observation angle.

    Correct for transmission loss due to differences in observation angle, as detailed
    in section 3.4.7 of 'Everything SAXS: small-angle scattering pattern collection and
    correction' [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        frames: A stack of frames to be corrected.
        incident_flux: The flux intensity observed upstream of the sample.
        transmitted_flux: The flux intensity observed downstream of the sample.
        beam_center: The center position of the beam in pixels.
        pixel_sizes: The real space size of a detector pixel.
        distance: The distance between the detector and the sample.

    Returns:
        The corrected stack of frames.
    """
    angles = scattering_angles(
        cast(Tuple[int, int], frames.shape[-2:]), beam_center, pixel_sizes, distance
    )
    transmissibility = transmitted_flux / incident_flux
    transmissibility = (
        transmissibility
        if transmissibility.shape == (1,)
        else expand_dims(transmissibility, (1, 2))
    )

    secangles: ndarray[Tuple[int, int], dtype[floating]] = broadcast_to(
        1 / cos(angles), frames.shape
    )
    correction_factors: ndarray[Tuple[int, int, int], dtype[floating]] = divide(
        1 - power(transmissibility, secangles - 1),
        log(transmissibility) * (1 - secangles),
        out=ones_like(secangles),
        where=logical_and(secangles != 1.0, transmissibility != 1.0),
    )

    return frames * correction_factors
