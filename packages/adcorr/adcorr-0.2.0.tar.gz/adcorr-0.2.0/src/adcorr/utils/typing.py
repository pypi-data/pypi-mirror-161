from typing import Literal, TypeVar, Union

from numpy import dtype, ndarray

#: The underlying data type of a frame.
FrameDType = TypeVar("FrameDType", bound=dtype)
#: The number of frames in a stack of frames.
NumFrames = TypeVar("NumFrames", bound=int)
#: The number of pixels spanning the width of a frame.
FrameWidth = TypeVar("FrameWidth", bound=int)
#: The number of pixels spanning the height of a frame.
FrameHeight = TypeVar("FrameHeight", bound=int)

#: An array with the given length, or a singular value
VectorOrSingle = tuple[Union[NumFrames, Literal[1]]]

#: A frame; Comprising a shape and a data type
Frame = ndarray[tuple[FrameWidth, FrameHeight], FrameDType]
#: A stack of frames; Comprising a shape and a data type
Frames = ndarray[tuple[NumFrames, FrameWidth, FrameHeight], FrameDType]
