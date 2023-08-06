from numpy import dtype, number

from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames


def normalize_thickness(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    sample_thickness: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Normailizes pixel intensities by dividing by the sample thickness.

    Normailizes pixel intensities by dividing by the sample thickness, as detailed in
    section 3.4.3 of 'Everything SAXS: small-angle scattering pattern collection and
    correction' [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        frames: A stack of frames to be corrected.
        sample_thickness: The thickness of the exposed sample.

    Returns:
        The normalized stack of frames.
    """
    if sample_thickness <= 0:
        raise ValueError("Sample Thickness must be positive.")

    return frames / sample_thickness
