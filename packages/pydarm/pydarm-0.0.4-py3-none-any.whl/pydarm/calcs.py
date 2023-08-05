# Copyright (C) Evan Goetz (2022)
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

import numpy as np
from scipy import signal
from .utils import load_foton_export_tf, digital_delay_filter
from .digital import daqdownsamplingfilters
from .model import Model
from .darm import DARMModel


class CALCSModel(DARMModel):

    def __init__(self, config, calcs=None):
        """
        Initialize a CALCSModel object

        Note that any string or path to file string in `calcs` will
        overwrite anything in the `config` parameter string or path to file
        """
        super().__init__(config)
        if 'calcs' in self._config:
            self.calcs = Model(config, measurement='calcs')
        if calcs is not None:
            self.calcs = Model(calcs, measurement='calcs')
        if not hasattr(self, 'calcs'):
            raise ValueError('No CALCS parameters have been defined')

    def optical_response_ratio(self, frequencies):
        """
        This computes (opt resp) / (opt resp)_foton

        It is a bit confusing because the FOTON filter is the inverse
        sensing function, so we'll be multiplying the true optical
        response from the model by the FOTON transfer function.

        In T1900169, in the definition of C/C_CALCS, the last three
        terms are
          (opt resp)/(opt resp)_foton * (LP_foton/LP) * LP
        and this method returns this combination since the export from
        FOTON gives the full combination of
          LP_foton / (opt resp)_foton

        Note that (LP_foton/LP) is the "IIR warping"

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies for the optical response ratio

        Returns
        -------
        foton_inv_sensing_interp : `complex128`, array-like
            ratio of interpolated values
        """

        # We need the coupled cavity LTI object
        coupled_cavity = self.sensing.optical_response(
            self.sensing.coupled_cavity_pole_frequency,
            self.sensing.detuned_spring_frequency,
            self.sensing.detuned_spring_q,
            pro_spring=self.sensing.is_pro_spring)

        # load inverse sensing data from foton file export (1/SRC_D2N)
        foton_freq, foton_tf = load_foton_export_tf(
            self.dpath(self.calcs.foton_invsensing_tf))

        # Take ratio of true optical response / foton response where
        # "foton response" is already the approximated
        # LP_foton / (opt resp)_foton, so we just need to multiply the two
        # terms
        opt_response_ratio = (
            signal.freqresp(coupled_cavity, 2.0*np.pi*foton_freq)[1] *
            foton_tf)

        # interpolate to the requested frequencies
        opt_response_ratio_interp = np.interp(frequencies,
                                              foton_freq,
                                              opt_response_ratio)

        return opt_response_ratio_interp

    def sus_response_ratio(self, frequencies, arm, stage):
        """
        This computes (sus resp) / (sus resp)_foton

        See T1900169 definition of delta A_mn

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies for the optical response ratio
        arm : str, `x` or `y`
        stage : str `UIM`, `PUM`, or `TST`

        Returns
        -------
        response_ratio : `complex128`, array-like
            ratio of interpolated values
        """

        # load FOTON suspension dynamics filter
        foton_freq, foton_tf = load_foton_export_tf(
            self.dpath(getattr(self.calcs,
                               f'{arm.lower()}arm_{stage.lower()}_analog')))

        if arm.lower() == 'x':
            arm_act = self.actuation.xarm
        elif arm.lower() == 'y':
            arm_act = self.actuation.yarm
        else:
            raise ValueError('The accepted values for arm is x or y')

        # get true suspension dynamics
        [uim, pum, tst] = arm_act.matlab_force2length_response(
            arm_act.suspension_file, foton_freq)

        if stage.lower() == 'uim':
            ratio = uim / foton_tf
        elif stage.lower() == 'pum':
            ratio = pum / foton_tf
        elif stage.lower() == 'tst':
            ratio = tst / foton_tf
        else:
            raise ValueError('stage must be uim, pum or tst')

        # interpolate to the requested frequencies
        response_ratio = np.interp(frequencies, foton_freq, ratio)

        return response_ratio

    def C_corr(self, frequencies):
        """
        Compute delta C = delay*(opt resp)/(opt resp)_foton*C_r

        The inverse of this transfer function is multiplied by
        DELTAL_RESIDUAL as the GDS correction.

        We need to divide out the normalized optical response FOTON filter
        only and be sure to include 1 16k clock cycle delay from the model
        jump OMC to CAL-CS. There is an optical
        gain factor in the front end model, but it is fine to leave this in
        place. The output is basically C_pydarm / C_foton, and GDS will need to
        either divide the DELTAL_RESIDUAL data by this function or invert the output
        of this function and multiply by the DELTAL_RESIDUAL data.

        This is delay*(opt resp)/(opt resp)_foton*C_r (see T1900169-v5 eq 33)

        This is also known as C_corr or delta C in T1900169

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies to compute the GDS sensing correction

        Returns
        -------
        tf : `complex128`, array-like
            transfer function response of the correction
        """

        # Residual sensing function transfer function
        # This is everything in sensing except the optical gain and response
        C_res = self.sensing.sensing_residual(frequencies)

        # we will need to apply a delay because when it is inverted in GDS
        # this will become an advance (the correct thing to do)
        omc_to_calcs_response = (
            signal.dfreqresp(digital_delay_filter(1, 2**14),
                             2.0*np.pi*frequencies/2**14)[1])

        # get the optical response ratio between FOTON and pyDARM
        opt_response_ratio = self.optical_response_ratio(frequencies)

        # the final correction is the sensing model divided by the interpolated
        # foton filter
        correction = (omc_to_calcs_response *
                      opt_response_ratio *
                      C_res)

        return correction

    def drivealign_out_to_longitudinal_displacement(
            self, frequencies, arm, stage):
        """
        CALCS representation of the transfer function from the
        DRIVEALIGN bank to longitudinal displacement of the test
        mass.
        Units are m/ct = (N/ct) * (m/N)


        The gain (N/ct) of the CALCS model is assumed to be exactly the same
        as what is in the reference model, so that is used.

        If there is anything in the "coiloutf" key-value pair, then this
        transfer function is also used, but this would be used only in
        special circumstances.

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies for the CALCS approximated longitudinal
            actuation of the test mass from the given stage
        arm : `str`
            arm for the calculation, 'x' or 'y'
        stage : `str`
            SUS stage for the calculation, 'UIM', 'PUM', or 'TST'

        Returns
        -------
        out_tf : `complex128`, array-like
            CALCS approximation of the DRIVEALIGN output to displacement
        """

        # The pieces of the actuator are multiplicative to obtain the final
        # result so we need to start with unity transfer functions and
        # change them only if a user has supplied a FOTON transfer
        # function export. The tf_ana_interp will be filled in by the FOTON
        # export of the SUS response. The tf_dig_interp will only be used if
        # there is CALCS COILOUTF content.
        tf_dig_interp = np.ones(len(frequencies), dtype='complex128')
        tf_ana_interp = np.ones(len(frequencies), dtype='complex128')

        # Get the coiloutf and analog exports if they exist
        if hasattr(self.calcs, f'{arm.lower()}arm_{stage.lower()}_coiloutf'):
            val = getattr(
                self.calcs, f'{arm.lower()}arm_{stage.lower()}_coiloutf')
            if val != '':
                [f, tf_dig] = load_foton_export_tf(self.dpath(val))
                tf_dig_interp = np.interp(frequencies, f, tf_dig)
        if hasattr(self.calcs, f'{arm.lower()}arm_{stage.lower()}_analog'):
            val = getattr(
                self.calcs, f'{arm.lower()}arm_{stage.lower()}_analog')
            if val != '':
                [f, tf_ana] = load_foton_export_tf(self.dpath(val))
                tf_ana_interp = np.interp(frequencies, f, tf_ana)

        # Get the CALCS actuation output matrix (different then the DARM output
        # matrix)
        # TODO: this is -1 for X and I think +1 for Y; why is this?
        if hasattr(self.calcs, f'{arm.lower()}arm_output_matrix'):
            idx = ['top', 'uim', 'pum', 'tst'].index(stage.lower())
            out_mtrx = getattr(self.calcs,
                               f'{arm.lower()}arm_output_matrix')[idx]
        else:
            out_mtrx = 0

        # put in the gain and the DARM feedback sign
        # FOTON export is in m/N, here we apply the N/ct from the model
        # assuming that this has been replicated perfectly in CALCS.
        # Note the DARM feedback sign is applied here as well, from the
        # model.
        if (getattr(self.actuation, f'{arm.lower()}arm') is not None and
                stage.lower() in ['uim', 'pum', 'tst']):
            if ((stage.lower() in ['uim', 'pum'] and
                    hasattr(getattr(self.actuation, f'{arm.lower()}arm'),
                            f'{stage.lower()}_npa') and
                    getattr(getattr(self.actuation, f'{arm.lower()}arm'),
                            f'{stage.lower()}_npa') != '') or
                    (stage.lower() == 'tst' and
                        hasattr(getattr(self.actuation, f'{arm.lower()}arm'),
                                f'{stage.lower()}_npv2') and
                        getattr(getattr(self.actuation, f'{arm.lower()}arm'),
                                f'{stage.lower()}_npv2') != '')):
                act_arm_model = getattr(self.actuation, f'{arm.lower()}arm')
                # tf_ana_interp *= act_arm_model.darm_feedback_sign
                if stage.lower() == 'uim':
                    tf_ana_interp *= act_arm_model.uim_dc_gain_Npct()
                elif stage.lower() == 'pum':
                    tf_ana_interp *= act_arm_model.pum_dc_gain_Npct()
                else:
                    tf_ana_interp *= act_arm_model.tst_dc_gain_Npct()

        out_tf = (out_mtrx *
                  tf_dig_interp *
                  tf_ana_interp)

        return out_tf

    def drivealign_out_to_darm_displacement(self, frequencies, arm, stage):
        """
        CALCS representation of the SUS_EXC DRIVEALIGN point to DARM
        displacement transfer function.

        Units are m/ct = (N/ct) * (m/N)


        The gain (N/ct) of the CALCS model is assumed to be exactly the same
        as what is in the reference model, so that is used.

        If there is anything in the "coiloutf" key-value pair, then this
        transfer function is also used, but this would be used only in
        special circumstances.

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies
        arm : `str`
            arm for the calculation, 'x' or 'y'
        stage : `str`
            SUS stage for the calculation, 'UIM', 'PUM', or 'TST'

        Returns
        -------
        tf : `complex128`, array-like
            CALCS approximation of the DRIVEALIGN output to DARM displacement
        """

        if (getattr(self.actuation, f'{arm.lower()}arm') is None):
            raise ValueError('Must provide a valide arm object')

        act_arm_model = getattr(self.actuation, f'{arm.lower()}arm')

        tf = (act_arm_model.darm_feedback_sign *
              self.drivealign_out_to_longitudinal_displacement(
                  frequencies, arm, stage))

        return tf

    def compute_actuation_single_stage(self, frequencies, arm, stage):
        """
        A_n,calcs

        CALCS approximation of a specific arm, stage from DARM_CTRL
        input to SUS ISCINF to DARM (and therefore does not include
        the OMC to CALCS delay)
        displacement. See T1900169


        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies for the CALCS approximated DARM actuation
        arm : `str`
            arm for the calculation, 'x' or 'y'
        stage : `str`
            SUS stage for the calculation, 'UIM', 'PUM', or 'TST'

        Returns
        -------
        calcs_stage_actuation : `complex128`, array-like
            CALCS approximation of SUS model ISCINF input to DARM displacement
            transfer function
        """

        # Assume the same as in-loop DARM output matrix
        # only used as determining if this is non-zero
        output_matrix = self.actuation.darm_output_matrix_values()

        # initialize zeros for the output
        calcs_stage_actuation = np.zeros(len(frequencies), dtype='complex128')

        arm_idx = ['x', 'y'].index(arm.lower())
        stage_idx = ['top', 'uim', 'pum', 'tst'].index(stage.lower())
        if (output_matrix[arm_idx, stage_idx] != 0.0):
            assert stage_idx > 0, 'top has not been implemented'

            # Model SUS filters
            arm_obj = getattr(self.actuation, f'{arm}arm')
            dig_filt = arm_obj.sus_digital_filters_response(frequencies)

            # This is the CALCS DARM displacement for this arm and stage
            drivealign_out_to_disp = self.drivealign_out_to_darm_displacement(
                frequencies, arm=arm, stage=stage)

            calcs_stage_actuation = (dig_filt[stage_idx - 1] *
                                     drivealign_out_to_disp)

        return calcs_stage_actuation

    def gds_actuation_correction(self, frequencies, stage, daqdownsample=True):
        """
        Compute the correction to the CAL-CS output for GDS. Note that this
        implicitly assumes that the front end digital filters in CALCS is the
        same as that in the SUS path!

        This is also more complicated than sensing because there is a single
        channel for a given stage that accounts for BOTH arms; e.g.,
        ${IFO}:CAL-DELTAL_CTRL_${STAGE}_DBL_DQ takes input from both x and y
        arms using an output matrix.

        This is (A_{xn}+A_{yn})/(A_{xn,calcs}+A_{yn,calcs})/(F*delay)
        where n is the stage, calcs denotes FOTON implementation of an actuator
        F is the DAQ downsampling filter (on by default), and delay of the 1
        16384 clock cycle delay going from OMC to CALCS

        See T1900169, definition of delta A_n

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies to compute the GDS sensing correction
        stage : `str`
            SUS stage for the calculation, 'UIM', 'PUM', or 'TST'
        daqdownsample : `bool`, optional
            When True (default), the 16k-4k daqdownsample is applied in
            GDS actuation correction

        Returns
        -------
        correction : `complex128`, array-like
            transfer function response of the correction
        """

        # Assume the same as in-loop DARM output matrix
        output_matrix = self.actuation.darm_output_matrix_values()

        # 1 clock cycle delay transfer function for OMC to SUS and
        # OMC to CALCS
        omc_to_sus_response = (
            signal.dfreqresp(digital_delay_filter(1, 16384),
                             2.0*np.pi*frequencies/16384)[1])
        omc_to_calcs_response = (
            signal.dfreqresp(digital_delay_filter(1, 16384),
                             2.0*np.pi*frequencies/16384)[1])

        A_n = 0
        A_n_calcs = 0
        stage_idx = ['top', 'uim', 'pum', 'tst'].index(stage.lower())
        for arm_idx, arm in enumerate(['x', 'y']):
            if (output_matrix[arm_idx, stage_idx] != 0.0):
                assert stage_idx > 0, 'top has not been implemented'

                arm_obj = getattr(self.actuation, f'{arm}arm')

                # ideal model sum of actuators for A_{xn} and A_{yn}
                A_n += (
                    output_matrix[arm_idx, stage_idx] *
                    arm_obj.compute_actuation_single_stage(
                        frequencies, stage=stage))

                # CALCS approximate for A_{xn,calcs} and A_{yn,calcs}
                A_n_calcs += (
                    output_matrix[arm_idx, stage_idx] *
                    self.compute_actuation_single_stage(
                        frequencies, arm=arm, stage=stage))

        if daqdownsample:
            # DAQ downsampling filters are applied so we need to account
            # for this
            daqdownsampling = signal.dfreqresp(
                daqdownsamplingfilters(16384, 4096, 'biquad', 'v3'),
                2.0*np.pi*frequencies/16384)[1]
        else:
            daqdownsampling = 1

        # This is \delta A_n
        correction = ((omc_to_sus_response * A_n / A_n_calcs) *
                      (1 / (daqdownsampling * omc_to_calcs_response)))

        return correction

    def calcs_darm_actuation(self, frequencies):
        """
        Compute the CALCS approximated DARM actuation. This method implicitly
        assumes that the CALCS DARM output matrix and actuation digital
        filtering matches the installed in-loop DARM ouput matrix and actuation
        digital filtering.

        See T1900169, definition of A_CALCS

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies for the CALCS approximated DARM actuation

        Returns
        -------
        calcs_actuation : `complex128`, array-like
            Residual phase after removing the simulated delay
        """

        # Assume the same as in-loop DARM output matrix
        # we won't actually multiply these values it's just to help
        # loop through stages that are used
        output_matrix = self.actuation.darm_output_matrix_values()

        # Start with zeros
        calcs_actuation = np.zeros(len(frequencies), dtype='complex128')

        # Loop over arms and stages to compute the digital filters and scale/sum
        # everything together
        # output matrix * digital filters * calcs digital out to displacement
        for arm_idx, arm in enumerate(['x', 'y']):
            for stage_idx, stage in enumerate(['top', 'uim', 'pum', 'tst']):
                if output_matrix[arm_idx, stage_idx] != 0.0:
                    assert stage_idx > 0, 'top has not been implemented'
                    # dig_filt only has UIM, PUM, and TST
                    # calcs_dig_out_to_disp has same order as output_matrix
                    calcs_actuation += (
                        self.compute_actuation_single_stage(
                            frequencies, arm=arm, stage=stage))

        return calcs_actuation

    def gds_sensing_correction(self, frequencies):
        """
        Compute 1 / C_corr = C_foton / C see T1900169.

        For the sensing path, GDS sensing correction = 1 / C_corr. This is
        to be multiplied into DELTAL_RESIDUAL

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies to compute the GDS sensing correction

        Returns
        -------
        tf : `complex128`, array-like
            transfer function response of the correction
        """

        return 1 / self.C_corr(frequencies)

    def A_corr(self, frequencies, daqdownsample=True):
        """
        Compute total DARM actuator A_corr = A / A_foton (aka delta A),
        see T1900169.

        This is more complicated than computing C_corr, since the GDS actuation
        correction is applied to each stage separately, so we cannot just sum
        the corrections and multiply by a common factor. Instead, we compute
        the modeled (true) DARM actuation, and divide by the CALCS
        (approximate) DARM actuation. We also account for the OMC to CALCS
        delay and the possibility for DAQ downsampling.

        DAQ downsample is an option here because if you want to create
        delta L_ctrl from ${IFO}:CAL-DELTAL_CTRL_DBL_DQ, then we need to
        use daqdownsampling = True because the channel that is read has
        been downsampled. When computing the delay between CAL-DELTAL_CTRL
        and CAL-DELTAL_RESIDUAL to improve CAL-DELTAL_EXTERNAL, however, one
        does not need daqdownsampling (see discussion in sec III of
        T1900169).

        Both products are using the CALCS copy of DARM_CTRL and therefore need
        the delay (OMC to CALCS)

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies to compute the GDS sensing correction
        daqdownsample : `bool`, optional
            When True (default), the 16k-4k daqdownsample is applied in A_corr

        Returns
        -------
        A_corr : `complex128`, array-like
            transfer function response of the correction
        """

        if daqdownsample:
            # DAQ downsampling filters are applied so we need to account
            # for this
            daqdownsampling = signal.dfreqresp(
                daqdownsamplingfilters(16384, 4096, 'biquad', 'v3'),
                2.0*np.pi*frequencies/16384)[1]
        else:
            daqdownsampling = 1

        # we will need to apply a delay because when it is inverted in GDS
        # this will become an advance (the correct thing to do)
        omc_to_calcs_response = (
            signal.dfreqresp(digital_delay_filter(1, 16384),
                             2.0*np.pi*frequencies/16384)[1])

        A = self.actuation.compute_actuation(frequencies)
        A_calcs = self.calcs_darm_actuation(frequencies)

        A_corr = ((A / A_calcs) *
                  (1 / (daqdownsampling * omc_to_calcs_response)))

        return A_corr

    def sensing_actuation_delay(self, frequencies, clock=False):
        """
        Compute the delay based on the GDS sensing and actuation correction in
        units of seconds delay or (if clock=True) in units of 16384
        samples/sec, i.e., 1 16384 Hz clock delay = 6.1035e-5 s. Positive
        indicates a delay, negative indicates an advance

        See T1900169, sec III "method 1"

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies to model the phase delay
        clock : `boolean`, optional
            if clock is True, then the output delay_fit and residual will
            be computed and rounded to the nearest number of integer clock
            cycles (16384)

        Returns
        -------
        delay : float
            Units of seconds or 16384 Hz clock cycles (if clock=True)
        """

        # We use the C_corr = \delta C and A_corr = \delta A values from
        # T1900169, but note that we TURN OFF the DAQ downsample here
        # because the path that is summed in CALCS does not have the DAQ
        # downsampling
        C_corr = self.C_corr(frequencies)
        A_corr = self.A_corr(frequencies, daqdownsample=False)

        delay = -np.angle(C_corr*A_corr) / (2.0*np.pi*frequencies)

        if clock is True:
            delay = delay * 16384

        return delay

    def deltal_ext_whitening(self, frequencies):
        """
        Compute the interpolated transfer function of the DELTAL_EXTERNAL
        export from FOTON

        If no export file is provided in the configuration, this method
        will return an array of ones

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies to compute the interpolation

        Returns
        -------
        whitening_interp : `complex128`, array-like
            transfer function response of the calibration
        """

        if (hasattr(self.calcs, 'foton_deltal_whitening_tf') and
                getattr(self.calcs, 'foton_deltal_whitening_tf') != ''):
            foton_freq, foton_tf = load_foton_export_tf(
                self.dpath(self.calcs.foton_deltal_whitening_tf))
            whitening_interp = np.interp(frequencies,
                                         foton_freq,
                                         foton_tf)
        else:
            whitening_interp = np.ones(len(frequencies), dtype='complex128')

        return whitening_interp

    def calcs_dtt_calibration(self, frequencies, include_whitening=True,
                              strain_calib=False, save_to_file=None, fmt=None):
        """
        Compute the calibration transfer function, dL_pyDARM / dL_CALCS
        for the main control room calibrated sensitivity curve. One can save
        this data to a file with the needed frequency, dB magnitude, and
        degrees phase columns, and apply it to a DTT template.

        See T1900169 section IV

        Parameters
        ----------
        frequencies : `float`, array-like
            array of frequencies to compute the CAL_DELTAL_EXTERNAL DTT
            calibration
        include_whitening : `bool`, optional
            if the whitening filter is on (default), then we'd like to remove
            its effect so by default this divides out the whitening filter
        strain_calib : `bool`, optional
            the output defaults to dL_pyDARM/dL_CALCS, so that we can recalibrate
            CAL-DELTAL_EXTERNAL. If this option is True, then the output is
            h_pyDARM/dL_CALCS
        save_to_file : `str`, optional
            Filename (ASCII) to save the data from this result. Note:
            the default file columns are
            <frequency> <magnitude (dB)> <phase (deg)>
        fmt : `str`, optional
            if save_to_file is used, then this is the output format. Options
            are 'dB,deg' (default), 'mag,deg', 'dB,rad', 'mag,rad', or 're,im'.
            If none is given, then the default is used

        Returns
        -------
        tf : `complex128`, array-like
            transfer function response of the calibration
        """

        # This is C_r*delay*(opt resp)/(opt resp)_foton
        C_corr = self.C_corr(frequencies)

        # Remember that A_corr should not have a DAQ downsample since
        # the path that is summed does not have the DAQ downsample in it
        A_corr = self.A_corr(frequencies, daqdownsample=False)

        # Whitening filter
        whitening_interp = self.deltal_ext_whitening(frequencies)

        if not include_whitening:
            whitening_interp = 1

        # Foton delay filter
        foton_freq, foton_tf = load_foton_export_tf(
            self.dpath(self.calcs.foton_delay_filter_tf))
        delay_interp = np.interp(frequencies, foton_freq, foton_tf)

        # Model loop gain CDA
        G = self.compute_darm_olg(frequencies)

        calib = ((1 / whitening_interp) *
                 (1 / C_corr) *
                 ((1.0 + G) /
                  (1.0 + G*delay_interp/(C_corr*A_corr))))

        if strain_calib:
            calib /= np.mean(np.array([self.sensing.x_arm_length,
                                       self.sensing.y_arm_length]))

        # Save to file and use the fmt options if given
        # default is to save as dB magnitude and degrees phase
        if save_to_file is not None:
            col1 = frequencies
            col2 = 20.0*np.log10(np.abs(calib))
            col3 = np.angle(calib, deg=True)

            if fmt is not None:
                fmt_opt = fmt.split(',')
                if len(fmt_opt) != 2:
                    raise ValueError('Wrong formatting for fmt')
                if fmt_opt[0] == 'mag':
                    col2 = np.abs(calib)
                elif fmt_opt[0] == 're':
                    col2 = np.real(calib)
                if fmt_opt[1] == 'rad':
                    col3 = np.angle(calib, deg=False)
                elif fmt_opt[1] == 'im':
                    col3 = np.imag(calib)

            np.savetxt(save_to_file,
                       np.array([col1,
                                 col2,
                                 col3]).T,
                       fmt='%.7g')

        return calib
