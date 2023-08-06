from typing import Tuple, cast

from numpy import cos, dtype, floating, number, power

from ..utils.geometry import scattering_angles
from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames


def correct_solid_angle(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    beam_center: Tuple[float, float],
    pixel_sizes: Tuple[float, float],
    distance: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[floating]]:
    """Corrects for the solid angle by scaling by the inverse of area subtended by a pixel.

    Corrects for the solid angle by scaling by the inverse of area subtended by each
    pixel, as detailed in section 3.4.6 of 'Everything SAXS: small-angle scattering
    pattern collection and correction' [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        frames: A stack of frames to be corrected.
        beam_center: The center position of the beam in pixels.
        pixel_sizes: The real space size of a detector pixel.
        distance: The distance between the detector and the sample head.

    Returns:
        The corrected stack of frames.
    """
    correction = power(
        cos(
            scattering_angles(
                cast(Tuple[int, int], frames.shape[-2:]),
                beam_center,
                pixel_sizes,
                distance,
            )
        ),
        3,
    )
    return frames / correction
