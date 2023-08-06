from numpy import dtype, number

from ..utils.typing import Frame, FrameHeight, Frames, FrameWidth, NumFrames


def subtract_background(
    foreground_frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    background_frame: Frame[FrameWidth, FrameHeight, dtype[number]],
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Subtract a background frame from a sequence of foreground frames.

    Subtract a background frame from a sequence of foreground frames, as detailed in
    section 3.4.6 of 'Everything SAXS: small-angle scattering pattern collection and
    correction' [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        foreground_frames: A sequence of foreground frames to be corrected.
        background_frame: The background which is to be corrected for.

    Returns:
        A sequence of corrected frames.
    """
    return foreground_frames - background_frame
