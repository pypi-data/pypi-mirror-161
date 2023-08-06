from typing import TypeVar

from numpy import bool_, dtype, floating, ndarray, number

from ..corrections import (
    average_all_frames,
    correct_angular_efficiency,
    correct_dark_current,
    correct_deadtime,
    correct_displaced_volume,
    correct_flatfield,
    correct_polarization,
    correct_self_absorption,
    correct_solid_angle,
    mask_frames,
    normalize_frame_time,
    normalize_thickness,
    normalize_transmitted_flux,
    subtract_background,
)
from ..utils.typing import (
    Frame,
    FrameHeight,
    Frames,
    FrameWidth,
    NumFrames,
    VectorOrSingle,
)


def pauw_instrumental_background_sequence(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    mask: Frame[FrameWidth, FrameHeight, dtype[bool_]],
    count_times: ndarray[VectorOrSingle[NumFrames], dtype[floating]],
    incident_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    transmitted_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    minimum_pulse_separation: float,
    minimum_arrival_separation: float,
    base_dark_current: float,
    temporal_dark_current: float,
    flux_dependant_dark_current: float,
    beam_center_pixels: tuple[float, float],
    pixel_sizes: tuple[float, float],
    sample_detector_separation: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Applies an ordered sequence of corrections to correct for instrumental background.

    Applies an ordered sequence of corrections to correct for instrumental background,
    as detailed as Process A in section 2 of 'The modular small-angle X-ray scattering
    data correction sequence' [https://doi.org/10.1107/S1600576717015096].

    Args:
        frames: A sequence of frames, on which the series of corrections should be
            applied.
        mask: The boolean mask to apply to each frame.
        count_times: The period over which photons are counted for each frame in the
            sequence, or a single value which is applied to all frames in the sequence.
        incident_flux: The flux intensity observed upstream of the sample.
        transmitted_flux: The flux intensity observed downstream of the sample.
        minimum_pulse_separation: The minimum time difference required between a prior
            pulse and the current pulse for the current pulse to be recorded correctly.
        minimum_arrival_separation: The minimum time difference required between the
            current pulse and a subsequent pulse for the current pulse to be recorded
            correctly.
        base_dark_current: The dark current flux, irrespective of time.
        temporal_dark_current: The dark current flux, as a factor of time.
        flux_dependant_dark_current: The dark current flux, as a factor of incident
            flux.
        beam_center_pixels: The center position of the beam in pixels.
        pixel_sizes: The real space size of a detector pixel.

    Returns:
        The corrected stack of frames.
    """
    frames = mask_frames(frames, mask)
    frames = correct_deadtime(
        frames, count_times, minimum_pulse_separation, minimum_arrival_separation
    )
    frames = correct_dark_current(
        frames,
        count_times,
        base_dark_current,
        temporal_dark_current,
        flux_dependant_dark_current,
    )
    frames = normalize_frame_time(frames, count_times)
    frames = normalize_transmitted_flux(frames, transmitted_flux)
    frames = correct_self_absorption(
        frames,
        incident_flux,
        transmitted_flux,
        beam_center_pixels,
        pixel_sizes,
        sample_detector_separation,
    )
    return frames


#: The number of background frames in a stack of frames
NumBackgrounds = TypeVar("NumBackgrounds", bound=int)


def pauw_simple_sample_sequence(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    backgrounds: Frames[NumBackgrounds, FrameWidth, FrameHeight, dtype[number]],
    mask: Frame[FrameWidth, FrameHeight, dtype[bool_]],
    flatfield: Frame[FrameWidth, FrameHeight, dtype[floating]],
    frames_count_times: ndarray[VectorOrSingle[NumFrames], dtype[floating]],
    backgrounds_count_times: ndarray[VectorOrSingle[NumBackgrounds], dtype[floating]],
    frames_incident_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    frames_transmitted_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    background_incident_flux: ndarray[VectorOrSingle[NumBackgrounds], dtype[number]],
    background_transmitted_flux: ndarray[VectorOrSingle[NumBackgrounds], dtype[number]],
    minimum_pulse_separation: float,
    minimum_arrival_separation: float,
    base_dark_current: float,
    temporal_dark_current: float,
    flux_dependant_dark_current: float,
    beam_center_pixels: tuple[float, float],
    pixel_sizes: tuple[float, float],
    sample_detector_separation: float,
    sensor_absorption_coefficient: float,
    sample_thickness: float,
    sensor_thickness: float,
    beam_polarization: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Applies an ordered sequence of corrections to frames containing a simple sample.

    Applies an ordered sequence of corrections to correct for instrumental background,
    as detailed as Process B in section 2 of 'The modular small-angle X-ray scattering
    data correction sequence' [https://doi.org/10.1107/S1600576717015096].

    Args:
        frames: A sequence of frames, on which the series of corrections should be
            applied.
        backgrounds: A sequence of background frames, which should be subtracted from
            the foreground frames post correction.
        mask: The boolean mask to apply to each frame.
        flatfield: The multiplicative flatfield correction to be applied to detector
            readings. If None, a uniform flatfield of ones is applied, resulting in no
            change to the frame.
        frames_count_times: The period over which photons are counted for each frame in
            the frames sequence, or a single value which is applied to all frames in
            the sequence.
        backgrounds_count_times: The period over which photons are counted for each
            frame in the backgrounds sequence, or a single value which is applied to
            all frames in the sequence.
        frames_incident_flux: The flux intensity observed upstream of the sample for
            each frame in the frames sequence.
        frames_transmitted_flux: The flux intensity observed downstream of the sample
            for each frame in the frames sequence.
        background_incident_flux: The flux intensity observed upstream of the sample for
            each frame in the backgrounds sequence.
        background_transmitted_flux: The flux intensity observed downstream of the
            sample for each frame in the backgrounds sequence.
        minimum_pulse_separation: The minimum time difference required between a prior
            pulse and the current pulse for the current pulse to be recorded correctly.
        minimum_arrival_separation: The minimum time difference required between the
            current pulse and a subsequent pulse for the current pulse to be recorded
            correctly.
        base_dark_current: The dark current flux, irrespective of time.
        temporal_dark_current: The dark current flux, as a factor of time.
        flux_dependant_dark_current: The dark current flux, as a factor of incident
            flux.
        beam_center_pixels: The center position of the beam in pixels.
        pixel_sizes: The real space size of a detector pixel.
        sample_detector_separation: The distance between the detector and the sample.
        sensor_absorption_coefficient: The coefficient of absorption for a given
            detector head material at a given photon energy.
        sample_thickness: The thickness of the sample material.
        sensor_thickness: The thickness of the detector head material.
        beam_polarization: The fraction of incident radiation polarized in the
            horizontal plane, where 0.5 signifies an unpolarized source.

    Returns:
        The corrected stack of frames.
    """
    frames = pauw_instrumental_background_sequence(
        frames,
        mask,
        frames_count_times,
        frames_incident_flux,
        frames_transmitted_flux,
        minimum_pulse_separation,
        minimum_arrival_separation,
        base_dark_current,
        temporal_dark_current,
        flux_dependant_dark_current,
        beam_center_pixels,
        pixel_sizes,
        sample_detector_separation,
    )
    backgrounds = pauw_instrumental_background_sequence(
        backgrounds,
        mask,
        backgrounds_count_times,
        background_incident_flux,
        background_transmitted_flux,
        minimum_pulse_separation,
        minimum_arrival_separation,
        base_dark_current,
        temporal_dark_current,
        flux_dependant_dark_current,
        beam_center_pixels,
        pixel_sizes,
        sample_detector_separation,
    )
    background = average_all_frames(backgrounds)
    frames = subtract_background(frames, background)
    frames = correct_flatfield(frames, flatfield)
    frames = correct_angular_efficiency(
        frames,
        beam_center_pixels,
        pixel_sizes,
        sample_detector_separation,
        sensor_absorption_coefficient,
        sensor_thickness,
    )
    frames = correct_solid_angle(
        frames, beam_center_pixels, pixel_sizes, sample_detector_separation
    )
    frames = correct_polarization(
        frames,
        beam_center_pixels,
        pixel_sizes,
        sample_detector_separation,
        beam_polarization,
    )
    frames = normalize_thickness(frames, sample_thickness)
    return frames


#: The number of dispersant frames in a stack of frames
NumDispersants = TypeVar("NumDispersants", bound=int)


def pauw_dispersed_sample_sequence(
    frames: Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]],
    dispersants: Frames[NumDispersants, FrameWidth, FrameHeight, dtype[number]],
    backgrounds: Frames[NumBackgrounds, FrameWidth, FrameHeight, dtype[number]],
    mask: Frame[FrameWidth, FrameHeight, dtype[bool_]],
    flatfield: Frame[FrameWidth, FrameHeight, dtype[floating]],
    frame_count_times: ndarray[VectorOrSingle[NumFrames], dtype[floating]],
    dispersant_count_times: ndarray[VectorOrSingle[NumDispersants], dtype[floating]],
    background_count_times: ndarray[VectorOrSingle[NumBackgrounds], dtype[floating]],
    frames_incident_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    frames_transmitted_flux: ndarray[VectorOrSingle[NumFrames], dtype[number]],
    dispersant_incident_flux: ndarray[VectorOrSingle[NumDispersants], dtype[number]],
    dispersant_transmitted_flux: ndarray[VectorOrSingle[NumDispersants], dtype[number]],
    background_incident_flux: ndarray[VectorOrSingle[NumBackgrounds], dtype[number]],
    background_transmitted_flux: ndarray[VectorOrSingle[NumBackgrounds], dtype[number]],
    minimum_pulse_separation: float,
    minimum_arrival_separation: float,
    base_dark_current: float,
    temporal_dark_current: float,
    flux_dependant_dark_current: float,
    beam_center_pixels: tuple[float, float],
    pixel_sizes: tuple[float, float],
    sample_detector_separation: float,
    sensor_absorption_coefficient: float,
    sample_thickness: float,
    sensor_thickness: float,
    beam_polarization: float,
    displaced_fraction: float,
) -> Frames[NumFrames, FrameWidth, FrameHeight, dtype[number]]:
    """Applies an ordered sequence of corrections to frames containing a dispersed sample.

    Applies an ordered sequence of corrections to correct for instrumental background,
    as detailed as Process C in section 2 of 'The modular small-angle X-ray scattering
    data correction sequence' [https://doi.org/10.1107/S1600576717015096].

    Args:
        frames: A sequence of frames, on which the series of corrections should be
            applied.
        dispersants: A sequence of dispersant frames, which should be subtracted from
            the foreground frames following simple sample corrections.
        backgrounds: A sequence of background frames, which should be subtracted from
            the dispersant and foreground frames following instrumental background
            corrections.
        mask: The boolean mask to apply to each frame.
        flatfield: The multiplicative flatfield correction to be applied to detector
            readings. If None, a uniform flatfield of ones is applied, resulting in no
            change to the frame.
        frame_count_times: The period over which photons are counted for each frame in
            the frames sequence, or a single value which is applied to all frames in
            the sequence.
        dispersant_count_times: The period over which photons are counted for each
            frame in the despersants sequence, or a single value which is applied to
            all frames in the sequence.
        background_count_times: The period over which photons are counted for each
            frame in the backgrounds sequence, or a single value which is applied to
            all frames in the sequence.
        frames_incident_flux: The flux intensity observed upstream of the sample for
            each frame in the frames sequence.
        frames_transmitted_flux: The flux intensity observed downstream of the sample
            for each frame in the frames sequence.
        background_incident_flux: The flux intensity observed upstream of the sample for
            each frame in the backgrounds sequence.
        background_transmitted_flux: The flux intensity observed downstream of the
            sample for each frame in the backgrounds sequence.
        dispersants_incident_flux: The flux intensity observed upstream of the sample
            for each frame in the dispersants sequence.
        dispersants_transmitted_flux: The flux intensity observed downstream of the
            sample for each frame in the dispersants sequence.
        minimum_pulse_separation: The minimum time difference required between a prior
            pulse and the current pulse for the current pulse to be recorded correctly.
        minimum_arrival_separation: The minimum time difference required between the
            current pulse and a subsequent pulse for the current pulse to be recorded
            correctly.
        base_dark_current: The dark current flux, irrespective of time.
        temporal_dark_current: The dark current flux, as a factor of time.
        flux_dependant_dark_current: The dark current flux, as a factor of incident
            flux.
        beam_center_pixels: The center position of the beam in pixels.
        pixel_sizes: The real space size of a detector pixel.
        sample_detector_separation: The distance between the detector and the sample.
        sensor_absorption_coefficient: The coefficient of absorption for a given
            detector head material at a given photon energy.
        sample_thickness: The thickness of the sample material.
        sensor_thickness: The thickness of the detector head material.
        beam_polarization: The fraction of incident radiation polarized in the
            horizontal plane, where 0.5 signifies an unpolarized source.
        displaced_fraction: The fraction of solvent displaced by the analyte.

    Returns:
        The corrected stack of frames.
    """
    frames = pauw_simple_sample_sequence(
        frames,
        backgrounds,
        mask,
        flatfield,
        frame_count_times,
        background_count_times,
        frames_incident_flux,
        frames_transmitted_flux,
        background_incident_flux,
        background_transmitted_flux,
        minimum_pulse_separation,
        minimum_arrival_separation,
        base_dark_current,
        temporal_dark_current,
        flux_dependant_dark_current,
        beam_center_pixels,
        pixel_sizes,
        sample_detector_separation,
        sensor_absorption_coefficient,
        sample_thickness,
        sensor_thickness,
        beam_polarization,
    )
    dispersants = pauw_simple_sample_sequence(
        dispersants,
        backgrounds,
        mask,
        flatfield,
        dispersant_count_times,
        background_count_times,
        dispersant_incident_flux,
        dispersant_transmitted_flux,
        background_incident_flux,
        background_transmitted_flux,
        minimum_pulse_separation,
        minimum_arrival_separation,
        base_dark_current,
        temporal_dark_current,
        flux_dependant_dark_current,
        beam_center_pixels,
        pixel_sizes,
        sample_detector_separation,
        sensor_absorption_coefficient,
        sample_thickness,
        sensor_thickness,
        beam_polarization,
    )
    dispersants = correct_displaced_volume(dispersants, displaced_fraction)
    dispersant = average_all_frames(dispersants)
    frames = subtract_background(frames, dispersant)
    return frames
