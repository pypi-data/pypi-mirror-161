from numpy import dtype, expand_dims, ndarray, number

from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames, VectorOrSingle


def normalize_transmitted_flux(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    transmitted_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Normalize for incident flux and transmissibility by scaling photon counts.

    Normalize for incident flux and transmissibility by scaling photon counts with
    respect to the total observed flux, as detailed in section 4 of 'The modular small-
    angle X-ray scattering data correction sequence'
    [https://doi.org/10.1107/S1600576717015096].

    Args:
        frames: A stack of frames to be normalized.
        transmitted_flux: The flux intensity observed downstream of the sample.

    Returns:
        The normalized stack of frames.
    """

    return frames / expand_dims(transmitted_flux, (-2, -1))
