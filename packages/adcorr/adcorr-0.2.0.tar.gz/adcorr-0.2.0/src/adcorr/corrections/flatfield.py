from numpy import dtype, floating, number

from ..utils.typing import Frame, FrameHeight, Frames, FrameWidth, NumFrames


def correct_flatfield(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    flatfield: Frame[FrameWidth, FrameHeight, dtype[floating]],
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Apply multiplicative flatfield correction, to correct for inter-pixel sensitivity.

    Apply multiplicative flatfield correction, to correct for inter-pixel sensitivity,
    as described in section 3.xii of 'The modular small-angle X-ray scattering data
    correction sequence' [https://doi.org/10.1107/S1600576717015096].

    Args:
        frames: A stack of frames to be corrected.
        flatfield: The multiplicative flatfield correction to be applied.

    Returns:
        The corrected stack of frames.
    """
    return frames * flatfield
