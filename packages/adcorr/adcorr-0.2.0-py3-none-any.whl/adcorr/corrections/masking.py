from numpy import bool_, broadcast_to, dtype
from numpy.ma import MaskedArray, masked_where

from ..utils.typing import Frame, FrameDType, FrameHeight, Frames, FrameWidth, NumFrames


def mask_frames(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, FrameDType],
    mask: Frame[FrameWidth, FrameHeight, dtype[bool_]],
) -> MaskedArray[tuple[NumFrames, FrameWidth, FrameHeight], FrameDType]:
    """Replaces masked elemenets of frames in a stack with zero.

    Args:
        frames: A stack of frames to be masked.
        mask: The boolean mask to apply to each frame.

    Returns:
        A stack of frames where pixels.
    """
    return masked_where(broadcast_to(mask, frames.shape), frames)
