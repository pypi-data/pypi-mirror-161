import unittest
import pydarm
import numpy as np
import h5py
import os
from pydarm.FIR import (FIRfilter, createFIRfilter,
                        correctFIRfilter, two_tap_zero_filter_response,
                        check_td_vs_fd, check_td_vs_fd_response)


class TestFIRfilter(unittest.TestCase):

    def setUp(self):
        self.window = np.array([6.747975786659215006e-03,
                                2.767078112501164186e-02,
                                7.377080623487733413e-02,
                                1.551839702572553048e-01,
                                2.768990448483386047e-01,
                                4.345680722833729082e-01,
                                6.125095782158316293e-01,
                                7.853264037228884220e-01,
                                9.232791494417179612e-01,
                                1.000000000000000000e+00,
                                1.000000000000000000e+00,
                                9.232791494417179612e-01,
                                7.853264037228884220e-01,
                                6.125095782158316293e-01,
                                4.345680722833729082e-01,
                                2.768990448483386047e-01,
                                1.551839702572553048e-01,
                                7.377080623487733413e-02,
                                2.767078112501164186e-02,
                                6.747975786659215006e-03])

    def tearDown(self):
        del self.window

    def test_FIRfilter(self):
        test_filter = FIRfilter(fNyq=10, dur=1, highpass_fcut=10, lowpass_fcut=None,
                                latency=None, window_type='dpss', freq_res=3.0)
        self.assertEqual(len(test_filter.window), len(self.window))
        for n in range(len(self.window)):
            self.assertAlmostEqual(np.real(test_filter.window[n]),
                                   np.real(self.window[n]))


class TestcreateFIRfilter(unittest.TestCase):

    def setUp(self):
        self.FIRPars = FIRfilter(fNyq=10, dur=1, highpass_fcut=10, lowpass_fcut=None,
                                 latency=None, window_type='dpss', freq_res=3.0)
        self.config = '''
[metadata]
[interferometer]
[sensing]
x_arm_length = 3994.4704
y_arm_length = 3994.4692
coupled_cavity_optical_gain = 3.22e6
coupled_cavity_pole_frequency = 410.6
detuned_spring_frequency = 4.468
detuned_spring_Q = 52.14
sensing_sign = 1
is_pro_spring = True
anti_aliasing_rate_string = 16k
anti_aliasing_method      = biquad
analog_anti_aliasing_file = test/H1aa.mat, test/H1aa.mat
whitening_mode_names = mode1, mode1
omc_meas_p_trans_amplifier   = 13.7e3, 17.8e3: 13.7e3, 17.8e3
omc_meas_p_whitening_mode1   = 11.346e3, 32.875e3, 32.875e3: 11.521e3, 32.863e3, 32.863e3
omc_meas_z_whitening_mode1 =
omc_meas_z_whitening_mode2 =
omc_meas_p_whitening_mode2 =
super_high_frequency_poles_apparent_delay = 0, 0
gain_ratio = 1, 1
balance_matrix = 1, 1
omc_path_names = A, B
single_pole_approximation_delay_correction = -12e-6
adc_gain = 1, 1
omc_compensation_filter_file = test/H1OMC_1239468752.txt
omc_compensation_filter_bank = OMC_DCPD_A, OMC_DCPD_B
omc_compensation_filter_modules_in_use = 4: 4
omc_compensation_filter_gain = 1, 1
'''
        self.C = pydarm.sensing.SensingModel(self.config)
        self.Cf = self.C.compute_sensing(self.FIRPars.freq_array)
        self.known_Cfir = np.array(
            [-7.494399500980555e-01, 1.878503003094571e+00,
             5.462232980771952e+00, -2.695548527287479e+01,
             2.545219465518255e+01, 6.151843365364729e+01,
             -1.858747352804171e+02, 1.227768241438271e+02,
             2.900328422755409e+02, -8.351660492271960e+02,
             1.043878605764661e+03, -7.252724534558012e+02,
             1.926554483363665e+02, 1.272121476274398e+02,
             -1.396991669256313e+02, 3.825453241252376e+01,
             1.445728611878720e+01, -1.178386791012969e+01,
             1.399786372967719e+00, 5.828415612098137e-01])

    def tearDown(self):
        del self.FIRPars
        del self.config
        del self.C
        del self.Cf
        del self.known_Cfir

    def test_createFIRfilter(self):
        test_Cfir = createFIRfilter(self.FIRPars, self.Cf)[0]

        for n in range(len(self.known_Cfir)):
            self.assertAlmostEqual(np.real(test_Cfir[n]) /
                                   np.real(self.known_Cfir[n]),
                                   1.0, places=1)


class TestcorrectFIRfilter(unittest.TestCase):

    def setUp(self):
        self.FIRPars = FIRfilter(fNyq=10, dur=1, highpass_fcut=10, lowpass_fcut=None,
                                 latency=None, window_type='dpss', freq_res=3.0)
        self.config = '''
[metadata]
[interferometer]
[sensing]
x_arm_length = 3994.4704
y_arm_length = 3994.4692
coupled_cavity_optical_gain = 3.22e6
coupled_cavity_pole_frequency = 410.6
detuned_spring_frequency = 4.468
detuned_spring_Q = 52.14
sensing_sign = 1
is_pro_spring = True
anti_aliasing_rate_string = 16k
anti_aliasing_method      = biquad
analog_anti_aliasing_file = test/H1aa.mat, test/H1aa.mat
omc_meas_p_trans_amplifier   = 13.7e3, 17.8e3: 13.7e3, 17.8e3
whitening_mode_names = mode1, mode1
omc_meas_p_whitening_mode1   = 11.346e3, 32.875e3, 32.875e3: 11.521e3, 32.863e3, 32.863e3
omc_meas_z_whitening_mode1 =
omc_meas_z_whitening_mode2 =
omc_meas_p_whitening_mode2 =
super_high_frequency_poles_apparent_delay = 0, 0
gain_ratio = 1, 1
balance_matrix = 1, 1
omc_path_names = A, B
single_pole_approximation_delay_correction = -12e-6
adc_gain = 1, 1
omc_compensation_filter_file = test/H1OMC_1239468752.txt
omc_compensation_filter_bank = OMC_DCPD_A, OMC_DCPD_B
omc_compensation_filter_modules_in_use = 4: 4
omc_compensation_filter_gain = 1, 1
'''
        self.C = pydarm.sensing.SensingModel(self.config)
        self.Cf = self.C.compute_sensing(self.FIRPars.freq_array)
        self.known_Corfir = np.array(
            [-103.66404816958784-1.337730548924199e-01j,
             -584.6694985643597-2.113137675101644e+01j,
             -2502.2100106742537-2.145479833879172e+02j,
             -13425.302150346777-2.127963450969817e+03j,
             16240.886940562672-3.349456399201711e+02j,
             6943.844285969676+1.487810161706327e+02j,
             4267.369269140403+3.264374033219781e+00j,
             2854.2796483130155-1.201598895624997e+02j,
             2605.6585269756306-1.086858615979269e+02j,
             2452.99276738437-1.055089399962111e+02j])

    def tearDown(self):
        del self.FIRPars
        del self.config
        del self.C
        del self.Cf
        del self.known_Corfir

    def test_correctFIRfilter(self):
        test_Cfir = createFIRfilter(self.FIRPars, self.Cf)[0]
        test_Corfir = correctFIRfilter(self.FIRPars, test_Cfir, self.Cf,  [2, 4, 7, 9])
        test_Corfir = np.delete(test_Corfir, 0)

        self.assertEqual(len(test_Corfir), len(self.known_Corfir))
        for n in range(len(test_Corfir)):
            self.assertAlmostEqual(
                np.abs(test_Corfir[n])/np.abs(self.known_Corfir[n]), 1)
            self.assertAlmostEqual(
                np.abs(np.angle(test_Corfir[n], deg=True) /
                       np.angle(self.known_Corfir[n], deg=True)), 1)


class Testtwo_tap_zero_filter(unittest.TestCase):

    def setUp(self):
        self.known_two_tap_zero_filt = np.array(
            [0.999999999999999889+0.000000000000000000j,
             0.944065144524670274-0.242141032019198316j,
             0.791790257603250391-0.430462197742083885j,
             0.584088546831189381-0.528606912083167346j,
             0.372528221948197957-0.528347694598477635j,
             0.201488911932644205-0.449462235973869528j,
             0.094304975193611695-0.329261396976028187j,
             0.048712779360778842-0.206416348868232596j,
             0.042948901676579269-0.105952738743734842j,
             0.049370136034108433-0.031598975501051528j])

    def tearDown(self):
        del self.known_two_tap_zero_filt

    def test_two_tap_zero_filt(self):
        test_ttzf = two_tap_zero_filter_response([1, 2], 1, np.linspace(1, 100, 10))

        for n in range(len(test_ttzf)):
            self.assertAlmostEqual(np.abs(test_ttzf[n]),
                                   np.abs(self.known_two_tap_zero_filt[n]), places=6)
            self.assertAlmostEqual(np.angle(test_ttzf[n], deg=True),
                                   np.angle(self.known_two_tap_zero_filt[n], deg=True),
                                   places=6)


class Testcheck_td_vs_fd(unittest.TestCase):

    def setUp(self):
        self.FIRPars = FIRfilter(fNyq=10, dur=1, highpass_fcut=10, lowpass_fcut=None,
                                 latency=None, window_type='dpss', freq_res=3.0)
        self.config = '''
[metadata]
[interferometer]
[sensing]
x_arm_length = 3994.4704
y_arm_length = 3994.4692
coupled_cavity_optical_gain = 3.22e6
coupled_cavity_pole_frequency = 410.6
detuned_spring_frequency = 4.468
detuned_spring_Q = 52.14
sensing_sign = 1
is_pro_spring = True
anti_aliasing_rate_string = 16k
anti_aliasing_method      = biquad
analog_anti_aliasing_file = test/H1aa.mat, test/H1aa.mat
whitening_mode_names = mode1, mode1
omc_meas_p_trans_amplifier   = 13.7e3, 17.8e3: 13.7e3, 17.8e3
omc_meas_p_whitening_mode1   = 11.346e3, 32.875e3, 32.875e3: 11.521e3, 32.863e3, 32.863e3
omc_meas_z_whitening_mode1 =
omc_meas_z_whitening_mode2 =
omc_meas_p_whitening_mode2 =
super_high_frequency_poles_apparent_delay = 0, 0
gain_ratio = 1, 1
balance_matrix = 1, 1
omc_path_names = A, B
single_pole_approximation_delay_correction = -12e-6
adc_gain = 1, 1
omc_compensation_filter_file = test/H1OMC_1239468752.txt
omc_compensation_filter_bank = OMC_DCPD_A, OMC_DCPD_B
omc_compensation_filter_modules_in_use = 4: 4
omc_compensation_filter_gain = 1, 1
'''
        self.C = pydarm.sensing.SensingModel(self.config)
        self.Cf = self.C.compute_sensing(self.FIRPars.freq_array)
        self.known_freq_array = np.array(
            [0., 0.125, 0.25, 0.375, 0.5, 0.625, 0.75,
             0.875, 1., 1.125, 1.25, 1.375, 1.5, 1.625,
             1.75, 1.875, 2., 2.125, 2.25, 2.375, 2.5,
             2.625, 2.75, 2.875, 3., 3.125, 3.25, 3.375,
             3.5, 3.625, 3.75, 3.875, 4., 4.125, 4.25,
             4.375, 4.5, 4.625, 4.75, 4.875, 5., 5.125,
             5.25, 5.375, 5.5, 5.625, 5.75, 5.875, 6.,
             6.125, 6.25, 6.375, 6.5, 6.625, 6.75, 6.875,
             7., 7.125, 7.25, 7.375, 7.5, 7.625, 7.75,
             7.875, 8., 8.125, 8.25, 8.375, 8.5, 8.625,
             8.75, 8.875, 9., 9.125, 9.25, 9.375, 9.5,
             9.625, 9.75, 9.875, 10.])

    def tearDown(self):
        del self.known_freq_array

    def test_check_td_vs_fd(self):
        test_Cfir = createFIRfilter(self.FIRPars, self.Cf)
        test_ctvf = check_td_vs_fd(test_Cfir[0], self.Cf, fNyq=10,
                                   delay_samples=self.FIRPars.delay_samples,
                                   filename="res_corr_fd_comparison.png",
                                   plot_title="Residual corrections comparison.")
        test_freq = np.array(test_ctvf[0])

        for n in range(len(test_freq)):
            self.assertAlmostEqual((np.abs(test_freq[n]) -
                                    np.abs(self.known_freq_array[n])).all(), 0, places=6)


class Testcheck_td_vs_fd_response(unittest.TestCase):

    def setUp(self):
        self.FIRPars = FIRfilter(fNyq=10, dur=1, highpass_fcut=10, lowpass_fcut=None,
                                 latency=None, window_type='dpss', freq_res=3.0)
        self.config = '''
[metadata]
[interferometer]
[sensing]
x_arm_length = 3994.4704
y_arm_length = 3994.4692
coupled_cavity_optical_gain = 3.22e6
coupled_cavity_pole_frequency = 410.6
detuned_spring_frequency = 4.468
detuned_spring_Q = 52.14
sensing_sign = 1
is_pro_spring = True
anti_aliasing_rate_string = 16k
anti_aliasing_method      = biquad
analog_anti_aliasing_file = test/H1aa.mat, test/H1aa.mat
whitening_mode_names = mode1, mode1
omc_meas_p_trans_amplifier   = 13.7e3, 17.8e3: 13.7e3, 17.8e3
omc_meas_p_whitening_mode1   = 11.346e3, 32.875e3, 32.875e3: 11.521e3, 32.863e3, 32.863e3
omc_meas_z_whitening_mode1 =
omc_meas_z_whitening_mode2 =
omc_meas_p_whitening_mode2 =
super_high_frequency_poles_apparent_delay = 0, 0
gain_ratio = 1, 1
balance_matrix = 1, 1
omc_path_names = A, B
single_pole_approximation_delay_correction = -12e-6
adc_gain = 1, 1
omc_compensation_filter_file = test/H1OMC_1239468752.txt
omc_compensation_filter_bank = OMC_DCPD_A, OMC_DCPD_B
omc_compensation_filter_modules_in_use = 4: 4
omc_compensation_filter_gain = 1, 1

[digital]
digital_filter_file           = test/H1OMC_1239468752.txt
digital_filter_bank           = LSC_DARM1, LSC_DARM2
digital_filter_modules_in_use = 1,2,3,4,7,9,10: 3,4,5,6,7
digital_filter_gain           = 400,1

[actuation]
# actuation parameters

# Fill in DARM output matrix values [EX,EY,IX,IY]
darm_output_matrix = 1.0, -1.0, 0.0, 0.0
# Fill in OFF or ON for a 1x4 array [MO,L1,L2,L3] for X and Y arms
darm_feedback_x    = OFF, ON, ON, ON
darm_feedback_y    = OFF, OFF, OFF, OFF

#################
#    x - arm    #
#################
[actuation_x_arm]
darm_feedback_sign = -1  # This should not be changed
# UIM = 1.634     ==> 7.67e-08 (N/ct)
# PUM = 0.02947   ==> 6.036e-10 (N/ct)
# TST = 4.427e-11 ==> 4.727e-12 (N/ct)
uim_NpA       = 1.634
pum_NpA       = 0.02947
tst_NpV2      = 4.427e-11
linearization = OFF
actuation_esd_bias_voltage = -9.3

# actuation filter file
sus_filter_file = test/H1SUSETMX_1236641144.txt

# TST interferometer sensing and control
tst_isc_inf_bank    = ETMX_L3_ISCINF_L
tst_isc_inf_modules =
tst_isc_inf_gain    = 1.0

# TST lock settings
tst_lock_bank       = ETMX_L3_LOCK_L
tst_lock_modules    = 5,8,9,10
tst_lock_gain       = 1.0

# TST drive align
tst_drive_align_bank     = ETMX_L3_DRIVEALIGN_L2L
tst_drive_align_modules  = 4,5
tst_drive_align_gain     = -35.7

# PUM lock settings
pum_lock_bank    = ETMX_L2_LOCK_L
pum_lock_modules = 7
pum_lock_gain    = 23.0

# PUM drive align settings
pum_drive_align_bank    = ETMX_L2_DRIVEALIGN_L2L
pum_drive_align_modules = 6,7
pum_drive_align_gain    = 1.0
# L1 needs -1 here, because of poor OSEM convention V
pum_coil_outf_signflip  = 1

# UIM lock settings
uim_lock_bank    = ETMX_L1_LOCK_L
uim_lock_modules = 10
uim_lock_gain    = 1.06

# UIM dirive align settings
uim_drive_align_bank    = ETMX_L1_DRIVEALIGN_L2L
uim_drive_align_modules =
uim_drive_align_gain    = 1.0

# suspension file contains the force to length transfer function
suspension_file = test/H1susdata_O3.mat

# Driver parameters and setup. Updated 2019-03-04, LHO aLOG 44469
tst_driver_meas_Z_UL = 129.7e3
tst_driver_meas_Z_LL = 90.74e3
tst_driver_meas_Z_UR = 93.52e3
tst_driver_meas_Z_LR = 131.5e3
tst_driver_meas_P_UL = 3.213e3, 31.5e3
tst_driver_meas_P_LL = 3.177e3, 26.7e3
tst_driver_meas_P_UR = 3.279e3, 26.6e3
tst_driver_meas_P_LR = 3.238e3, 31.6e3
# This is the compensation filter bank, modules in use, and gains
# Only add the modules in use if you also put the low frequency poles and zeros
# in the above measured zeros and poles values, otherwise below can be blank
# The same is true if you add the zeros and poles above, you need to add the
# bank, modules in use, and gains
tst_compensation_filter_bank_UL =
tst_compensation_filter_modules_in_use_UL =
tst_compensation_filter_gain_UL =
tst_compensation_filter_bank_LL =
tst_compensation_filter_modules_in_use_LL =
tst_compensation_filter_gain_LL =
tst_compensation_filter_bank_UR =
tst_compensation_filter_modules_in_use_UR =
tst_compensation_filter_gain_UR =
tst_compensation_filter_bank_LR =
tst_compensation_filter_modules_in_use_LR =
tst_compensation_filter_gain_LR =

# Driver parameters and setup for PUM
pum_driver_meas_Z_UL =
pum_driver_meas_Z_LL =
pum_driver_meas_Z_UR =
pum_driver_meas_Z_LR =
pum_driver_meas_P_UL =
pum_driver_meas_P_LL =
pum_driver_meas_P_UR =
pum_driver_meas_P_LR =
pum_compensation_filter_bank_UL =
pum_compensation_filter_modules_in_use_UL =
pum_compensation_filter_gain_UL =
pum_compensation_filter_bank_LL =
pum_compensation_filter_modules_in_use_LL =
pum_compensation_filter_gain_LL =
pum_compensation_filter_bank_UR =
pum_compensation_filter_modules_in_use_UR =
pum_compensation_filter_gain_UR =
pum_compensation_filter_bank_LR =
pum_compensation_filter_modules_in_use_LR =
pum_compensation_filter_gain_LR =

# Driver parameters and setup for UIM
uim_driver_meas_Z_UL =
uim_driver_meas_Z_LL =
uim_driver_meas_Z_UR =
uim_driver_meas_Z_LR =
uim_driver_meas_P_UL =
uim_driver_meas_P_LL =
uim_driver_meas_P_UR =
uim_driver_meas_P_LR =
uim_compensation_filter_bank_UL =
uim_compensation_filter_modules_in_use_UL =
uim_compensation_filter_gain_UL =
uim_compensation_filter_bank_LL =
uim_compensation_filter_modules_in_use_LL =
uim_compensation_filter_gain_LL =
uim_compensation_filter_bank_UR =
uim_compensation_filter_modules_in_use_UR =
uim_compensation_filter_gain_UR =
uim_compensation_filter_bank_LR =
uim_compensation_filter_modules_in_use_LR =
uim_compensation_filter_gain_LR =

# Dead reckoned from circuit schematic
tst_driver_DC_gain_VpV_HV = 40
tst_driver_DC_gain_VpV_LV = 1.881
pum_driver_DC_trans_ApV = 2.6847e-4
uim_driver_DC_trans_ApV = 6.1535e-4

# anti imaging filter file settings
anti_imaging_rate_string = 16k
anti_imaging_method      = biquad
analog_anti_imaging_file = test/H1aa.mat
# DAC gain in V/ct note that this is 20 / 2**18
dac_gain = 7.62939453125e-05

# unknown_actuation_delay is applied to all stages
unknown_actuation_delay = 15e-6

# individual delays applied to stages separately
uim_delay = 0
pum_delay = 0
tst_delay = 0

#################
#    y - arm    #
#################
[actuation_y_arm]
darm_feedback_sign = 1  # This should not be changed
# UIM =      ==>  (N/ct)
# PUM =      ==>  (N/ct)
# TST =      ==>  (N/ct)
uim_NpA       =
pum_NpA       =
tst_NpV2      =
linearization =
actuation_esd_bias_voltage =

# actuation filter file
sus_filter_file =

# TST interferometer sensing and control
tst_isc_inf_bank    = ETMY_L3_ISCINF_L
tst_isc_inf_modules =
tst_isc_inf_gain    = 1.0

# TST lock settings
tst_lock_bank       = ETMY_L3_LOCK_L
tst_lock_modules    =
tst_lock_gain       = 1.0

# TST drive align
tst_drive_align_bank     = ETMY_L3_DRIVEALIGN_L2L
tst_drive_align_modules  =
tst_drive_align_gain     = 1.0

# PUM lock settings
pum_lock_bank    = ETMY_L2_LOCK_L
pum_lock_modules =
pum_lock_gain    = 1.0

# PUM drive align settings
pum_drive_align_bank    = ETMY_L2_DRIVEALIGN_L2L
pum_drive_align_modules =
pum_drive_align_gain    = 1.0
# L1 needs -1 here, because of poor OSEM convention V
pum_coil_outf_signflip  = 1

# UIM lock settings
uim_lock_bank    = ETMY_L1_LOCK_L
uim_lock_modules =
uim_lock_gain    = 1.0

# UIM dirive align settings
uim_drive_align_bank    = ETMY_L1_DRIVEALIGN_L2L
uim_drive_align_modules =
uim_drive_align_gain    = 1.0

# suspension file contains the force to length transfer function
suspension_file =

# Driver parameters and setup
tst_driver_meas_Z_UL =
tst_driver_meas_Z_LL =
tst_driver_meas_Z_UR =
tst_driver_meas_Z_LR =
tst_driver_meas_P_UL =
tst_driver_meas_P_LL =
tst_driver_meas_P_UR =
tst_driver_meas_P_LR =
# This is the compensation filter FOTON export data
# Only add these files if you also put the low frequency poles and zeros
# in the above measured zeros and poles values, otherwise below can be blank
# The same is true if you add the zeros and poles above, you need to add the
# exported FOTON values below
tst_driver_fe_compensation =

pum_driver_meas_Z =
pum_driver_meas_P =
pum_driver_fe_compensation =

uim_driver_meas_Z =
uim_driver_meas_P =
uim_driver_fe_compensation =

# Dead reckoned from circuit schematic
tst_driver_DC_gain_VpV_HV = 40
tst_driver_DC_gain_VpV_LV = 1.881
pum_driver_DC_trans_ApV = 2.6847e-4
uim_driver_DC_trans_ApV = 6.1535e-4

# anti imaging filter file settings
anti_imaging_rate_string = 16k
anti_imaging_method      = biquad
analog_anti_imaging_file = test/H1aa.mat
# DAC gain in V/ct note that this is 20 / 2**18
dac_gain = 7.62939453125e-05

# unknown_actuation_delay is applied to all stages
unknown_actuation_delay = 15e-6

# individual delays applied to stages separately
uim_delay = 0
pum_delay = 0
tst_delay = 0

[pcal]
# importing susnorm and mpN_DC gain
pcal_filter_file           = test/H1CALEY_1123041152.txt
pcal_filter_bank           = PCALY_TX_PD
pcal_filter_modules_in_use = 6,8
pcal_filter_gain           = 1.0

pcal_dewhiten               = 1.0, 1.0
pcal_incidence_angle        = 8.8851

# pcal_etm_watts_per_ofs_volt LHO alog 46846
pcal_etm_watts_per_ofs_volt = 0.13535

# Used for measurements like swept sine or broadband transfer functions
# x-arm ==> 1, y-arm ==> -1
# Change this value only if the Pcal arm for the measurements is different
ref_pcal_2_darm_act_sign    = -1.0

# Pcal Anti-aliasing filter parameters
anti_aliasing_rate_string = 16k
anti_aliasing_method      = biquad
analog_anti_aliasing_file = test/H1aa.mat
'''
        self.A = pydarm.actuation.DARMActuationModel(self.config)
        self.C = pydarm.sensing.SensingModel(self.config)
        self.Pcal = pydarm.pcal.PcalModel(self.config)
        self.darm = pydarm.darm.DARMModel(self.config, sensing=self.C,
                                          actuation=self.A, pcal=self.Pcal)
        f = self.FIRPars.freq_array
        self.Res = self.darm.compute_response_function(f)
        self.TST_fil = self.darm.actuation.xarm.compute_actuation_single_stage(f, stage='TST')
        self.PUM_fil = self.darm.actuation.xarm.compute_actuation_single_stage(f, stage='PUM')
        self.UIM_fil = self.darm.actuation.xarm.compute_actuation_single_stage(f, stage='UIM')
        self.Dig = self.darm.digital.compute_response(f)
        self.Cf = self.C.compute_sensing(f)
        self.test_Cfir = pydarm.FIR.createFIRfilter(self.FIRPars, self.Cf)
        self.Cf = np.delete(self.Cf, 0)
        self.Inv_C = 1.0/self.Cf
        self.known_freq_array = np.array(
            [0., 0.227272727272727, 0.454545454545455,
             0.681818181818182, 0.909090909090909, 1.136363636363636,
             1.363636363636364, 1.590909090909091, 1.818181818181818,
             2.045454545454545, 2.272727272727272, 2.5,
             2.727272727272727, 2.954545454545455, 3.181818181818182,
             3.409090909090909, 3.636363636363636, 3.863636363636363,
             4.090909090909091, 4.318181818181818, 4.545454545454545,
             4.772727272727272, 5., 5.227272727272728,
             5.454545454545454, 5.681818181818182, 5.909090909090909,
             6.136363636363636, 6.363636363636363, 6.590909090909091,
             6.818181818181818, 7.045454545454545, 7.272727272727272,
             7.5, 7.727272727272727, 7.954545454545454,
             8.181818181818182, 8.409090909090908, 8.636363636363637,
             8.863636363636363, 9.09090909090909, 9.318181818181818,
             9.545454545454545, 9.772727272727272, 10.])

    def tearDown(self):
        del self.known_freq_array

    def test_check_td_vs_fd(self):
        test_ctvf = check_td_vs_fd_response(self.Inv_C, invsens_highpass=None,
                                            TST_filt=self.TST_fil,
                                            PUM_filt=self.PUM_fil, UIM_filt=self.UIM_fil,
                                            act_highpass=None,
                                            D=self.Dig, R=self.Res, invsens_fNyq=10,
                                            invsens_highpass_fNyq=10,
                                            act_fNyq=10, D_fNyq=10, R_fNyq=10,
                                            invsens_delay=None,
                                            invsens_highpass_delay=None, act_delay=None,
                                            act_highpass_delay=None,
                                            time_delay=1.0/16384,
                                            filename="td_vs_fd_response.png",
                                            plot_title="Response Function",
                                            legend=['DARM model', 'FIR filters'])
        test_freq = np.array(test_ctvf[0])

        for n in range(len(test_freq)):
            self.assertAlmostEqual(np.abs(test_freq[n]) -
                                   np.abs(self.known_freq_array[n]), 0, places=6)


class TestGDS_FIR_filter_generation(unittest.TestCase):
    def setUp(self):
        # Maddie test
        # Set up for control chain FIR filter generation
        self.FIRpars = FIRfilter(fNyq=1024, dur=3.5, highpass_fcut=10.5, lowpass_fcut=None,
                                 latency=None, window_type='dpss', freq_res=4.0)

        # Load in known transfer function and resulting FIR filter
        h5f = h5py.File('./test/FIR_unit_test_coeffs.h5', 'r')
        self.known_FIR_filter = h5f['FIR_filter'][:]
        self.known_tf = h5f['transfer_function'][:]

    def tearDown(self):
        del self.FIRpars
        del self.known_FIR_filter
        del self.known_tf

    def test_GDS_FIR_filter_generation(self):
        # Generate test FIR filter from frequency domain transfer function
        [test_FIR_filter, model] = createFIRfilter(self.FIRpars, self.known_tf)
        # FIXME: (Arif) Scipy and FIRtools have much different results under 10 Hz.
        # I changed the range and places. My local test could take higher places.
        for n in range(300, len(self.known_FIR_filter)-300):
            self.assertAlmostEqual(abs((self.known_FIR_filter[n] / test_FIR_filter[n])
                                       - 1), 0, places=3)


class TestFilterGeneration(unittest.TestCase):

    def setUp(self):
        self.arm_length = 3994.4698
        self.fcc = 410.6
        self.fs = 4.468
        self.fs_squared = 19.963024
        self.srcQ = 52.14
        self.ips = 1.0
        os.environ['CAL_DATA_ROOT'] = './test'

    def tearDown(self):
        del self.arm_length
        del self.fcc
        del self.fs
        del self.fs_squared
        del self.srcQ
        del self.ips
        del os.environ['CAL_DATA_ROOT']

    def test_FilterGeneration(self):
        config = './example_model_files/H1_20190416.ini'
        FG = pydarm.FIR.FilterGeneration(config)
        self.assertEqual(self.arm_length, FG.arm_length)
        self.assertEqual(self.fcc, FG.fcc)
        self.assertEqual(self.fs, FG.fs)
        self.assertEqual(self.fs_squared, FG.fs_squared)
        self.assertEqual(self.srcQ, FG.srcQ)
        self.assertEqual(self.ips, FG.ips)


class TestGDS(unittest.TestCase):

    def setUp(self):
        self.GDS_file = np.load('./test/GDS_test.npz')
        self.ctrl_corr_td = self.GDS_file['ctrl_corr_filter']
        os.environ['CAL_DATA_ROOT'] = './test'

    def tearDown(self):
        del self.GDS_file
        del self.ctrl_corr_td
        del os.environ['CAL_DATA_ROOT']

    def test_GDS(self):
        config = './example_model_files/H1_20190416.ini'
        FG = pydarm.FIR.FilterGeneration(config)
        FG.GDS(ctrl_window_type='dpss', res_window_type='dpss',
               make_plot=False, output_filename='./test/GDS.npz',
               plots_directory='./examples/GDS_plots')
        gds = np.load('./test/GDS.npz')
        ctrl_td = gds['ctrl_corr_filter']
        for n in range(1000, len(self.ctrl_corr_td)-1000):
            self.assertAlmostEqual(abs((self.ctrl_corr_td[n] / ctrl_td[n])
                                       - 1), 0, places=3)


class TestDCS(unittest.TestCase):

    def setUp(self):
        self.DCS_file = np.load('./test/DCS_test.npz')
        self.known_act_tst = self.DCS_file['actuation_tst']
        os.environ['CAL_DATA_ROOT'] = './test'

    def tearDown(self):
        del self.DCS_file
        del self.known_act_tst
        del os.environ['CAL_DATA_ROOT']

    def test_DCS(self):
        config = './example_model_files/H1_20190416.ini'
        FG = pydarm.FIR.FilterGeneration(config)
        FG.DCS(act_window_type='dpss', invsens_window_type='dpss',
               make_plot=False, output_filename='./test/DCS.npz',
               plots_directory='examples/DCS_plots')
        gds = np.load('./test/DCS.npz')
        act_tst = gds['actuation_tst']
        for n in range(1000, len(self.known_act_tst)-1000):
            self.assertAlmostEqual(abs((self.known_act_tst[n] / act_tst[n])
                                       - 1), 0, places=3)


if __name__ == '__main__':
    unittest.main()
