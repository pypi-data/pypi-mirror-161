from numpy import atleast_1d, dtype, expand_dims, floating, ndarray, number

from ..utils.typing import FrameHeight, Frames, FrameWidth, NumFrames, VectorOrSingle


def normalize_frame_time(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    count_times: ndarray[VectorOrSingle[NumFrames], dtype[floating]],
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[floating]]:
    """Normalize for detector frame rate by scaling photon counts according to count time.

    Normalize for detector frame rate by scaling photon counts according to count time,
    as detailed in section 3.4.3 of 'Everything SAXS: small-angle scattering pattern
    collection and correction' [https://doi.org/10.1088/0953-8984/25/38/383201].

    Args:
        frames: A stack of frames to be normalized.
        count_times: The period over which photons are counted for each frame.

    Returns:
        The normalized stack of frames.
    """
    if (count_times <= 0).any():
        raise ValueError("Count times must be positive.")

    times = expand_dims(atleast_1d(count_times), (1, 2))
    return frames / times
