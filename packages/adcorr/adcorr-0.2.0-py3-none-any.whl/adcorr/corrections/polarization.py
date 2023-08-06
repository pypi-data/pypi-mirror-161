from typing import Tuple, cast

from numpy import cos, dtype, floating, number, sin, square

from ..utils.geometry import azimuthal_angles, scattering_angles
from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames


def correct_polarization(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    beam_center: Tuple[float, float],
    pixel_sizes: Tuple[float, float],
    distance: float,
    horizontal_poarization: float = 0.5,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[floating]]:
    """Corrects for the effect of polarization of the incident beam.

    Corrects for the effect of polarization of the incident beam, as detailed in
    section 3.4.1 of 'Everything SAXS: small-angle scattering pattern collection and
    correction' [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        frames: A stack of frames to be corrected.
        beam_center: The center position of the beam in pixels.
        pixel_sizes: The real space size of a detector pixel.
        distance: The distance between the detector and the sample.
        horizontal_poarization: The fraction of incident radiation polarized in the
            horizontal plane, where 0.5 signifies an unpolarized source. Defaults to
            0.5.

    Returns:
        The corrected stack of frames.
    """
    if horizontal_poarization < 0.0 or horizontal_poarization > 1.0:
        raise ValueError("Horizontal Polarization must be within the interval [0, 1].")

    scattering = scattering_angles(
        cast(tuple[int, int], frames.shape[-2:]), beam_center, pixel_sizes, distance
    )
    azimuths = azimuthal_angles(
        cast(tuple[int, int], frames.shape[-2:]), beam_center, pixel_sizes
    )
    correction_factors = horizontal_poarization * (
        1.0 - square(sin(azimuths) * sin(scattering))
    ) + (1.0 - horizontal_poarization) * (1.0 - square(cos(azimuths) * sin(scattering)))
    return frames * correction_factors
