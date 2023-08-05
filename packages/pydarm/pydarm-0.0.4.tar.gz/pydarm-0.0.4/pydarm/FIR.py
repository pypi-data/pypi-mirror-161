# Copyright (C) Aaron Viets, Miftahul Ma'arif (2021)
#
# This file is part of pyDARM.
#
# pyDARM is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pyDARM is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pyDARM. If not, see <https://www.gnu.org/licenses/>.
# %%
import numpy as np
from scipy import signal, fft
import warnings
from .FIRtools import (DPSS, resample,
                       DolphChebyshev, freqresp)
from .plot import plot
from .model import Model
from .darm import DARMModel
from .calcs import CALCSModel
from .digital import daqdownsamplingfilters


class FIRfilter(object):
    """ Model parameters for FIR filter creation
    Parameters.
    ----------
    fNyquist : int
        Nyquist frequency of FIR filter
    dur : float
        Duration in seconds of FIR filter
    latency : float
        Latency in seconds of FIR filter
    df : float
        Frequency spacing of the FIR filter
    window_type : str
        Type of window function to use. Options are 'dpss', 'kaiser',
        'dolph_chebyshev', and 'hann'.
    window : float
        Window function, stored as an array
    freq_res: float
        Frequency resolution of the FIR filter, computed as half the width of
        the central lobe.
    dt : float
        Inverse of the sampling rate
    freq_array : float
        Frequency array from 0 Hz up to and including Nyquist
    highpass_fcut : float
        Cut off frequency for high-pass filter
    lowpass_fcut : float
        Cut off frequency for low-pass filter (relevant for inverse sensing filter)
    samples_to_HPcorner : int
        Number of samples in the frequency domain below the high-pass corner frequency
    samples_to_LPcorner : int
        Number of samples in the frequency domain above the low-pass corner frequency
    delay_samples : int
        Number of samples to delay filter.  This is related to the desired latency.
    delay_array : complex
        complex array of the delay to be applied at each frequency
    advance_array : complex
        complex array of the advance to be applied at each frequency required to
        undo the artificial delay
    Returns
    ----------
    FIRfilter : list
        List of model parameters for FIR filter creation parameters
    """
    def __init__(self, fNyq=8192, dur=0, highpass_fcut=10, lowpass_fcut=None,
                 latency=None, window_type='dpss', freq_res=3.0):
        self.fNyquist = fNyq
        self.dt = 1/(2.0*fNyq)
        nsamples = round(dur / self.dt)
        self.dur = nsamples * self.dt
        self.window_type = window_type
        if latency is None:
            self.latency = self.dur/2.0
        else:
            self.latency = round(latency / self.dt) * self.dt

        if dur:
            if window_type == 'hann':
                warnings.warn("Frequency resolution can not be set "
                              "since you are using Hann window.")
                self.freq_res = 2.0 / self.dur
            else:
                self.freq_res = freq_res
            self.df = 1.0 / self.dur
            self.freq_array = np.fft.rfftfreq(nsamples, d=self.dt)
            self.highpass_fcut = highpass_fcut
            if highpass_fcut is not None:
                self.samples_to_HPcorner = int((highpass_fcut - 0.75 * self.freq_res) / self.df)
            else:
                self.samples_to_HPcorner = 0
            self.lowpass_fcut = lowpass_fcut
            if self.lowpass_fcut is not None:
                self.samples_to_LPcorner = int((self.fNyquist - self.lowpass_fcut) / self.df)
            else:
                self.samples_to_LPcorner = 0
            self.delay_samples = round(self.latency / self.dt)
            self.delay_array = \
                np.exp(-2 * np.pi * 1j * self.freq_array * self.delay_samples * self.dt)
            self.advance_array = \
                np.exp(2 * np.pi * 1j * self.freq_array * self.delay_samples * self.dt)

            # Compute a window so that the filter falls off smoothly at the edges.
            front_length = int(self.latency / self.dt)
            back_length = nsamples - front_length
            if window_type == "dpss":
                if front_length == back_length:
                    alpha = self.freq_res * 2 * front_length * self.dt
                    alpha = np.sqrt(alpha * alpha - 1)
                    dpss = DPSS(2 * front_length, alpha, max_time=60)
                    self.window = dpss
                else:
                    alpha_front = self.freq_res * 2 * front_length * self.dt
                    alpha_back = self.freq_res * 2 * back_length * self.dt
                    alpha_front = np.sqrt(alpha_front * alpha_front - 1)
                    alpha_back = np.sqrt(alpha_back * alpha_back - 1)
                    dpss_front = DPSS(2 * front_length, alpha_front,
                                      max_time=60)[:front_length]
                    dpss_back = DPSS(2 * back_length, alpha_back,
                                     max_time=60)[-back_length:]
                    dpss = np.concatenate((dpss_front, dpss_back))
                    self.window = dpss
            elif window_type == "kaiser":
                alpha_front = self.freq_res * 2 * front_length * self.dt
                alpha_back = self.freq_res * 2 * back_length * self.dt
                beta_front = np.pi * np.sqrt(alpha_front * alpha_front - 1)
                beta_back = np.pi * np.sqrt(alpha_back * alpha_back - 1)
                kaiserwin_front = signal.windows.kaiser(2 * front_length,
                                                        int(beta_front))[:front_length]
                kaiserwin_back = signal.windows.kaiser(2 * back_length,
                                                       int(beta_back))[-back_length:]
                kaiserwin = np.concatenate((kaiserwin_front, kaiserwin_back))
                self.window = kaiserwin
            elif window_type == "dolph_chebyshev":
                alpha_front = self.freq_res * 2 * front_length * self.dt
                alpha_back = self.freq_res * 2 * back_length * self.dt
                alpha_front = np.sqrt(1.37 * 1.37 * alpha_front * alpha_front - 1)
                alpha_back = np.sqrt(1.37 * 1.37 * alpha_back * alpha_back - 1)
                DC_front = DolphChebyshev(2 * front_length, alpha_front)[:front_length]
                DC_back = DolphChebyshev(2 * back_length, alpha_back)[-back_length:]
                DC = np.concatenate((DC_front, DC_back))
                self.window = DC
            elif window_type == "hann":
                hannwin_front = np.hanning(np.float64(2*front_length))[:front_length]
                hannwin_back = np.hanning(np.float64(2*back_length))[-back_length:]
                hannwin = np.concatenate((hannwin_front, hannwin_back))
                self.window = hannwin
            else:
                raise ValueError("Window type needs to be set to 'dpss', 'kaiser', "
                      "'dolph_chebyshev' or 'hann'. It is currently ", window_type, ".")
        else:
            self.delay_samples = 0


def correctFIRfilter(FIRparams, tdfilt, fdmodel, window_correction_range, save_to_file=None):
    """ Correct FIR filter production errors induced by windowing,
    and return a compensated version of the frequency-domain model.

    Parameters
    ----------
    FIRparams : FIRfilter parameters list
        a list of model parameters for FIR filter creation
    parameters
    tdfilt : array-like
        Time-domain model FIR filter
    fdmodel : array-like
        Transfer function of frequency domain model
    window_correction_range : array
        Frequency range for window correction FIR filter
    save_to_file : `str`, optional
        Filename (NPZ) to save the data from this result

    Returns
    ----------
    compensated_model : array-like
        A compensated version of the frequency-domain model
    """
    if len(window_correction_range) % 4:
        raise ValueError("correctFIRfilter: Invalid input argument for window_correction_range."
                         " It must be a multiple of 4.")
    for i in range(1, len(window_correction_range)):
        if window_correction_range[i] < window_correction_range[i-1]:
            raise ValueError("correctFIRfilter: Invalid input argument for "
                             "window_correction_range.")

    if type(FIRparams) is not list:
        FIRparams = [FIRparams]
    if type(tdfilt) is not list:
        tdfilt = [tdfilt]

    model = np.asarray(fdmodel)

    fd_from_td = fft.rfft(tdfilt[0])
    fd_from_td *= FIRparams[0].advance_array

    for i in range(1, len(FIRparams)):
        if any(tdfilt[i]):
            factor = fft.rfft(tdfilt[i])
            factor *= FIRparams[i].advance_array
            for j in range(int(FIRparams[i].fNyquist / FIRparams[0].df)):
                fd_from_td[j] *= factor[round(j * FIRparams[0].df / FIRparams[i].df)]

    for i in range(1, len(fd_from_td)):
        if fd_from_td[i] == 0:
            fd_from_td[i] = fd_from_td[i - 1]
    correction = model / fd_from_td

    # Smooth off the correction below the cutoff frequency
    for i in range(FIRparams[0].samples_to_HPcorner):
        j = FIRparams[0].samples_to_HPcorner - 1 - i
        correction[j] = 1.5 * correction[j + 1] - 0.5 * correction[j + 2]

    # Window the result so that it doesn't add kinks to the "corrected" model
    start = 0
    for i in range(len(window_correction_range) // 4):
        rampup_start = int(window_correction_range[4*i+0] / FIRparams[0].df)
        rampup_end = int(window_correction_range[4*i+1] / FIRparams[0].df)
        rampdown_start = int(window_correction_range[4*i+2] / FIRparams[0].df)
        rampdown_end = int(window_correction_range[4*i+3] / FIRparams[0].df)
        for j in range(start, rampup_start):
            correction[j] = 1.0
        hann = np.hanning(3 + 2 * (rampup_end - rampup_start))[1: 1 + rampup_end - rampup_start]
        for j in range(rampup_start, rampup_end):
            correction[j] = correction[j] * hann[j - rampup_start] + 1.0 - hann[j - rampup_start]
        hann = np.hanning(3 + 2 * (rampdown_end
                                   - rampdown_start))[2 + rampdown_end - rampdown_start: -1]
        for j in range(rampdown_start, rampdown_end):
            correction[j] = correction[j] * hann[j
                                                 - rampdown_start] + 1.0 - hann[j - rampdown_start]
        start = rampdown_end
    for i in range(start, len(correction)):
        correction[i] = 1.0

    # Multiply the model by the correction
    compensated_model = model * correction

    if save_to_file is not None:
        np.savez(save_to_file, compensated_model=compensated_model)

    return compensated_model


def createFIRfilter(FIRparams, static_model, save_to_file=None):
    """ Generate an FIR filter based on provided frequency-domain model

    Parameters
    ----------
    FIRparams : FIRfilter parameters list
        a list of model parameters for FIR filter creation parameters
    static_model : array-like
        Transfer function of frequency domain model
    save_to_file : `str`, optional
        Filename (NPZ) to save the data from this result

    Returns
    ----------
    model_FIR : `float64`, array-like
        A time domain FIR filter model
    double_model : `float`, array-like
        An array of real doubles FIR filter model
    """
    model = []
    for i in range(0, len(static_model)):
        model.append(static_model[i])
    model = np.asarray(model, dtype=np.complex128)

    if FIRparams.highpass_fcut is not None:
        # Smooth off the model below the cutoff
        smooth_samples = int((FIRparams.highpass_fcut - 0.4 * FIRparams.freq_res) / FIRparams.df)
        slope = model[smooth_samples - 1] - model[smooth_samples]
        model[:smooth_samples] = model[smooth_samples - 1] \
            + slope * smooth_samples / np.pi * 2 * np.cos(np.arange(smooth_samples)
                                                          * np.pi / 2 / smooth_samples)

    # Upsample for better FFT quality
    model = resample(model, 16 * (len(model) - 1) + 1, return_double=True)

    if FIRparams.highpass_fcut is not None:
        # Create a high-pass filter to be convolved with the FIR model filter
        hp_hann = np.hanning(32)[:16]
        hp_hann = np.concatenate((np.zeros(16 * FIRparams.samples_to_HPcorner
                                           - len(hp_hann)), hp_hann))

        model[: 16 * FIRparams.samples_to_HPcorner] *= hp_hann

    if FIRparams.lowpass_fcut is not None:
        # Create a low-pass filter to be convolved with the FIR model filter
        lp_hann = np.hanning(32 * FIRparams.samples_to_LPcorner)
        lp_hann = lp_hann[-16 * FIRparams.samples_to_LPcorner:]
        model[-16 * FIRparams.samples_to_LPcorner:] *= lp_hann

    # Zero out the Nyquist component
    model[-1] = 0

    # Take inverse real FFT of model
    model_FIR = fft.irfft(model)

    # Add delay to model to make sure it falls off at the edges
    model_FIR = np.roll(model_FIR, int(FIRparams.latency / FIRparams.dt))[:len(model_FIR) // 16]
    freq_array = np.fft.rfftfreq(len(model_FIR), d=FIRparams.dt)
    if not (freq_array == FIRparams.freq_array).all:
        print("Frequency arrays for FIR and model don't agree!")
        print("Freq array from FIR filter is ", freq_array)
        print("Freq array from model is ", FIRparams.freq_array)

    # Apply a window so that the filter falls off smoothly at the edges.
    model_FIR *= FIRparams.window

    # Convert the filter model into an array of real doubles
    # so that it can be read into gstlal_compute_strain
    double_model = np.zeros(2 * len(model))
    double_model[::2] = np.real(model)
    double_model[1::2] = np.imag(model)

    if save_to_file is not None:
        np.savez(save_to_file, model_FIR=np.float64(model_FIR),
                 double_model=double_model)

    return np.float64(model_FIR), double_model


def two_tap_zero_filter_response(zeros, sr, freq):
    """
    Generating two-tap zero filter

    Parameters
    ----------
    zeros : float, int
    sr : float, int
    freq : array

    Returns
    -------
    two_tap : array
    """
    filt = np.ones(1)
    two_tap_filt = np.zeros(2)
    for zero in zeros:
        two_tap_filt[0] = 0.5 + sr / (2.0 * np.pi * zero)
        two_tap_filt[1] = 0.5 - sr / (2.0 * np.pi * zero)
        filt = np.convolve(filt, two_tap_filt)

    filt = np.concatenate((filt, np.zeros(2 * (len(freq) - 1) + len(filt) % 2 - len(filt))))
    two_tap = freqresp(filt, delay_samples=0, samples_per_lobe=1, return_double=True)
    return two_tap


def check_td_vs_fd(tdfilt, fdmodel, fNyq=None, delay_samples=None, highpasstd=None,
                   highpass_fNyq=None, highpass_delay_samples=None, filename="td_vs_fd.png",
                   plot_title="Frequency Response", legend=[r'FIR filter', r'DARM model'],
                   samples_per_lobe=8, ymax_increase=1):
    """
    Checking time-domain vs frequency-domain filters

    Parameters
    ----------
    tdfilt : array
    fdmodel : array
    fNyq : float, int
    delay_samples : float, int
    highpasstd : float, int
    highpass_fNyq : float, int
    highpass_delay_samples : float, int
    filename : str
    plot_title : str
    legend : str, array-like
    samples_per_lobe : int
    ymax_increase : int

    Returns
    -------
    plot figure
    """
    # Check if highpass exists
    if highpasstd is not None:
        highpass_exists = True
    else:
        highpass_exists = False

    # Convert input arguments to lists
    if type(tdfilt) is not list:
        tdfilt = [tdfilt]
    num_filts = len(tdfilt)
    if type(fNyq) is not list:
        fNyq = [fNyq]
    for i in range(num_filts - len(fNyq)):
        fNyq.append(fNyq[-1])
    for i in range(num_filts):
        if fNyq[i] is None:
            fNyq[i] = 1.0
    if delay_samples is None:
        delay_samples = [len(tdfilt[0]) // 2]
    elif type(delay_samples) is not list:
        delay_samples = [delay_samples]
    for i in range(num_filts - len(delay_samples)):
        delay_samples.append(len(tdfilt[len(delay_samples)]) // 2)
    if highpass_exists:
        if type(highpasstd) is not list:
            highpasstd = [highpasstd]
        for i in range(len(highpasstd)):
            if not any(highpasstd[i]):
                highpasstd[i] = None
        for i in range(num_filts - len(highpasstd)):
            highpasstd.append(None)
        if type(highpass_fNyq) is not list:
            highpass_fNyq = [highpass_fNyq]
        for i in range(num_filts - len(highpass_fNyq)):
            highpass_fNyq.append(highpass_fNyq[-1])
        for i in range(num_filts):
            if highpass_fNyq[i] is None:
                highpass_fNyq[i] = 1.0
        if highpass_delay_samples is None:
            if highpasstd[0] is None:
                highpass_delay_samples = [None]
            else:
                highpass_delay_samples = [len(highpasstd[0]) // 2]
        elif type(highpass_delay_samples) is not list:
            highpass_delay_samples = [highpass_delay_samples]
        for i in range(num_filts - len(highpass_delay_samples)):
            if highpasstd[len(highpass_delay_samples)] is None:
                highpass_delay_samples.append(None)
            else:
                highpass_delay_samples.append(len(highpasstd[len(highpass_delay_samples)]) // 2)
    if legend is not None:
        if type(legend) is not list:
            legend = [legend]
        for i in range(num_filts + 1 - len(legend)):
            legend.append("FIR filter %d" % len(legend))

    freq_arrays = []
    fd_from_td_mags = []
    fd_from_td_phases = []
    mag_ratios = []
    phase_diffs = []

    for i in range(num_filts):
        # Find the frequency response of the FIR filter at the requested frequency resolution
        fd_from_td = freqresp(tdfilt[i], delay_samples=delay_samples[i],
                              samples_per_lobe=samples_per_lobe)
        Nf = len(fd_from_td)

        # Check the frequency-domain model to see if it is sampled correctly
        Nfdmodel = len(fdmodel)
        if Nfdmodel != Nf:
            warnings.warn("frequency spacing of frequency-domain model is incorrect."
                          " Resampling - some information may be lost.")
            long_fdmodel = resample(fdmodel, Nf)
        else:
            long_fdmodel = fdmodel

        df = float(fNyq[i]) / (Nf - 1)
        freq_array = np.arange(0.0, fNyq[i] + df, df)

        if highpass_exists:
            if highpasstd[i] is not None:
                highpassfd = freqresp(highpasstd[i], delay_samples=highpass_delay_samples[i])
                highpass_df = float(highpass_fNyq[i]) / (len(highpassfd) - 1)
                for j in range(0, int(highpass_fNyq[i] / df)):
                    fd_from_td[j] *= highpassfd[int(round(j * df / highpass_df))]

        long_fdmodel[0] = long_fdmodel[1]
        ratio = fd_from_td / long_fdmodel

        fd_from_td_mag = np.absolute(fd_from_td)
        fd_from_model_mag = np.absolute(long_fdmodel)
        mag_ratio = np.absolute(ratio)

        fd_from_td_phase = np.zeros(len(fd_from_td))
        for i in range(len(fd_from_td_phase)):
            fd_from_td_phase[i] = np.angle(fd_from_td[i]) * 180 / np.pi

        fd_from_model_phase = np.zeros(len(long_fdmodel))
        for i in range(len(fd_from_model_phase)):
            fd_from_model_phase[i] = np.angle(long_fdmodel[i]) * 180 / np.pi

        phase_diff = np.zeros(len(long_fdmodel))
        for i in range(len(phase_diff)):
            phase_diff[i] = np.angle(ratio[i]) * 180 / np.pi

        freq_arrays.append(np.copy(freq_array))
        fd_from_td_mags.append(np.copy(fd_from_td_mag))
        fd_from_td_phases.append(np.copy(fd_from_td_phase))
        mag_ratios.append(np.copy(mag_ratio))
        phase_diffs.append(np.copy(phase_diff))

    df = freq_array[1] - freq_array[0]
    ymin = pow(10, int(round(np.log10(fd_from_td_mags[-1][int(np.ceil(1.0 / df))]))) - 2)
    ymax = pow(10, int(round(np.log10(fd_from_model_mag[int(np.ceil(1.0 / df))]))) + 2)
    ymax *= ymax_increase
    plot(freq_array, fd_from_td, freq_array, long_fdmodel, freq_min=1,
         freq_max=max(freq_arrays[0]), mag_min=ymin, mag_max=ymax, label=legend,
         title=r'%s' % plot_title.replace('_', '\\_'), filename=filename)
    return freq_arrays, mag_ratios, phase_diffs


def check_td_vs_fd_response(invsens_filt, invsens_highpass, TST_filt, PUM_filt, UIM_filt,
                            act_highpass, D, R, invsens_fNyq=8192, invsens_highpass_fNyq=1024,
                            act_fNyq=1024, D_fNyq=8192, R_fNyq=8192, invsens_delay=None,
                            invsens_highpass_delay=None, act_delay=None, act_highpass_delay=None,
                            time_delay=1.0/16384, filename="td_vs_fd_response.png",
                            plot_title="Response Function", legend=['FIR filters', 'DARM model']):
    """
    Checking time-domain vs frequency-domain responses

    Parameters
    ----------
    invsens_filt : array
    invsens_highpass : array
    TST_filt : array-like
    PUM_filt : array-like
    UIM_filt : array-like
    act_highpass : array
    D : array
    R : array
    invsens_fNyq : float, int
    invsens_highpass_fNyq : float, int
    act_fNyq : float, int
    D_fNyq : float, int
    R_fNyq : float, int
    invsens_delay : float, int
    invsens_highpass_delay : float, int
    act_delay : float, int
    act_highpass_delay : float, int
    time_delay : float, int
    filename : str
    plot_title : str
    legend : str, array-like
    samples_per_lobe : int
    ymax_increase : int

    Returns
    -------
    plot figure
    """
    if invsens_highpass is None:
        invsens_highpass = []
    if act_highpass is None:
        act_highpass = []

    # If delays are None, assume they are half the length of the filter
    if invsens_delay is None:
        invsens_delay = len(invsens_filt) // 2
    if invsens_highpass_delay is None:
        invsens_highpass_delay = len(invsens_highpass) // 2
    if act_delay is None:
        # This assumes that TST, PUM, and UIM filters are all all the same length
        act_delay = len(TST_filt) // 2
    if act_highpass_delay is None:
        act_highpass_delay = len(act_highpass) // 2

    # Now find frequency responses of each filter
    invsens_fd = freqresp(invsens_filt, delay_samples=invsens_delay)

    invsens_highpass_fd = []
    if any(invsens_highpass):
        invsens_highpass_fd = freqresp(invsens_highpass, delay_samples=invsens_highpass_delay)

    TST_fd = freqresp(TST_filt, delay_samples=act_delay)
    PUM_fd = freqresp(PUM_filt, delay_samples=act_delay)
    UIM_fd = freqresp(UIM_filt, delay_samples=act_delay)

    act_highpass_fd = []
    if any(act_highpass):
        act_highpass_fd = freqresp(act_highpass, delay_samples=act_highpass_delay)

    # List of frequency-domain filters and models to manipulate
    fd_list = [[invsens_fd, invsens_highpass_fd, TST_fd, PUM_fd, UIM_fd, act_highpass_fd, D, R],
               [invsens_fNyq, invsens_highpass_fNyq, act_fNyq,
                act_fNyq, act_fNyq, act_fNyq, D_fNyq, R_fNyq],
               [len(invsens_fd), len(invsens_highpass_fd), len(TST_fd), len(PUM_fd), len(UIM_fd),
                len(act_highpass_fd), len(D), len(R)]]
    # Find the maximum Nyquist frequency and pad anything with a lower Nyquist frequency with zeros.
    max_fNqy = max(fd_list[1])
    for i in range(len(fd_list[0])):
        if fd_list[1][i] < max_fNqy and any(fd_list[0][i]):
            length_needed = 1 + int(round(float(fd_list[2][i] - 1) * max_fNqy / fd_list[1][i]))
            if i == 1:
                # The additional inverse sensing filter should be padded with ones instead.
                fd_list[0][i] = np.concatenate((fd_list[0][i],
                                                np.ones(length_needed - fd_list[2][i])))
            else:
                fd_list[0][i] = np.concatenate((fd_list[0][i],
                                                np.zeros(length_needed - fd_list[2][i])))
            fd_list[2][i] = length_needed

    # Now find the finest frequency resolution and upsample everything else to that resolution.
    max_length = max(fd_list[2])
    for i in range(len(fd_list[0])):
        if fd_list[2][i] < max_length and any(fd_list[0][i]):
            resampled = np.zeros(max_length, dtype=np.complex128)
            # linear resampler
            resampled[0] = fd_list[0][i][0]
            resampled[-1] = fd_list[0][i][-1]
            for j in range(1, max_length - 1):
                fdmodel_position = float(j * (fd_list[2][i] - 1)) / (max_length - 1)
                k = int(fdmodel_position)
                after_weight = fdmodel_position - k
                before_weight = 1.0 - after_weight
                resampled[j] = before_weight * fd_list[0][i][k] + after_weight * fd_list[0][i][k+1]
            fd_list[0][i] = resampled

    # Compute a frequency vector
    df = float(max_fNqy) / (max_length - 1)
    frequency = np.arange(0, max_fNqy + df, df)

    # Add in the high-pass filters' frequency response.
    if any(fd_list[0][1]):
        fd_list[0][0] *= fd_list[0][1]
    if any(fd_list[0][5]):
        fd_list[0][2] *= fd_list[0][5]
        fd_list[0][3] *= fd_list[0][5]
        fd_list[0][4] *= fd_list[0][5]

    # Now compute the response of the filters.
    filter_response = fd_list[0][0] + (fd_list[0][2]+fd_list[0][3]+fd_list[0][4]) * fd_list[0][6]

    # Apply a delay if there is one
    if time_delay:
        filter_response *= np.exp(-2.0 * np.pi * 1j * frequency * time_delay)

    # model response
    model_response = fd_list[0][7]

    # Find magnitude and phase, as well as ratios of filters / model
    model_mag = abs(model_response)
    model_phase = np.zeros(len(model_response))
    for i in range(len(model_phase)):
        model_phase[i] = np.angle(model_response[i]) * 180 / np.pi
    filter_mag = abs(filter_response)
    filter_phase = np.zeros(len(filter_response))
    for i in range(len(filter_phase)):
        filter_phase[i] = np.angle(filter_response[i]) * 180 / np.pi

    ratio = filter_response / model_response
    ratio_mag = abs(ratio)
    ratio_phase = np.zeros(len(ratio))
    for i in range(len(ratio_phase)):
        ratio_phase[i] = np.angle(ratio[i]) * 180.0 / np.pi

    # Make plots
    ymin = pow(10, int(round(np.log10(filter_mag[int(np.ceil(1.0 / df))]))) - 2)
    ymax = pow(10, int(round(np.log10(model_mag[int(np.ceil(1.0 / df))]))) + 2)
    plot(frequency, model_response, frequency, filter_response, freq_min=1,
         freq_max=max(frequency), mag_min=ymin, mag_max=ymax, label=legend,
         title=r'%s' % plot_title, filename=filename)
    return frequency, ratio_mag, ratio_phase


class FilterGeneration(DARMModel):
    """ GDS and DCS FIR filter generation. """
    def __init__(self, config, FIR=None):
        """
        Initialize a FIRModel object

        Note that any string or path to file string in `FIR` will
        overwrite anything in the `config` parameter string or path to file

        Parameters
        ----------
        ka_pcal_line_freq    : float
            Line frequency for f_pcal1 line
        ka_esd_line_freq     : float
            Line frequency for f_ctrl, x_ctrl, DARM line
        kc_pcal_line_freq    : float
            Line frequency for f_pcal2
        ktst_esd_line_freq   : float
            Line frequency for f_tst, L3(ESD)
        pum_act_line_freq    : float
            Line frequency for f_pum, L2
        uim_act_line_freq    : float
            Line frequency for f_uim, L3
        high_pcal_line_freq  : float
            Line frequency for f_pcal3, ~1 kHz
        roaming_pcal_line_freq  : float
            Line frequency for roaming PCAL line, ~3 kHz
        src_use_ka_pcal_line    : float
            Use f_pcal1 instead of f_pcal4 for SRD detuning
        ctrl_corr_duration      : float
            Duration in seconds of control correction filter
        ctrl_corr_highpass_fcut : float
            Cut-off frequency for control correction high-pass filter
        ctrl_highpass_duration  : float
            Duration in seconds of additional highpass
            filter for the control path
        ctrl_corr_fnyq          : int
            Nyquist frequency for control correction filter
        ctrl_corr_freq_res      : float
            Frequency resolution of the control correction filters
        ctrl_highpass_freq_res  : float
            Frequency resolution of the additional highpass filter
            for the actuation path
        exclude_response_corr   : store_true
            Set this if you do not want to include the response
            correction in the residual correction filter
        res_corr_duration       : float
            Duration in seconds of residual correction filter
        res_highpass_duration   : float
            Duration in seconds of additional highpass filter for
            the residual path
        res_corr_highpass_fcut  : float
            Cut-off frequency for residual correction high-pass filter
        res_corr_lowpass_fcut   : float
            Cut-off frequency for residual correction low-pass filter
        res_corr_fnyq          : int
            Nyquist frequency for residual correction filter
        res_corr_freq_res      : float
            Frequency resolution of the residual correction filters
        res_highpass_freq_res  : float
            Frequency resolution of the additional highpass filter
            for the inverse sensing path
        calibcorr_pcal_freqs   : list, array
            List of four numbers representing frequencies at which
            pcal lines are periodically injected to measure and
            correct systematic error.
            freqs[0]**np.arange(freqs[1],freqs[2])+freqs[3])
        calibcorr_tst_freqs    : list, array
            List of four numbers representing frequencies at which
            tst lines are periodically injected to measure and
            correct systematic error.
            freqs[0]**np.arange(freqs[1],freqs[2])+freqs[3])
        calibcorr_pum_freqs    : list, array
            List of four numbers representing frequencies at which
            pum lines are periodically injected to measure and
            correct systematic error.
            freqs[0]**np.arange(freqs[1],freqs[2])+freqs[3])
        calibcorr_uim_freqs    : list, array
            List of four numbers representing frequencies at which
            uim lines are periodically injected to measure and
            correct systematic error.
            freqs[0]**np.arange(freqs[1],freqs[2])+freqs[3])
        """
        super().__init__(config)
        if 'FIR' in self._config:
            self.FIR = Model(config, measurement='FIR')
        if FIR is not None:
            self.FIR = Model(FIR, measurement='FIR')
        if not hasattr(self, 'FIR'):
            raise ValueError('No FIR parameters have been defined')

        # Load model parameters
        self.darm = DARMModel(config)
        self.calcs = CALCSModel(config)

        # Parameters directly from IFO params file
        self.arm_length = np.mean(np.array([self.darm.sensing.x_arm_length,
                                            self.darm.sensing.y_arm_length]))
        self.fcc = self.darm.sensing.coupled_cavity_pole_frequency
        self.fs = self.darm.sensing.detuned_spring_frequency
        self.fs_squared = np.real(pow(self.fs, 2.0))
        self.srcQ = self.darm.sensing.detuned_spring_q
        self.ips = self.darm.sensing.is_pro_spring

        # Create response function for plotting, etc.
        self.response_fvec = np.arange(0, 8192.25, 0.25)

        # Don't bother trying to compute things at DC
        self.R = self.darm.compute_response_function(self.response_fvec[1:])
        self.C = self.darm.sensing.compute_sensing(self.response_fvec[1:])
        self.invsens_model = 1.0 / self.C
        self.tst_model = self.darm.actuation.xarm.compute_actuation_single_stage(
            self.response_fvec[1:], stage='TST')
        self.pum_model = self.darm.actuation.xarm.compute_actuation_single_stage(
            self.response_fvec[1:], stage='PUM')
        self.uim_model = self.darm.actuation.xarm.compute_actuation_single_stage(
            self.response_fvec[1:], stage='UIM')
        self.res_corr_model = self.calcs.gds_sensing_correction(self.response_fvec[1:])
        self.ctrl_corr_model = self.calcs.gds_actuation_correction(self.response_fvec[1:],
                                                                   stage='TST')
        self.D_model = self.darm.digital.compute_response(self.response_fvec[1:])
        self.TST_corr_model = self.ctrl_corr_model
        self.act_model = self.darm.actuation.compute_actuation(self.response_fvec[1:])

        # Add in the DC component by hand to avoid RuntimeWarnings
        self.R = np.insert(self.R, 0, abs(self.R[0]))
        self.R_model_jump_delay = np.exp(2 * np.pi * 1j * self.response_fvec / 16384.0)
        self.invsens_model = np.insert(self.invsens_model, 0,
                                       abs(self.invsens_model[0])) * self.R_model_jump_delay
        self.tst_model = np.insert(self.tst_model, 0,
                                   abs(self.tst_model[0])) * self.R_model_jump_delay
        self.pum_model = np.insert(self.pum_model, 0,
                                   abs(self.pum_model[0])) * self.R_model_jump_delay
        self.uim_model = np.insert(self.uim_model, 0,
                                   abs(self.uim_model[0])) * self.R_model_jump_delay
        self.pumuim_model = self.pum_model + self.uim_model
        self.res_corr_model = np.insert(self.res_corr_model, 0, abs(self.res_corr_model[0]))
        self.ctrl_corr_model = np.insert(self.ctrl_corr_model, 0, abs(self.ctrl_corr_model[0]))
        self.TST_corr_model = np.insert(self.TST_corr_model, 0, abs(self.TST_corr_model[0]))
        self.D_model = np.insert(self.D_model, 0, abs(self.D_model[0]))
        self.act_model = np.insert(self.act_model, 0,
                                   abs(self.act_model[0])) * self.R_model_jump_delay

        # Model for response function
        self.response_function = np.array((self.response_fvec, np.real(self.R), np.imag(self.R)))

        # Model for residual path corrections
        self.res_corr_model = np.array((self.response_fvec, np.real(self.res_corr_model),
                                        np.imag(self.res_corr_model)))

        # Model for control path corrections
        self.ctrl_corr_model = np.array((self.response_fvec, np.real(self.ctrl_corr_model),
                                         np.imag(self.ctrl_corr_model)))
        self.TST_corr_model = np.array((self.response_fvec, np.real(self.TST_corr_model),
                                        np.imag(self.TST_corr_model)))
        self.PUM_corr_model = np.copy(self.ctrl_corr_model)
        self.UIM_corr_model = np.copy(self.ctrl_corr_model)

        # Model for inverse sensing path
        self.invsens_model = np.array((self.response_fvec, np.real(self.invsens_model),
                                       np.imag(self.invsens_model)))

        # Model for TST actuation path
        self.tst_model = np.array((self.response_fvec, np.real(self.tst_model),
                                   np.imag(self.tst_model)))

        # Model for PUM actuation path
        self.pum_model = np.array((self.response_fvec, np.real(self.pum_model),
                                   np.imag(self.pum_model)))

        # Model for UIM actuation path
        self.uim_model = np.array((self.response_fvec, np.real(self.uim_model),
                                   np.imag(self.uim_model)))

        # Model for PUM+UIM actuation path
        self.pumuim_model = np.array((self.response_fvec, np.real(self.pumuim_model),
                                      np.imag(self.pumuim_model)))

        # Model for Digital Filter D
        self.D_model = np.array((self.response_fvec, np.real(self.D_model), np.imag(self.D_model)))

        # Model for actuation path
        self.act_model = np.array((self.response_fvec, np.real(self.act_model),
                                   np.imag(self.act_model)))

        # FIXME: Add in check for filter's response functions
        # Calibration factors information
        self.src_pcal_line_freq = self.FIR.src_pcal_line_freq	 # f_pcal4, ~8Hz
        self.ka_pcal_line_freq = self.FIR.ka_pcal_line_freq	   # f_pcal, PCAL
        self.ka_esd_line_freq = self.FIR.ka_esd_line_freq	     # f_ctrl, x_ctrl, DARM
        self.kc_pcal_line_freq = self.FIR.kc_pcal_line_freq	   # f_pcal2
        self.ktst_esd_line_freq = self.FIR.ktst_esd_line_freq	 # f_tst, L3(ESD)
        self.pum_act_line_freq = self.FIR.pum_act_line_freq	   # f_pum, L2
        self.uim_act_line_freq = self.FIR.uim_act_line_freq	   # f_uim, L3
        self.high_pcal_line_freq = self.FIR.high_pcal_line_freq       # f_pcal3, ~1kHz
        self.roaming_pcal_line_freq = self.FIR.roaming_pcal_line_freq  # ~3kHz
        self.ctrl_corr_fNyq = self.FIR.ctrl_corr_fnyq

        if hasattr(self, 'ka_pcal_line_freq') and self.ka_pcal_line_freq == '':
            self.ka_pcal_line_freq = 1.0
            print("EPICS involving the k_a PCAL line freq will be nonsense.")
        if hasattr(self, 'uim_act_line_freq') and self.uim_act_line_freq == '':
            self.uim_act_line_freq = 1.0
            print("EPICS involving the UIM line freq will be nonsense.")
        if hasattr(self, 'pum_act_line_freq') and self.pum_act_line_freq == '':
            self.pum_act_line_freq = 1.0
            print("EPICS involving the PUM line freq will be nonsense.")
        if hasattr(self, 'ktst_esd_line_freq') and self.ktst_esd_line_freq == '':
            self.ktst_esd_line_freq = 1.0
            print("EPICS involving the TST line freq will be nonsense.")
        if hasattr(self, 'kc_pcal_line_freq') and self.kc_pcal_line_freq == '':
            self.kc_pcal_line_freq = 1.0
            print("EPICS involving the k_c PCAL line freq will be nonsense.")
        if hasattr(self, 'src_pcal_line_freq') and self.src_pcal_line_freq == '':
            self.src_pcal_line_freq = 1.0
            print("EPICS involving the SRC PCAL line freq will be nonsense.")
        if hasattr(self, 'roaming_pcal_line_freq') and self.roaming_pcal_line_freq == '':
            self.roaming_pcal_line_freq = 1.0
            print("EPICS involving the roaming PCAL line freq will be nonsense.")

        self.coupled_cavity = self.darm.sensing.optical_response(self.fcc, self.fs,
                                                                 self.srcQ,
                                                                 pro_spring=self.ips)
        # FIXME: Use old_school_pars for computing Pcal correction factors
        # FIXME: Store EPICS records. Problems in EPICS record numbering. Identifying EPICS 23-47.
        # Ref LIGO-T1700106-v10: EPICS channel number only up to 30.

    def GDS(self, ctrl_window_type='dpss', res_window_type='dpss', make_plot=True,
            output_filename='GDS.npz', plots_directory='../examples/GDS_plots'):
        """ GDS FIR filter generation

        Parameters
        ----------
        ctrl_window_type : str
            'dpss', 'kaiser', 'dolph-chebyshev', or 'hann'
        res_window_type : str
            'dpss', 'kaiser', 'dolph-chebyshev', or 'hann'
        make_plot : True or False
            Set this to make diagnostic plots of filters.
        output_filename : str
            Output filename
        plots_directory : str
            Directory to which to save diagnostic plots.

        Returns
        -------
        output_filename.npz, diagnostic plots of filters
        """

        # Additional zeros necessary to correct the front end output
        self.extra_zeros_tst = [] if self.FIR.extra_zeros_tst == \
            '[]' else self.FIR.extra_zeros_tst.strip('[]').split(',')
        for i in range(len(self.extra_zeros_tst)):
            self.extra_zeros_tst[i] = float(self.extra_zeros_tst[i])
        self.extra_zeros_pum = [] if self.FIR.extra_zeros_pum == \
            '[]' else self.FIR.extra_zeros_pum.strip('[]').split(',')
        for i in range(len(self.extra_zeros_pum)):
            self.extra_zeros_pum[i] = float(self.extra_zeros_pum[i])
        self.extra_zeros_uim = [] if self.FIR.extra_zeros_uim == \
            '[]' else self.FIR.extra_zeros_uim.strip('[]').split(',')
        for i in range(len(self.extra_zeros_uim)):
            self.extra_zeros_uim[i] = float(self.extra_zeros_uim[i])

        # Checking latencies input values. There's problem when tried to put
        # it on configuration files especially as NoneType inputs, it will
        # recognized as string which caused problem in calculation of self.latency
        # on FIRfilter class.
        self.ctrl_corr_latency = self.FIR.ctrl_corr_latency
        self.ctrl_highpass_latency = self.FIR.ctrl_highpass_latency
        self.res_corr_latency = self.FIR.res_corr_latency
        self.res_highpass_latency = self.FIR.res_highpass_latency

        if hasattr(self, 'ctrl_corr_latency') and self.ctrl_corr_latency == '':
            self.ctrl_corr_latency = None
        if hasattr(self, 'ctrl_highpass_latency') and self.ctrl_highpass_latency == '':
            self.ctrl_highpass_latency = None
        if hasattr(self, 'res_corr_latency') and self.res_corr_latency == '':
            self.res_corr_latency = None
        if hasattr(self, 'res_highpass_latency') and self.res_highpass_latency == '':
            self.res_highpass_latency = None
        # Compute FIR parameters
        # Note: Highpass filtering is applied to both the control and residual chains
        # mainly for computational reasons.
        # Applying highpass filtering to both chains reduces the overall cost and latency
        # required to achieve sufficient highpass filtering.
        A_FIRpars = FIRfilter(fNyq=self.FIR.ctrl_corr_fnyq,
                              dur=self.FIR.ctrl_corr_duration,
                              highpass_fcut=self.FIR.ctrl_corr_highpass_fcut,
                              latency=self.ctrl_corr_latency,
                              window_type=ctrl_window_type,
                              freq_res=self.FIR.ctrl_corr_freq_res)
        A_freq = A_FIRpars.freq_array
        act_window_type = A_FIRpars.window_type
        act_freq_res = A_FIRpars.freq_res
        A_highpass_FIRpars = FIRfilter(fNyq=self.FIR.ctrl_corr_fnyq,
                                       dur=self.FIR.ctrl_highpass_duration,
                                       highpass_fcut=self.FIR.ctrl_corr_highpass_fcut,
                                       latency=self.ctrl_highpass_latency,
                                       window_type=ctrl_window_type,
                                       freq_res=self.FIR.ctrl_highpass_freq_res)

        Cinv_FIRpars = FIRfilter(fNyq=self.FIR.res_corr_fnyq,
                                 dur=self.FIR.res_corr_duration,
                                 lowpass_fcut=self.FIR.res_corr_lowpass_fcut,
                                 highpass_fcut=self.FIR.res_corr_highpass_fcut,
                                 latency=self.res_corr_latency,
                                 window_type=res_window_type,
                                 freq_res=self.FIR.res_corr_freq_res)
        Cinv_freq = Cinv_FIRpars.freq_array
        invsens_window_type = Cinv_FIRpars.window_type
        invsens_freq_res = Cinv_FIRpars.freq_res

        Cinv_highpass_FIRpars = FIRfilter(fNyq=self.FIR.res_highpass_fnyq,
                                          dur=self.FIR.res_highpass_duration,
                                          highpass_fcut=self.FIR.res_corr_highpass_fcut,
                                          latency=self.res_highpass_latency,
                                          window_type=res_window_type,
                                          freq_res=self.FIR.res_highpass_freq_res)

        # Don't try to calculate response at zero frequency
        ctrl_corr_fd = self.calcs.gds_actuation_correction(A_freq[1:], stage='TST')
        TST_corr_fd = ctrl_corr_fd

        # Add in the DC component by hand to avoid RuntimeWarnings
        ctrl_corr_fd = np.insert(ctrl_corr_fd, 0, 0)
        TST_corr_fd = np.insert(TST_corr_fd, 0, 0)
        for i in range(len(self.extra_zeros_tst)):
            TST_corr_fd *= (1 + 1j * A_freq / self.extra_zeros_tst[i])
        TST_corr_fd *= np.exp(-2 * np.pi * 1j * A_freq * float(self.FIR.extra_delay_tst))
        PUM_corr_fd = np.copy(ctrl_corr_fd)
        for i in range(len(self.extra_zeros_pum)):
            PUM_corr_fd *= (1 + 1j * A_freq / self.extra_zeros_pum[i])
        PUM_corr_fd *= np.exp(-2 * np.pi * 1j * A_freq * float(self.FIR.extra_delay_pum))
        UIM_corr_fd = np.copy(ctrl_corr_fd)
        for i in range(len(self.extra_zeros_uim)):
            UIM_corr_fd *= (1 + 1j * A_freq / self.extra_zeros_uim[i])
        UIM_corr_fd *= np.exp(-2 * np.pi * 1j * A_freq * float(self.FIR.extra_delay_uim))

        if not self.FIR.exclude_response_corr:
            # Since we downsample the actuation, we'll use the inverse sensing filter
            # to model the entire response above the Nyquist rate of the actuation path.
            # We will therefore smoothly roll off the actuation filter as it
            # approaches the Nyquist rate.
            full_hann = np.hanning(round(A_FIRpars.fNyquist / A_FIRpars.df / 8))
            half_hann = full_hann[(len(full_hann) // 2 + 1):]
            ctrl_corr_fd[len(ctrl_corr_fd) - len(half_hann):] *= half_hann
            TST_corr_fd[len(TST_corr_fd) - len(half_hann):] *= half_hann

        # Don't try to calculate response at zero frequency
        sensing_corr_fd = self.calcs.gds_sensing_correction(Cinv_freq[1:])
        C = self.darm.sensing.compute_sensing(Cinv_freq[1:])
        RforCinv = self.darm.compute_response_function(Cinv_freq[1:])

        # Add in the DC component by hand to avoid RuntimeWarning.
        # Set it to 1 for now since we'll be dividing by it.  It will be zeroed out below.
        sensing_corr_fd = np.insert(sensing_corr_fd, 0, 1)
        C = np.insert(C, 0, 1)
        RforCinv = np.insert(RforCinv, 0, 1)

        # Since we downsample the actuation, compensate for the small loss of accuracy
        # by smoothly changing C_corr to 1/R_corr above the actuation path's Nyquist rate
        invsens_calcs = sensing_corr_fd / C
        response_inv_corr = invsens_calcs / RforCinv
        Cwindow = np.ones(len(sensing_corr_fd))
        full_hann = np.hanning(round(A_FIRpars.fNyquist / Cinv_FIRpars.df / 8))
        half_hann = full_hann[(len(full_hann) // 2 + 1):]
        indexNy = round(A_FIRpars.fNyquist / Cinv_FIRpars.df)
        Cwindow[indexNy - len(half_hann):indexNy] = half_hann
        Cwindow[indexNy:] = 0
        Rwindow = np.ones(len(sensing_corr_fd)) - Cwindow
        if not self.FIR.exclude_response_corr:
            sensing_corr_fd = Cwindow * sensing_corr_fd + Rwindow * response_inv_corr

        res_corr_fd = 1 / sensing_corr_fd
        # Add in the DC component by hand to avoid RuntimeWarnings
        res_corr_fd[0] = 0

        # Generate FIR filter from frequency-domain model
        Cinv_highpass_fnyq_df = \
            np.ones(1 + int(round(Cinv_highpass_FIRpars.fNyquist / Cinv_highpass_FIRpars.df)))
        [res_highpass_td, res_highpass_model] = \
            createFIRfilter(Cinv_highpass_FIRpars,
                            Cinv_highpass_fnyq_df) if self.FIR.res_highpass_duration else [[], []]
        [res_corr_td, res_corr_filt_model] = createFIRfilter(Cinv_FIRpars, res_corr_fd)

        # Generate an inverse sensing residual correction filter
        # that does not include the coupled cavity pole.
        # Divide out the response of the two-tap filter that would be used to apply the cavity pole.
        res_corr_noccpole_fd = \
            res_corr_fd / two_tap_zero_filter_response([self.fcc], 16384, Cinv_freq)
        [res_corr_noccpole_td, model] = createFIRfilter(Cinv_FIRpars, res_corr_noccpole_fd)

        # Generate an inverse sensing FIR filter that
        # does not include the coupled cavity pole or SRC detuning.
        if np.real(self.fs) != 0 and self.srcQ != 0:
            fsrQ1 = (self.fs / 2.0) * (1.0 / self.srcQ + np.sqrt(1.0 / self.srcQ / self.srcQ + 4.0))
            fsrQ2 = (self.fs / 2.0) * (1.0 / self.srcQ - np.sqrt(1.0 / self.srcQ / self.srcQ + 4.0))
            res_corr_nopole_fd = \
                res_corr_fd / two_tap_zero_filter_response([self.fcc, fsrQ1, fsrQ2],
                                                           16384, Cinv_freq)
            # fs^2 is a gain factor as well
            res_corr_nopole_fd /= self.fs_squared
        else:
            res_corr_nopole_fd = np.copy(res_corr_noccpole_fd)

        # Multiply by f^2
        res_corr_nopole_fd *= Cinv_freq * Cinv_freq
        [res_corr_nopole_td, model] = createFIRfilter(Cinv_FIRpars, res_corr_nopole_fd)
        res_corr_nopole_fd = correctFIRfilter([Cinv_FIRpars, Cinv_highpass_FIRpars],
                                              [res_corr_nopole_td, res_highpass_td],
                                              res_corr_nopole_fd, [5, 9, 100, 150])
        [res_corr_nopole_td, model] = createFIRfilter(Cinv_FIRpars, res_corr_nopole_fd)

        [ctrl_highpass_td, ctrl_highpass_model] = \
            createFIRfilter(A_highpass_FIRpars,
                            np.ones(1 +
                                    int(round(A_highpass_FIRpars.fNyquist /
                                        A_highpass_FIRpars.df))))\
            if self.FIR.ctrl_highpass_duration else [[], []]
        [ctrl_corr_td, ctrl_corr_filt_model] = createFIRfilter(A_FIRpars, ctrl_corr_fd)
        [TST_corr_td, TST_corr_filt_model] = createFIRfilter(A_FIRpars, TST_corr_fd)
        [PUM_corr_td, PUM_corr_filt_model] = createFIRfilter(A_FIRpars, PUM_corr_fd)
        [UIM_corr_td, UIM_corr_filt_model] = createFIRfilter(A_FIRpars, UIM_corr_fd)

        if make_plot:
            # Sample the model at 8 times the frequency resolution of the filter,
            # and test the filter at that frequency resolution as well.
            # (computeFIRfilters.check_td_vs_fd does that by default.)
            CinvPlot_freq = np.arange(0, Cinv_FIRpars.fNyquist + Cinv_FIRpars.df / 8.0,
                                      Cinv_FIRpars.df / 8.0)
            # Don't try to calculate response at zero frequency
            sensing_corr_fd_for_plot = self.calcs.gds_sensing_correction(CinvPlot_freq[1:])
            CForPlot = self.darm.sensing.compute_sensing(CinvPlot_freq[1:])
            RforCinvPlot = self.darm.compute_response_function(CinvPlot_freq[1:])

            if not self.FIR.exclude_response_corr:
                # same correction as above
                invsens_calcs_for_plot = sensing_corr_fd_for_plot / CForPlot
                response_inv_corr_for_plot = invsens_calcs_for_plot / RforCinvPlot
                CwindowForPlot = np.ones(len(sensing_corr_fd_for_plot))
                full_hann_for_plot = np.hanning(8 * round(A_FIRpars.fNyquist / Cinv_FIRpars.df / 8))
                half_hann_for_plot = full_hann_for_plot[(len(full_hann_for_plot) // 2 + 1):]
                indexNyForPlot = round(8 * A_FIRpars.fNyquist / Cinv_FIRpars.df)
                CwindowForPlot[indexNyForPlot
                               - len(half_hann_for_plot):indexNyForPlot] = half_hann_for_plot
                CwindowForPlot[indexNyForPlot:] = 0
                RwindowForPlot = np.ones(len(sensing_corr_fd_for_plot)) - CwindowForPlot
                sensing_corr_fd_for_plot = CwindowForPlot * sensing_corr_fd_for_plot + \
                    RwindowForPlot * response_inv_corr_for_plot

            invsensing_corr_fd_for_plot = 1/sensing_corr_fd_for_plot
            # Add in the DC component by hand to avoid RuntimeWarnings
            invsensing_corr_fd_for_plot = np.insert(invsensing_corr_fd_for_plot, 0, 0)
            if np.isinf(invsensing_corr_fd_for_plot[0]):
                invsensing_corr_fd_for_plot[0] = invsensing_corr_fd_for_plot[1]
            invsensing_corr_noccpole_fd_for_plot = \
                invsensing_corr_fd_for_plot / two_tap_zero_filter_response([self.fcc],
                                                                           16384, CinvPlot_freq)
            if np.real(self.fs) != 0 and self.srcQ != 0:
                srQ = np.sqrt(1.0 / self.srcQ / self.srcQ + 4.0)
                fsrQ1 = (self.fs / 2.0) * (1.0 / self.srcQ + srQ)
                fsrQ2 = (self.fs / 2.0) * (1.0 / self.srcQ - srQ)
                invsensing_corr_nopole_fd_for_plot = \
                    invsensing_corr_fd_for_plot / two_tap_zero_filter_response([self.fcc,
                                                                                fsrQ1, fsrQ2],
                                                                               16384, CinvPlot_freq)
                # fs^2 is a gain factor as well
                invsensing_corr_nopole_fd_for_plot /= self.fs_squared
            else:
                invsensing_corr_nopole_fd_for_plot = np.copy(invsensing_corr_noccpole_fd_for_plot)
            # Multiply by f^2
            invsensing_corr_nopole_fd_for_plot *= CinvPlot_freq * CinvPlot_freq

            # FIXME: Add plot_filter into plot.py
            check_td_vs_fd(np.copy(res_corr_td), invsensing_corr_fd_for_plot,
                           fNyq=Cinv_FIRpars.fNyquist, delay_samples=Cinv_FIRpars.delay_samples,
                           highpasstd=np.copy(res_highpass_td),
                           highpass_fNyq=Cinv_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=Cinv_highpass_FIRpars.delay_samples,
                           filename="%s/res_corr_fd_comparison.png" % plots_directory,
                           plot_title="Residual corrections comparison (%s)" % output_filename)
            check_td_vs_fd(np.copy(res_corr_noccpole_td), invsensing_corr_noccpole_fd_for_plot,
                           fNyq=Cinv_FIRpars.fNyquist, delay_samples=Cinv_FIRpars.delay_samples,
                           highpasstd=np.copy(res_highpass_td),
                           highpass_fNyq=Cinv_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=Cinv_highpass_FIRpars.delay_samples,
                           filename="%s/res_corr_noccpole_fd_comparison.png" % plots_directory,
                           plot_title="Res Corr No CC Pole comparison (%s)" % output_filename)
            check_td_vs_fd(np.copy(res_corr_nopole_td), invsensing_corr_nopole_fd_for_plot,
                           fNyq=Cinv_FIRpars.fNyquist, delay_samples=Cinv_FIRpars.delay_samples,
                           highpasstd=np.copy(res_highpass_td),
                           highpass_fNyq=Cinv_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=Cinv_highpass_FIRpars.delay_samples,
                           filename="%s/res_corr_nopole_fd_comparison.png" % plots_directory,
                           plot_title="Res Corr No Pole comparison (%s)" % output_filename,
                           ymax_increase=10000000)

        if make_plot:
            # Sample the model at 8 times the frequency resolution of the filter,
            # and test the filter at that frequency resolution as well.
            # (computeFIRfilters.check_td_vs_fd does that by default.)
            A_plot_freq = np.arange(0, A_FIRpars.fNyquist + A_FIRpars.df / 8.0, A_FIRpars.df / 8.0)
            # FIXME: I don't know why we have to call this again, but somehow actProd
            # from above seems to be carried as a pointer instead of copied
            # Don't try to calculate response at zero frequency
            AforPlot = self.calcs.gds_actuation_correction(A_plot_freq[1:], stage='TST')
            TSTforPlot = AforPlot
            # Add in the DC component by hand to avoid RuntimeWarnings
            AforPlot = np.insert(AforPlot, 0, 0)
            TSTforPlot = np.insert(TSTforPlot, 0, 0)
            PUMforPlot = np.copy(AforPlot)
            UIMforPlot = np.copy(AforPlot)
            for i in range(len(self.extra_zeros_tst)):
                TSTforPlot *= (1 + 1j * A_plot_freq / self.extra_zeros_tst[i])
            TSTforPlot *= np.exp(-2 * np.pi * 1j * A_plot_freq * float(self.FIR.extra_delay_tst))
            for i in range(len(self.extra_zeros_pum)):
                PUMforPlot *= (1 + 1j * A_plot_freq / self.extra_zeros_pum[i])
            PUMforPlot *= np.exp(-2 * np.pi * 1j * A_plot_freq * float(self.FIR.extra_delay_pum))
            for i in range(len(self.extra_zeros_uim)):
                UIMforPlot *= (1 + 1j * A_plot_freq / self.extra_zeros_uim[i])
            UIMforPlot *= np.exp(-2 * np.pi * 1j * A_plot_freq * float(self.FIR.extra_delay_uim))

            check_td_vs_fd(np.copy(ctrl_corr_td), AforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples,
                           highpasstd=np.copy(ctrl_highpass_td),
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/ctrl_corr_fd_comparison.png" % plots_directory,
                           plot_title="Control corrections comparison (%s)" %
                           output_filename)
            check_td_vs_fd(np.copy(TST_corr_td), TSTforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples,
                           highpasstd=np.copy(ctrl_highpass_td),
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/TST_corr_fd_comparison.png" % plots_directory,
                           plot_title="TST corrections comparison (%s)" %
                           output_filename)
            check_td_vs_fd(np.copy(PUM_corr_td), PUMforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples,
                           highpasstd=np.copy(ctrl_highpass_td),
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/PUM_corr_fd_comparison.png" % plots_directory,
                           plot_title="PUM corrections comparison (%s)" %
                           output_filename)
            check_td_vs_fd(np.copy(UIM_corr_td), UIMforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples,
                           highpasstd=np.copy(ctrl_highpass_td),
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/UIM_corr_fd_comparison.png" % plots_directory,
                           plot_title="UIM corrections comparison (%s)" %
                           output_filename)

        # Calibration systematic error information
        if self.FIR.calibcorr_pcal_freqs is not None:
            calibcorr_pcal_freqs = self.FIR.calibcorr_pcal_freqs
            calibcorr_tst_freqs = self.FIR.calibcorr_tst_freqs
            calibcorr_pum_freqs = self.FIR.calibcorr_pum_freqs
            calibcorr_uim_freqs = self.FIR.calibcorr_uim_freqs

            for i in range(2):
                calibcorr_pcal_freqs[i] = int(calibcorr_pcal_freqs[i])
                calibcorr_tst_freqs[i] = int(calibcorr_tst_freqs[i])
                calibcorr_pum_freqs[i] = int(calibcorr_pum_freqs[i])
                calibcorr_uim_freqs[i] = int(calibcorr_uim_freqs[i])
            for i in range(2, 4):
                calibcorr_pcal_freqs[i] = float(calibcorr_pcal_freqs[i])
                calibcorr_tst_freqs[i] = float(calibcorr_tst_freqs[i])
                calibcorr_pum_freqs[i] = float(calibcorr_pum_freqs[i])
                calibcorr_uim_freqs[i] = float(calibcorr_uim_freqs[i])
            if len(calibcorr_pcal_freqs) > 4:
                calibcorr_pcal_freqs[4] = int(calibcorr_pcal_freqs[4])
            else:
                calibcorr_pcal_freqs.append(0)
            if len(calibcorr_tst_freqs) > 4:
                calibcorr_tst_freqs[4] = int(calibcorr_tst_freqs[4])
            else:
                calibcorr_tst_freqs.append(0)
            if len(calibcorr_pum_freqs) > 4:
                calibcorr_pum_freqs[4] = int(calibcorr_pum_freqs[4])
            else:
                calibcorr_pum_freqs.append(0)
            if len(calibcorr_uim_freqs) > 4:
                calibcorr_uim_freqs[4] = int(calibcorr_uim_freqs[4])
            else:
                calibcorr_uim_freqs.append(0)

            pcalf = 1 + int(np.log(calibcorr_pcal_freqs[2] -
                                   calibcorr_pcal_freqs[3]) / np.log(calibcorr_pcal_freqs[0]))
            calibcorr_pcal_freqs0 = \
                calibcorr_pcal_freqs[0]**np.arange(calibcorr_pcal_freqs[1],
                                                   pcalf) + calibcorr_pcal_freqs[3]
            tstf = 1 + int(np.log(calibcorr_tst_freqs[2] -
                                  calibcorr_tst_freqs[3]) / np.log(calibcorr_tst_freqs[0]))
            calibcorr_tst_freqs0 = \
                calibcorr_tst_freqs[0]**np.arange(calibcorr_tst_freqs[1],
                                                  tstf) + calibcorr_tst_freqs[3]
            pumf = 1 + int(np.log(calibcorr_pum_freqs[2] -
                                  calibcorr_pum_freqs[3]) / np.log(calibcorr_pum_freqs[0]))
            calibcorr_pum_freqs0 = \
                calibcorr_pum_freqs[0]**np.arange(calibcorr_pum_freqs[1],
                                                  pumf) + calibcorr_pum_freqs[3]
            uimf = 1 + int(np.log(calibcorr_uim_freqs[2] -
                                  calibcorr_uim_freqs[3]) / np.log(calibcorr_uim_freqs[0]))
            calibcorr_uim_freqs0 = \
                calibcorr_uim_freqs[0]**np.arange(calibcorr_uim_freqs[1],
                                                  uimf) + calibcorr_uim_freqs[3]

            num_fill = calibcorr_pcal_freqs[0] - 1
            for i in range(calibcorr_pcal_freqs[4]):
                df = calibcorr_pcal_freqs0[1] - calibcorr_pcal_freqs0[0]
                j = 2
                dp = (calibcorr_pcal_freqs0[j] - calibcorr_pcal_freqs0[j - 1]) / df
                while dp < 1.01 and j < len(calibcorr_pcal_freqs0) - 1:
                    j += 1
                while j < len(calibcorr_pcal_freqs0):
                    df = (calibcorr_pcal_freqs0[j] -
                          calibcorr_pcal_freqs0[j - 1]) / (num_fill + 1)
                    for k in range(1, 1 + num_fill):
                        f = calibcorr_pcal_freqs0[j - 1] + k * df
                        calibcorr_pcal_freqs0 = np.insert(calibcorr_pcal_freqs0, j, f)
                        j += 1
                    j += 1
                df *= num_fill + 1
                f = calibcorr_pcal_freqs0[j - 1] + df
                while f <= calibcorr_pcal_freqs[2]:
                    calibcorr_pcal_freqs0 = np.insert(calibcorr_pcal_freqs0, j, f)
                    j += 1
                    f += df
            calibcorr_pcal_freqs = np.asarray(calibcorr_pcal_freqs0)

            num_fill = calibcorr_tst_freqs[0] - 1
            for i in range(calibcorr_tst_freqs[4]):
                df = calibcorr_tst_freqs0[1] - calibcorr_tst_freqs0[0]
                j = 2
                dp = (calibcorr_tst_freqs0[j] - calibcorr_tst_freqs0[j - 1]) / df
                while dp < 1.01 and j < len(calibcorr_tst_freqs0) - 1:
                    j += 1
                while j < len(calibcorr_tst_freqs0):
                    df = (calibcorr_tst_freqs0[j] -
                          calibcorr_tst_freqs0[j - 1]) / (num_fill + 1)
                    for k in range(1, 1 + num_fill):
                        f = calibcorr_tst_freqs0[j - 1] + k * df
                        calibcorr_tst_freqs0 = np.insert(calibcorr_tst_freqs0, j, f)
                        j += 1
                    j += 1
                df *= num_fill + 1
                f = calibcorr_tst_freqs0[j - 1] + df
                while f <= calibcorr_tst_freqs[2]:
                    calibcorr_tst_freqs0 = np.insert(calibcorr_tst_freqs0, j, f)
                    j += 1
                    f += df
            calibcorr_tst_freqs = np.asarray(calibcorr_tst_freqs0)

            num_fill = calibcorr_pum_freqs[0] - 1
            for i in range(calibcorr_pum_freqs[4]):
                df = calibcorr_pum_freqs0[1] - calibcorr_pum_freqs0[0]
                j = 2
                dp = (calibcorr_pum_freqs0[j] - calibcorr_pum_freqs0[j - 1]) / df
                while dp < 1.01 and j < len(calibcorr_pum_freqs0) - 1:
                    j += 1
                while j < len(calibcorr_pum_freqs0):
                    df = (calibcorr_pum_freqs0[j] -
                          calibcorr_pum_freqs0[j - 1]) / (num_fill + 1)
                    for k in range(1, 1 + num_fill):
                        f = calibcorr_pum_freqs0[j - 1] + k * df
                        calibcorr_pum_freqs0 = np.insert(calibcorr_pum_freqs0, j, f)
                        j += 1
                    j += 1
                df *= num_fill + 1
                f = calibcorr_pum_freqs0[j - 1] + df
                while f <= calibcorr_pum_freqs[2]:
                    calibcorr_pum_freqs0 = np.insert(calibcorr_pum_freqs0, j, f)
                    j += 1
                    f += df
            calibcorr_pum_freqs = np.asarray(calibcorr_pum_freqs0)

            num_fill = calibcorr_uim_freqs[0] - 1
            for i in range(calibcorr_uim_freqs[4]):
                df = calibcorr_uim_freqs0[1] - calibcorr_uim_freqs0[0]
                j = 2
                dp = (calibcorr_uim_freqs0[j] - calibcorr_uim_freqs0[j - 1]) / df
                while dp < 1.01 and j < len(calibcorr_uim_freqs0) - 1:
                    j += 1
                while j < len(calibcorr_uim_freqs0):
                    df = (calibcorr_uim_freqs0[j] -
                          calibcorr_uim_freqs0[j - 1]) / (num_fill + 1)
                    for k in range(1, 1 + num_fill):
                        f = calibcorr_uim_freqs0[j - 1] + k * df
                        calibcorr_uim_freqs0 = np.insert(calibcorr_uim_freqs0, j, f)
                        j += 1
                    j += 1
                df *= num_fill + 1
                f = calibcorr_uim_freqs0[j - 1] + df
                while f <= calibcorr_uim_freqs[2]:
                    calibcorr_uim_freqs0 = np.insert(calibcorr_uim_freqs0, j, f)
                    j += 1
                    f += df
            calibcorr_uim_freqs = np.asarray(calibcorr_uim_freqs0)

            calibcorr_freqs = np.concatenate((calibcorr_pcal_freqs, calibcorr_tst_freqs,
                                              calibcorr_pum_freqs, calibcorr_uim_freqs))

            calibcorr_freqs = np.sort(calibcorr_freqs)

            # sensProd_calibcorr = darm.sensing.old_school_senspars(calibcorr_freqs)
            # cres_calibcorr = sensProd_calibcorr.C_NoCav
            cres_calibcorr = self.darm.sensing.compute_sensing(calibcorr_freqs) / \
                signal.freqresp(self.coupled_cavity, 2*np.pi*calibcorr_freqs)
            D_calibcorr = self.darm.digital.compute_response(calibcorr_freqs)
            uim_calibcorr, pum_calibcorr, tst_calibcorr = \
                self.darm.actuation.xarm.drivealign_to_longitudinal_displacement(calibcorr_freqs)
            tst = self.darm.actuation.xarm.compute_actuation_single_stage(calibcorr_freqs,
                                                                          stage='TST')
            pum = self.darm.actuation.xarm.compute_actuation_single_stage(calibcorr_freqs,
                                                                          stage='PUM')
            uim = self.darm.actuation.xarm.compute_actuation_single_stage(calibcorr_freqs,
                                                                          stage='UIM')
            Ftst_calibcorr = tst / tst_calibcorr
            Fpum_calibcorr = pum / pum_calibcorr
            Fuim_calibcorr = uim / uim_calibcorr

            cres_calibcorr = np.array((calibcorr_freqs, np.real(cres_calibcorr),
                                       np.imag(cres_calibcorr)), dtype=object)
            D_calibcorr = np.array((calibcorr_freqs, np.real(D_calibcorr),
                                    np.imag(D_calibcorr)), dtype=object)
            tst_calibcorr = np.array((calibcorr_freqs, np.real(tst_calibcorr),
                                      np.imag(tst_calibcorr)), dtype=object)
            Ftst_calibcorr = np.array((calibcorr_freqs, np.real(Ftst_calibcorr),
                                       np.imag(Ftst_calibcorr)), dtype=object)
            pum_calibcorr = np.array((calibcorr_freqs, np.real(pum_calibcorr),
                                      np.imag(pum_calibcorr)), dtype=object)
            Fpum_calibcorr = np.array((calibcorr_freqs, np.real(Fpum_calibcorr),
                                       np.imag(Fpum_calibcorr)), dtype=object)
            uim_calibcorr = np.array((calibcorr_freqs, np.real(uim_calibcorr),
                                      np.imag(uim_calibcorr)), dtype=object)
            Fuim_calibcorr = np.array((calibcorr_freqs, np.real(Fuim_calibcorr),
                                       np.imag(Fuim_calibcorr)), dtype=object)

            # Still need Pcal correction factors and DAQ downsampling TFs
            pcal_corr_calibcorr = \
                self.darm.pcal.compute_pcal_correction(calibcorr_pcal_freqs) * \
                np.exp(-2 * np.pi * 1j * calibcorr_pcal_freqs / 16384)
            pcal_corr_calibcorr = np.array((calibcorr_pcal_freqs, np.real(pcal_corr_calibcorr),
                                            np.imag(pcal_corr_calibcorr)), dtype=object)
            daqdownsampling = daqdownsamplingfilters(2**14, 2**9, 'biquad', 'v3')
            daqdownsampling_tst_calibcorr = \
                signal.dfreqresp(daqdownsampling,
                                 2.0 * np.pi * calibcorr_tst_freqs / 2**14)[1] * \
                np.exp(2 * np.pi * 1j * calibcorr_tst_freqs / 16384)
            daqdownsampling_tst_calibcorr = np.array((calibcorr_tst_freqs,
                                                      np.real(daqdownsampling_tst_calibcorr),
                                                      np.imag(daqdownsampling_tst_calibcorr)),
                                                     dtype=object)
            daqdownsampling_pum_calibcorr = \
                signal.dfreqresp(daqdownsampling,
                                 2.0 * np.pi * calibcorr_pum_freqs / 2**14)[1] * \
                np.exp(2 * np.pi * 1j * calibcorr_pum_freqs / 16384)
            daqdownsampling_pum_calibcorr = np.array((calibcorr_pum_freqs,
                                                      np.real(daqdownsampling_pum_calibcorr),
                                                      np.imag(daqdownsampling_pum_calibcorr)),
                                                     dtype=object)
            daqdownsampling_uim_calibcorr = \
                signal.dfreqresp(daqdownsampling,
                                 2.0 * np.pi * calibcorr_uim_freqs / 2**14)[1] * \
                np.exp(2 * np.pi * 1j * calibcorr_uim_freqs / 16384)
            daqdownsampling_uim_calibcorr = np.array((calibcorr_uim_freqs,
                                                      np.real(daqdownsampling_uim_calibcorr),
                                                      np.imag(daqdownsampling_uim_calibcorr)),
                                                     dtype=object)

        else:
            cres_calibcorr = D_calibcorr = []
            tst_calibcorr = Ftst_calibcorr = []
            pum_calibcorr = Fpum_calibcorr = []
            uim_calibcorr = Fuim_calibcorr = []
            pcal_corr_calibcorr = daqdownsampling_tst_calibcorr = []
            daqdownsampling_pum_calibcorr = daqdownsampling_uim_calibcorr = []

        # Save filter output to file
        res_corr_delay = Cinv_FIRpars.delay_samples
        res_highpass_delay = Cinv_highpass_FIRpars.delay_samples
        res_highpass_sr = Cinv_highpass_FIRpars.fNyquist * 2
        ctrl_corr_delay = A_FIRpars.delay_samples
        ctrl_highpass_delay = A_highpass_FIRpars.delay_samples
        ctrl_corr_sr = A_FIRpars.fNyquist * 2
        ctrl_corr_filter = ctrl_corr_td
        TST_corr_filter = TST_corr_td
        PUM_corr_filter = PUM_corr_td
        UIM_corr_filter = UIM_corr_td
        res_corr_filter = res_corr_td
        res_corr_noccpole_filter = res_corr_noccpole_td
        res_corr_nopole_filter = res_corr_nopole_td
        ctrl_highpass = ctrl_highpass_td
        res_highpass = res_highpass_td

        return np.savez(output_filename, arm_length=self.arm_length, fcc=self.fcc, fs=self.fs,
                        fs_squared=self.fs_squared, srcQ=self.srcQ,
                        res_corr_model=self.res_corr_model, ctrl_corr_model=self.ctrl_corr_model,
                        TST_corr_model=self.TST_corr_model, PUM_corr_model=self.PUM_corr_model,
                        UIM_corr_model=self.UIM_corr_model, tst_model=self.tst_model,
                        pum_model=self.pum_model, uim_model=self.uim_model,
                        pumuim_model=self.pumuim_model, D_model=self.D_model,
                        act_window_type=act_window_type, act_freq_res=act_freq_res,
                        invsens_model=self.invsens_model,
                        invsens_window_type=invsens_window_type,
                        invsens_freq_res=invsens_freq_res,
                        response_function=self.response_function,
                        res_corr_delay=res_corr_delay,
                        ctrl_corr_delay=ctrl_corr_delay,
                        ctrl_highpass_delay=ctrl_highpass_delay,
                        res_highpass_delay=res_highpass_delay,
                        ctrl_corr_sr=ctrl_corr_sr,
                        res_highpass_sr=res_highpass_sr,
                        ctrl_corr_filter=ctrl_corr_filter,
                        ctrl_corr_filt_model=ctrl_corr_filt_model,
                        TST_corr_filter=TST_corr_filter, TST_corr_filt_model=TST_corr_filt_model,
                        PUM_corr_filter=PUM_corr_filter, PUM_corr_filt_model=PUM_corr_filt_model,
                        UIM_corr_filter=UIM_corr_filter, UIM_corr_filt_model=UIM_corr_filt_model,
                        res_corr_filter=res_corr_filter, res_corr_filt_model=res_corr_filt_model,
                        res_corr_noccpole_filter=res_corr_noccpole_filter,
                        res_corr_nopole_filter=res_corr_nopole_filter, ctrl_highpass=ctrl_highpass,
                        res_highpass=res_highpass, src_pcal_line_freq=self.src_pcal_line_freq,
                        ka_pcal_line_freq=self.ka_pcal_line_freq,
                        ka_esd_line_freq=self.ka_esd_line_freq,
                        pum_act_line_freq=self.pum_act_line_freq,
                        uim_act_line_freq=self.uim_act_line_freq,
                        kc_pcal_line_freq=self.kc_pcal_line_freq,
                        ktst_esd_line_freq=self.ktst_esd_line_freq,
                        high_pcal_line_freq=self.high_pcal_line_freq,
                        roaming_pcal_line_freq=self.roaming_pcal_line_freq,
                        cres_calibcorr=cres_calibcorr, D_calibcorr=D_calibcorr,
                        tst_calibcorr=tst_calibcorr, Ftst_calibcorr=Ftst_calibcorr,
                        pum_calibcorr=pum_calibcorr, Fpum_calibcorr=Fpum_calibcorr,
                        uim_calibcorr=uim_calibcorr, Fuim_calibcorr=Fuim_calibcorr,
                        pcal_corr_calibcorr=pcal_corr_calibcorr,
                        daqdownsampling_tst_calibcorr=daqdownsampling_tst_calibcorr,
                        daqdownsampling_pum_calibcorr=daqdownsampling_pum_calibcorr,
                        daqdownsampling_uim_calibcorr=daqdownsampling_uim_calibcorr)

    def DCS(self, act_window_type='dpss', invsens_window_type='dpss', make_plot=True,
            output_filename='DCS.npz', plots_directory='../examples/DCS_plots'):
        """ DCS FIR filter generation

        Parameters
        ----------
        act_window_type : str
            'dpss', 'kaiser', 'dolph-chebyshev', or 'hann'
        invsens_window_type : str
            'dpss', 'kaiser', 'dolph-chebyshev', or 'hann'
        make_plot : True or False
            Set this to make diagnostic plots of filters.
        output_filename : str
            Output filename
        plots_directory : str
            Directory to which to save diagnostic plots.

        Returns
        -------
        output_filename.npz, diagnostic plots of filters
        """
        # Compute FIR filter parameters for actuation and inverse sensing
        A_FIRpars = FIRfilter(fNyq=self.FIR.act_fnyq,
                              dur=self.FIR.act_duration,
                              highpass_fcut=self.FIR.act_highpass_fcut,
                              window_type=act_window_type,
                              freq_res=self.FIR.act_freq_res)
        A_freq = A_FIRpars.freq_array
        act_window_type = A_FIRpars.window_type
        act_freq_res = A_FIRpars.freq_res
        A_highpass_FIRpars = FIRfilter(fNyq=self.FIR.act_fnyq,
                                       dur=self.FIR.act_highpass_duration,
                                       highpass_fcut=self.FIR.act_highpass_fcut,
                                       window_type=act_window_type,
                                       freq_res=self.FIR.act_highpass_freq_res)

        Cinv_FIRpars = FIRfilter(fNyq=self.FIR.invsens_fnyq,
                                 dur=self.FIR.invsens_duration,
                                 lowpass_fcut=self.FIR.invsens_lowpass_fcut,
                                 highpass_fcut=self.FIR.invsens_highpass_fcut,
                                 window_type=invsens_window_type,
                                 freq_res=self.FIR.invsens_freq_res)
        Cinv_freq = Cinv_FIRpars.freq_array
        invsens_window_type = Cinv_FIRpars.window_type
        invsens_freq_res = Cinv_FIRpars.freq_res

        Cinv_highpass_FIRpars = FIRfilter(fNyq=self.FIR.invsens_highpass_fnyq,
                                          dur=self.FIR.invsens_highpass_duration,
                                          highpass_fcut=self.FIR.invsens_highpass_fcut,
                                          window_type=invsens_window_type,
                                          freq_res=self.FIR.invsens_highpass_freq_res)

        # Create actuation model
        # Don't try to calculate response at zero frequency
        tst = self.darm.actuation.xarm.compute_actuation_single_stage(A_freq[1:],
                                                                      stage='TST')
        pum = self.darm.actuation.xarm.compute_actuation_single_stage(A_freq[1:],
                                                                      stage='PUM')
        uim = self.darm.actuation.xarm.compute_actuation_single_stage(A_freq[1:],
                                                                      stage='UIM')
        A_model_jump_delay = np.exp(2 * np.pi * 1j * A_freq[1:] / 16384.0)
        tst_fd = tst * A_model_jump_delay
        pum_fd = pum * A_model_jump_delay
        uim_fd = uim * A_model_jump_delay
        # Add in the DC component by hand to avoid RuntimeWarnings
        tst_fd = np.insert(tst_fd, 0, 0)
        pum_fd = np.insert(pum_fd, 0, 0)
        uim_fd = np.insert(uim_fd, 0, 0)
        # Since we downsample the actuation, we'll use the inverse sensing filter to
        # model the entire response above the Nyquist rate of the actuation path.
        # We will therefore smoothly roll off the actuation filter
        # as it approaches the Nyquist rate.
        if not self.FIR.exclude_response_corr:
            full_hann = np.hanning(round(A_FIRpars.fNyquist / A_FIRpars.df / 8))
            half_hann = full_hann[(len(full_hann) // 2 + 1):]
            tst_fd[len(tst_fd) - len(half_hann):] *= half_hann
            pum_fd[len(pum_fd) - len(half_hann):] *= half_hann
            uim_fd[len(uim_fd) - len(half_hann):] *= half_hann

        # In case we are not applying time-dependent corrections for PUM and UIM separately,
        # include a PUM+UIM filter
        pumuim_fd = pum_fd + uim_fd

        A_fNyq = A_highpass_FIRpars.fNyquist
        A_df = A_highpass_FIRpars.df
        # Generate FIR filter from frequency-domain model
        [act_highpass_td, act_highpass_model] = \
            createFIRfilter(A_highpass_FIRpars,
                            np.ones(1 + int(round(A_fNyq/A_df)))) \
            if self.FIR.act_highpass_duration else [[], []]
        [tst_td, tstfilt_model] = createFIRfilter(A_FIRpars, tst_fd)
        tst_fd = correctFIRfilter([A_FIRpars, A_highpass_FIRpars],
                                  [tst_td, act_highpass_td], tst_fd, [5, 10, 100, 150])
        [tst_td, tstfilt_model] = createFIRfilter(A_FIRpars, tst_fd)
        [pum_td, pumfilt_model] = createFIRfilter(A_FIRpars, pum_fd)
        pum_fd = correctFIRfilter([A_FIRpars, A_highpass_FIRpars],
                                  [pum_td, act_highpass_td], pum_fd, [5, 10, 100, 150])
        [pum_td, pumfilt_model] = createFIRfilter(A_FIRpars, pum_fd)
        [uim_td, uimfilt_model] = createFIRfilter(A_FIRpars, uim_fd)
        uim_fd = correctFIRfilter([A_FIRpars, A_highpass_FIRpars],
                                  [uim_td, act_highpass_td], uim_fd, [5, 10, 100, 150])
        [uim_td, uimfilt_model] = createFIRfilter(A_FIRpars, uim_fd)
        [pumuim_td, pumuimfilt_model] = createFIRfilter(A_FIRpars, pumuim_fd)
        pumuim_fd = correctFIRfilter([A_FIRpars, A_highpass_FIRpars],
                                     [pumuim_td, act_highpass_td], pumuim_fd, [5, 10, 100, 150])
        [pumuim_td, pumuimfilt_model] = createFIRfilter(A_FIRpars, pumuim_fd)

        if make_plot is True:
            A_freq_plot = np.zeros((len(A_freq) - 1) * 8 + 1)
            for i in range(8):
                A_freq_plot[:-1][i::8] = \
                    (1 - float(i) / 8) * A_freq[:-1] + float(i) / 8 * A_freq[1:]
            A_freq_plot[-1] = A_freq[-1]
            # Don't try to calculate response at zero frequency
            tstplot = self.darm.actuation.xarm.compute_actuation_single_stage(A_freq_plot[1:],
                                                                              stage='TST')
            pumplot = self.darm.actuation.xarm.compute_actuation_single_stage(A_freq_plot[1:],
                                                                              stage='PUM')
            uimplot = self.darm.actuation.xarm.compute_actuation_single_stage(A_freq_plot[1:],
                                                                              stage='UIM')
            A_model_jump_delay_plot = np.exp(2 * np.pi * 1j * A_freq_plot[1:] / 16384.0)
            TSTforPlot = tstplot * A_model_jump_delay_plot
            PUMforPlot = pumplot * A_model_jump_delay_plot
            UIMforPlot = uimplot * A_model_jump_delay_plot
            PUMUIMforPlot = PUMforPlot + UIMforPlot
            # Add in the DC component by hand to avoid RuntimeWarnings
            TSTforPlot = np.insert(TSTforPlot, 0, 0)
            PUMforPlot = np.insert(PUMforPlot, 0, 0)
            UIMforPlot = np.insert(UIMforPlot, 0, 0)
            PUMUIMforPlot = np.insert(PUMUIMforPlot, 0, 0)
            check_td_vs_fd(tst_td, TSTforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples, highpasstd=act_highpass_td,
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/tst_actuation_fd_comparison.png" % plots_directory,
                           plot_title="TST actuation comparison (%s)" % output_filename)
            check_td_vs_fd(pum_td, PUMforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples, highpasstd=act_highpass_td,
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/pum_actuation_fd_comparison.png" % plots_directory,
                           plot_title="PUM actuation comparison (%s)" % output_filename)
            check_td_vs_fd(uim_td, UIMforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples, highpasstd=act_highpass_td,
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/uim_actuation_fd_comparison.png" % plots_directory,
                           plot_title="UIM actuation comparison (%s)" % output_filename)
            check_td_vs_fd(pumuim_td, PUMUIMforPlot, fNyq=A_FIRpars.fNyquist,
                           delay_samples=A_FIRpars.delay_samples, highpasstd=act_highpass_td,
                           highpass_fNyq=A_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=A_highpass_FIRpars.delay_samples,
                           filename="%s/pumuim_actuation_fd_comparison.png" % plots_directory,
                           plot_title="PUMUIM actuation comparison (%s)" % output_filename)

        # Create inverse sensing model
        # Don't try to calculate response at zero frequency
        R = self.darm.compute_response_function(Cinv_freq[1:])
        C = self.darm.sensing.compute_sensing(Cinv_freq[1:])

        # Add in the DC component by hand to avoid RuntimeWarning.
        # Set it to 1 for now since we'll be dividing by it.
        # It will be zeroed out below.
        C = np.insert(C, 0, 1)
        Cinv = 1 / C
        R = np.insert(R, 0, 1)

        Cinv_model_jump_delay = np.exp(2 * np.pi * 1j * Cinv_freq / 16384.0)

        # Since we downsample the actuation, compensate for the small loss of
        # accuracy by smoothly changing C_corr to 1/R_corr above
        # the actuation path's Nyquist rate
        Cwindow = np.ones(len(C))
        full_hann = np.hanning(round(A_FIRpars.fNyquist / Cinv_FIRpars.df / 8))
        half_hann = full_hann[(len(full_hann) // 2 + 1):]
        indexNy = round(A_FIRpars.fNyquist / Cinv_FIRpars.df)
        Cwindow[indexNy - len(half_hann):indexNy] = half_hann
        Cwindow[indexNy:] = 0
        Rwindow = np.ones(len(C)) - Cwindow
        if not self.FIR.exclude_response_corr:
            Cinv = Cwindow * Cinv + Rwindow * R

        Cinv *= Cinv_model_jump_delay
        # Set DC component to zero
        Cinv[0] = 0

        Cinv_fNyq = Cinv_highpass_FIRpars.fNyquist
        Cinv_df = Cinv_highpass_FIRpars.df
        # Generate FIR filter from frequency-domain model
        [invsens_highpass_td, invsens_highpass_model] = \
            createFIRfilter(Cinv_highpass_FIRpars,
                            np.ones(1 + int(round(Cinv_fNyq/Cinv_df)))) \
            if self.FIR.invsens_highpass_duration else [[], []]

        [invsens_td, invsensfilt_model] = createFIRfilter(Cinv_FIRpars, Cinv)

        # Generate an inverse sensing FIR filter
        # that does not include the coupled cavity pole.
        # Divide out the response of the two-tap filter
        # that would be used to apply the cavity pole.
        Cinv_noccpole = Cinv / two_tap_zero_filter_response([self.fcc], 16384, Cinv_freq)
        [invsens_noccpole_td, model] = createFIRfilter(Cinv_FIRpars, Cinv_noccpole)
        freqA = (self.fs / 2.0) * (1.0 / self.srcQ + np.sqrt(1.0 / self.srcQ / self.srcQ + 4.0))
        freqB = (self.fs / 2.0) * (1.0 / self.srcQ - np.sqrt(1.0 / self.srcQ / self.srcQ + 4.0))
        # Generate an inverse sensing FIR filter that
        # does not include the coupled cavity pole or SRC detuning.
        if np.real(self.fs) != 0 and self.srcQ != 0:
            Cinv_nopole = Cinv / two_tap_zero_filter_response([self.fcc, freqA, freqB],
                                                              16384, Cinv_freq)
            [invsens_nopole_td, model] = createFIRfilter(Cinv_FIRpars, Cinv_nopole)
        else:
            Cinv_nopole = np.copy(Cinv_noccpole)
            invsens_nopole_td = np.copy(invsens_noccpole_td)

        if make_plot is True:
            # Sample the model at 8 times the frequency resolution of the filter,
            # and test the filter at that frequency resolution as well.
            # (computeFIRfilters.check_td_vs_fd does that by default.)
            CinvPlot_freq = np.arange(0, Cinv_fNyq + Cinv_df / 8.0, Cinv_df / 8.0)
            # Don't try to calculate response at zero frequency
            R = self.darm.compute_response_function(CinvPlot_freq[1:])
            C = self.darm.sensing.compute_sensing(CinvPlot_freq[1:])
            Cinv_model_jump_delay_for_plot = np.exp(2 * np.pi * 1j * CinvPlot_freq / 16384.0)
            invsens_fd_for_plot = 1/C * Cinv_model_jump_delay_for_plot[1:]
            # Add in the DC component by hand to avoid RuntimeWarnings
            invsens_fd_for_plot = np.insert(invsens_fd_for_plot, 0, 0)
            if np.isinf(invsens_fd_for_plot[0]):
                invsens_fd_for_plot[0] = invsens_fd_for_plot[1]
            invsens_noccpole_fd_for_plot = \
                invsens_fd_for_plot / two_tap_zero_filter_response([self.fcc], 16384, CinvPlot_freq)
            if np.real(self.fs) != 0 and self.srcQ != 0:
                invsens_nopole_fd_for_plot = \
                    invsens_fd_for_plot / two_tap_zero_filter_response([self.fcc, freqA, freqB],
                                                                       16384, CinvPlot_freq)
            else:
                invsens_nopole_fd_for_plot = np.copy(invsens_noccpole_fd_for_plot)
            check_td_vs_fd(np.copy(invsens_td), invsens_fd_for_plot, fNyq=Cinv_FIRpars.fNyquist,
                           delay_samples=Cinv_FIRpars.delay_samples,
                           highpasstd=np.copy(invsens_highpass_td),
                           highpass_fNyq=Cinv_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=Cinv_highpass_FIRpars.delay_samples,
                           filename="%s/invsens_fd_comparison.png" % plots_directory,
                           plot_title="Inverse sensing comparison (%s)" % output_filename)
            check_td_vs_fd(np.copy(invsens_noccpole_td), invsens_noccpole_fd_for_plot,
                           fNyq=Cinv_FIRpars.fNyquist,
                           delay_samples=Cinv_FIRpars.delay_samples,
                           highpasstd=np.copy(invsens_highpass_td),
                           highpass_fNyq=Cinv_highpass_FIRpars.fNyquist,
                           highpass_delay_samples=Cinv_highpass_FIRpars.delay_samples,
                           filename="%s/invsens_noccpole_fd_comparison.png" % plots_directory,
                           plot_title="1/C No CC Pole comparison (%s)" % output_filename)
            if np.real(self.fs) != 0 and self.srcQ != 0:
                check_td_vs_fd(np.copy(invsens_nopole_td), invsens_nopole_fd_for_plot,
                               fNyq=Cinv_FIRpars.fNyquist,
                               delay_samples=Cinv_FIRpars.delay_samples,
                               highpasstd=np.copy(invsens_highpass_td),
                               highpass_fNyq=Cinv_highpass_FIRpars.fNyquist,
                               highpass_delay_samples=Cinv_highpass_FIRpars.delay_samples,
                               filename="%s/invsens_nopole_fd_comparison.png" % plots_directory,
                               plot_title="1/C No Pole comparison (%s)" % output_filename)

            # Compare filters to the model response function
            R_compare_freqs = np.arange(0, 8192.05, 0.05)
            R = self.darm.compute_response_function(R_compare_freqs[1:])
            D = self.darm.digital.compute_response(R_compare_freqs[1:])
            RforPlot = np.insert(R, 0, abs(R[0]))
            DforRplot = np.insert(D, 0, abs(D[0]))
            check_td_vs_fd_response(invsens_td, invsens_highpass_td, tst_td, pum_td, uim_td,
                                    act_highpass_td, DforRplot, RforPlot,
                                    invsens_fNyq=Cinv_FIRpars.fNyquist,
                                    invsens_highpass_fNyq=Cinv_highpass_FIRpars.fNyquist,
                                    act_fNyq=A_FIRpars.fNyquist,
                                    invsens_delay=Cinv_FIRpars.delay_samples,
                                    invsens_highpass_delay=Cinv_highpass_FIRpars.delay_samples,
                                    act_delay=A_FIRpars.delay_samples,
                                    act_highpass_delay=A_highpass_FIRpars.delay_samples,
                                    time_delay=1.0 / 16384,
                                    filename="%s/td_vs_fd_response.png" % plots_directory,
                                    plot_title=None, legend=['DARM model', 'FIR filters'])
        # Save output to file
        # Inverse sensing high pass output
        invsens_highpass_delay = Cinv_highpass_FIRpars.delay_samples
        invsens_highpass_sr = Cinv_highpass_FIRpars.fNyquist * 2
        inv_sensing_highpass = invsens_highpass_td
        # Actuation high pass output
        actuation_highpass_delay = A_highpass_FIRpars.delay_samples
        actuation_highpass = act_highpass_td
        # TST actuation output
        actuation_tst_delay = A_FIRpars.delay_samples
        actuation_tst_sr = A_FIRpars.fNyquist * 2
        actuation_tst = tst_td
        # PUM actuation output
        actuation_pum_delay = A_FIRpars.delay_samples
        actuation_pum_sr = A_FIRpars.fNyquist * 2
        actuation_pum = pum_td
        # UIM actuation output
        actuation_uim_delay = A_FIRpars.delay_samples
        actuation_uim_sr = A_FIRpars.fNyquist * 2
        actuation_uim = uim_td
        # PUM+UIM actuation output
        actuation_pumuim_delay = A_FIRpars.delay_samples
        actuation_pumuim_sr = A_FIRpars.fNyquist * 2
        actuation_pumuim = pumuim_td
        # Inverse sensing output
        inv_sensing = invsens_td
        inv_sens_delay = Cinv_FIRpars.delay_samples
        inv_sensing_noccpole = invsens_noccpole_td
        inv_sensing_nopole = invsens_nopole_td

        return np.savez(output_filename, arm_length=self.arm_length,
                        fcc=self.fcc, fs=self.fs, fs_squared=self.fs_squared,
                        srcQ=self.srcQ, invsens_model=self.invsens_model,
                        invsensfilt_model=invsensfilt_model,
                        invsens_window_type=invsens_window_type,
                        invsens_freq_res=invsens_freq_res,
                        act_model=self.act_model,
                        act_window_type=act_window_type,
                        act_freq_res=act_freq_res, tst_model=self.tst_model,
                        tstfilt_model=tstfilt_model,
                        uim_model=self.uim_model, uimfilt_model=uimfilt_model,
                        pum_model=self.pum_model, pumfilt_model=pumfilt_model,
                        pumuim_model=self.pumuim_model,
                        pumuimfilt_model=pumuimfilt_model,
                        response_function=self.response_function,
                        inv_sens_delay=inv_sens_delay,
                        actuation_tst_delay=actuation_tst_delay,
                        actuation_pum_delay=actuation_pum_delay,
                        actuation_uim_delay=actuation_uim_delay,
                        actuation_pumuim_delay=actuation_pumuim_delay,
                        actuation_highpass_delay=actuation_highpass_delay,
                        invsens_highpass_delay=invsens_highpass_delay,
                        actuation_tst_sr=actuation_tst_sr,
                        actuation_pum_sr=actuation_pum_sr,
                        actuation_uim_sr=actuation_uim_sr,
                        actuation_pumuim_sr=actuation_pumuim_sr,
                        invsens_highpass_sr=invsens_highpass_sr,
                        actuation_tst=actuation_tst,
                        actuation_pum=actuation_pum,
                        actuation_uim=actuation_uim,
                        actuation_pumuim=actuation_pumuim,
                        inv_sensing=inv_sensing,
                        inv_sensing_noccpole=inv_sensing_noccpole,
                        inv_sensing_nopole=inv_sensing_nopole,
                        actuation_highpass=actuation_highpass,
                        inv_sensing_highpass=inv_sensing_highpass,
                        src_pcal_line_freq=self.src_pcal_line_freq,
                        ka_pcal_line_freq=self.ka_pcal_line_freq,
                        ka_esd_line_freq=self.ka_esd_line_freq,
                        pum_act_line_freq=self.pum_act_line_freq,
                        uim_act_line_freq=self.uim_act_line_freq,
                        kc_pcal_line_freq=self.kc_pcal_line_freq,
                        ktst_esd_line_freq=self.ktst_esd_line_freq,
                        high_pcal_line_freq=self.high_pcal_line_freq,
                        roaming_pcal_line_freq=self.roaming_pcal_line_freq)
# %%
