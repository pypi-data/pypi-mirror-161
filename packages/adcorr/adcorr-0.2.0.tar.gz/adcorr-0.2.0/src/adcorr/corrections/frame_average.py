from math import prod

from numpy import dtype, number

from ..utils.typing import Frame, FrameHeight, Frames, FrameWidth, NumFrames


def average_all_frames(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]
) -> Frame[FrameWidth, FrameHeight, dtype[number]]:
    """Average all frames over the leading axis.

    Args:
        frames: A stack of frames to be averaged.

    Returns:
        A frame containing the average pixel values of all frames in the stack.
    """
    return frames.reshape(
        [frames.size // prod(frames.shape[-2:]), *frames.shape[-2:]]
    ).mean(0)
