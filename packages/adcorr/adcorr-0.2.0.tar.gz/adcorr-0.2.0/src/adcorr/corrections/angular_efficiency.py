from typing import Tuple, cast

from numpy import cos, dtype, exp, number

from ..utils.geometry import scattering_angles
from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames


def correct_angular_efficiency(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    beam_center: Tuple[float, float],
    pixel_sizes: Tuple[float, float],
    distance: float,
    absorption_coefficient: float,
    thickness: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Corrects for loss due to the angular efficiency of the detector head.

    Corrects for loss due to the angular efficiency of the detector head, as described
    in section 3.xiii and appendix C of 'The modular small-angle X-ray scattering data
    correction sequence' [https://doi.org/10.1107/S1600576717015096].

    Args:
        frames: A stack of frames to be corrected.
        beam_center: The center position of the beam in pixels.
        pixel_sizes: The real space size of a detector pixel.
        distance: The distance between the detector and the sample head.
        absorption_coefficient: The coefficient of absorption for a given material at a
            given photon energy.
        thickness: The thickness of the detector head material.

    Returns:
        The corrected stack of frames.
    """
    if absorption_coefficient <= 0.0:
        raise ValueError("Absorption Coefficient must be positive.")
    if thickness <= 0.0:
        raise ValueError("Thickness must be positive.")

    absorption_efficiency = 1.0 - exp(
        -absorption_coefficient
        * thickness
        / cos(
            scattering_angles(
                cast(tuple[int, int], frames.shape[-2:]),
                beam_center,
                pixel_sizes,
                distance,
            )
        )
    )
    return frames / absorption_efficiency
