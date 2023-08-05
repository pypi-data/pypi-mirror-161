import unittest
import pydarm
import numpy as np


class TestFindPrimeFactors(unittest.TestCase):

    def setUp(self):
        self.N = 3
        self.known_results = np.array([3, 1])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_find_prime_factors(self):
        test = pydarm.FIRtools.find_prime_factors(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.real(test[n]),
                                   np.real(self.known_results[n]))


class TestFindM(unittest.TestCase):

    def setUp(self):
        self.N = 10
        self.known_results_0 = 10
        self.known_results_1 = np.array([2, 5, 1])

    def tearDown(self):
        del self.N
        del self.known_results_0
        del self.known_results_1

    def test_find_M(self):
        test = pydarm.FIRtools.find_M(self.N)

        self.assertEqual(test[0], self.known_results_0)
        for n in range(len(test[1])):
            self.assertAlmostEqual(np.real(test[1][n]),
                                   np.real(self.known_results_1[n]))


class TestFindExpArray(unittest.TestCase):

    def setUp(self):
        self.N = 10
        self.known_results = np.array([
            1.+0.j,
            0.80901699-0.58778525j,
            0.30901699-0.95105652j,
            -0.30901699-0.95105652j,
            -0.80901699-0.58778525j,
            -1.+0.j,
            -0.80901699+0.58778525j,
            -0.30901699+0.95105652j,
            0.30901699+0.95105652j,
            0.80901699+0.58778525j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_find_exp_array(self):
        test = pydarm.FIRtools.find_exp_array(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestFindExpArray2(unittest.TestCase):

    def setUp(self):
        self.N = 10
        self.known_results = np.array(
            [1.+0.j,
             0.95105652-0.30901699j,
             0.30901699-0.95105652j,
             -0.95105652-0.30901699j,
             0.30901699+0.95105652j,
             0.-1.j,
             0.30901699+0.95105652j,
             -0.95105652-0.30901699j,
             0.30901699-0.95105652j,
             0.95105652-0.30901699j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_find_exp_array2(self):
        test = pydarm.FIRtools.find_exp_array2(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestDFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [55.+0.j,
             -5.+15.38841769j,
             -5.+6.8819096j,
             -5.+3.63271264j,
             -5.+1.62459848j,
             -5.+0.j,
             -5.-1.62459848j,
             -5.-3.63271264j,
             -5.-6.8819096j,
             -5.-15.38841769j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_dft(self):
        test = pydarm.FIRtools.dft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestRDFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [55.+0.j,
             -5.+15.38841769j,
             -5.+6.8819096j,
             -5.+3.63271264j,
             -5.+1.62459848j,
             -5.+0.j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_rdft(self):
        test = pydarm.FIRtools.rdft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestIRDFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [5.50000000e+00,
             -1.84241319e+00,
             -1.80700362e-20,
             -2.22222222e-01,
             -7.83034902e-20,
             -9.46715662e-02,
             0.00000000e+00,
             -6.29152406e-02,
             -7.83034902e-20,
             -5.55555556e-02,
             -7.83034902e-20,
             -6.29152406e-02,
             0.00000000e+00,
             -9.46715662e-02,
             -7.83034902e-20,
             -2.22222222e-01,
             -1.80700362e-20,
             -1.84241319e+00])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_irdft(self):
        test = pydarm.FIRtools.irdft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))


class TestFFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [55.+0.j,
             -5.+15.38841769j,
             -5.+6.8819096j,
             -5.+3.63271264j,
             -5.+1.62459848j,
             -5.+0.j,
             -5.-1.62459848j,
             -5.-3.63271264j,
             -5.-6.8819096j,
             -5.-15.38841769j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_fft(self):
        test = pydarm.FIRtools.fft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestIFFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [5.5+0.j,
             -0.5-1.538841768587627j,
             -0.5-0.688190960235587j,
             -0.5-0.36327126400268j,
             -0.5-0.162459848116453j,
             -0.5+0.j,
             -0.5+0.162459848116453j,
             -0.5+0.36327126400268j,
             -0.5+0.688190960235587j,
             -0.5+1.538841768587627j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_ifft(self):
        test = pydarm.FIRtools.ifft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestPrime_FFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [55.+2.602085213965211e-19j,
             -5.+1.538841768587627e+01j,
             -5.+6.881909602355868e+00j,
             -5.+3.632712640026804e+00j,
             -5.+1.624598481164532e+00j,
             -5.-3.079134169858833e-18j,
             -5.-1.624598481164532e+00j,
             -5.-3.632712640026804e+00j,
             -5.-6.881909602355868e+00j,
             -5.-1.538841768587627e+01j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_prime_fft(self):
        test = pydarm.FIRtools.prime_fft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestPrime_IRFFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [5.500000000000000e+00, -1.842413193195909e+00,
             4.549226020051922e-20, -2.222222222222222e-01,
             -8.417075210445289e-20, -9.467156616899152e-02,
             -1.070816960479511e-19, -6.291524063509968e-02,
             -1.051106487897057e-19, -5.555555555555556e-02,
             3.259193740688347e-20, -6.291524063509968e-02,
             -3.212450881438532e-20, -9.467156616899152e-02,
             -5.489919065095004e-20, -2.222222222222222e-01,
             2.254883592741939e-19, -1.842413193195909e+00])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_prime_irfft(self):
        test = pydarm.FIRtools.prime_irfft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))


class TestPrime_RFFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [55.-7.401486830834377e-18j,
             -5.+1.538841768587627e+01j,
             -5.+6.881909602355868e+00j,
             -5.+3.632712640026804e+00j,
             -5.+1.624598481164532e+00j,
             -5.+1.850371707708594e-18j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_prime_rfft(self):
        test = pydarm.FIRtools.prime_rfft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestRFFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [55.+0.j,
             -5.+15.388417685876267j,
             -5.+6.881909602355868j,
             -5.+3.632712640026804j,
             -5.+1.624598481164532j,
             -5.+0.j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_rfft(self):
        test = pydarm.FIRtools.rfft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class TestIRFFT(unittest.TestCase):

    def setUp(self):
        self.N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.known_results = np.array(
            [5.500000000e+00, -1.842413193e+00, 6.023345403e-21,
             -2.222222222e-01, 1.204669081e-20, -9.467156617e-02,
             1.204669081e-20, -6.291524064e-02, 0.000000000e+00,
             -5.555555556e-02, 0.000000000e+00, -6.291524064e-02,
             1.204669081e-20, -9.467156617e-02, 1.204669081e-20,
             -2.222222222e-01, 9.035018104e-21, -1.842413193e+00])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_irfft(self):
        test = pydarm.FIRtools.irfft(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(
                np.abs(np.angle(test[n], deg=True) -
                       np.angle(self.known_results[n], deg=True)), 0.0, places=6)


class Testmattimesvec(unittest.TestCase):

    def setUp(self):
        self.M = [1., 2., 3.]
        self.V = [1., 2.]
        self.known_results = [1.33333333333333, 1.]

    def tearDown(self):
        del self.M
        del self.V
        del self.known_results

    def test_mattimesvec(self):
        test = pydarm.FIRtools.mat_times_vec(self.M, self.V)
        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))


class TestDPSS(unittest.TestCase):

    def setUp(self):
        self.N = 5
        self.B = 16
        self.known_results = np.array(
            [0.44321078700654, 0.83098434177807, 1.,
             0.83098434177807, 0.44321078700654])

    def tearDown(self):
        del self.N
        del self.B
        del self.known_results

    def test_DPSS(self):
        test = pydarm.FIRtools.DPSS(self.N, self.B)
        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]),
                                   places=6)


class TestcomputeTn(unittest.TestCase):

    def setUp(self):
        self.N = 1
        self.B = 16
        self.known_results = 1.0

    def tearDown(self):
        del self.N
        del self.B
        del self.known_results

    def test_computeTn(self):
        test = pydarm.FIRtools.compute_Tn(self.N, self.B)
        self.assertAlmostEqual(np.abs(test),
                               np.abs(self.known_results))


class TestcomputeW0Lagged(unittest.TestCase):

    def setUp(self):
        self.N = 16
        self.B = 1
        self.known_results = [1.000000000e+00+0.j,
                              -1.065235759e-01-0.021188857j,
                              3.652655927e-02+0.015129796j,
                              4.151055100e-02+0.027736463j,
                              3.282099121e-02+0.032820991j,
                              2.101570991e-02+0.031452233j,
                              1.014723686e-02+0.024497597j,
                              2.659050841e-03+0.013367951j,
                              9.183429072e-20+0.j]

    def tearDown(self):
        del self.N
        del self.B
        del self.known_results

    def test_compute_W0_lagged(self):
        test = pydarm.FIRtools.compute_W0_lagged(self.N, self.B)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]))
            self.assertAlmostEqual(np.angle(test[n], deg=True),
                                   np.angle(self.known_results[n], deg=True),
                                   places=6)


class TestDolphChebyshev(unittest.TestCase):

    def setUp(self):
        self.N = 16
        self.B = 1
        self.known_results = np.array(
            [0.8668296927388, 0.50431006465412, 0.62167043818165,
             0.73337937658832, 0.8327331038598, 0.91351461128685,
             0.9705186581255,  1., 1., 0.9705186581255,
             0.91351461128685, 0.8327331038598, 0.73337937658832,
             0.62167043818165, 0.50431006465412, 0.8668296927388])

    def tearDown(self):
        del self.N
        del self.B
        del self.known_results

    def test_DolphChebyshev(self):
        test = pydarm.FIRtools.DolphChebyshev(self.N, self.B)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]), places=6)
            self.assertAlmostEqual(np.angle(test[n], deg=True),
                                   np.angle(self.known_results[n], deg=True),
                                   places=6)


class TestResample(unittest.TestCase):

    def setUp(self):
        self.N = np.linspace(1, 100, 15)
        self.B = 10
        self.known_results = np.array(
            [1., 12.01200936894652, 23.05579571636385,
             34.0362625611402, 45.1101331908868, 55.8898668091132,
             66.9637374388598, 77.94420428363615, 88.98799063105348,
             100.])

    def tearDown(self):
        del self.N
        del self.B
        del self.known_results

    def test_resample(self):
        test = pydarm.FIRtools.resample(self.N, self.B)
        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]), places=6)


class TestFreqresp(unittest.TestCase):

    def setUp(self):
        self.N = np.linspace(1, 16, 8)
        self.known_results = np.array(
            [68.+0.j,
             59.48445890636821-30.52945786235738j,
             36.84293730912102-51.76597925799235j,
             7.68035907617445-57.79361930967018j,
             -18.57943825259448-48.11882085320455j,
             -34.18355417297142-27.60239500215145j,
             -35.76197233728974-4.36222766254847j,
             -25.22421250295184+13.45302599634338j,
             -8.57142857142857+20.6932591060551j,
             6.78944776685062+16.84735056355831j,
             15.06065526360838+5.72520046505279j,
             14.15621988372335-6.55486359389886j,
             6.1001834190962-14.32465515694111j,
             -4.31159130661836-14.67005982624531j,
             -11.88468421883575-8.34956381179203j,
             -13.33966008951263+0.9510851460444j,
             -8.57142857142857+8.57142857142857j,
             -0.38653393620457+11.0850464457693j,
             7.04820384659785+7.76456399152353j,
             10.25421289199872+0.6991807859211j,
             8.02164711553033-6.395424105799j,
             1.82671829025581-10.04394696175532j,
             -5.03754860172615-8.64991512808857j,
             -9.14029290683677-3.15358857555265j,
             -8.57142857142857+3.55040196319796j,
             -3.79633017320841+8.10339541063871j,
             2.66677748140826+8.33474493830941j,
             7.54930744558597+4.2799094461385j,
             8.45760771796795-1.90387551634815j,
             5.02832789185148-7.05299088135736j,
             -0.93436874288388-8.57976326067755j,
             -6.3868770645046-5.74418800922619j,
             -8.57142857142857+0.j])

    def tearDown(self):
        del self.N
        del self.known_results

    def test_freqresp(self):
        test = pydarm.FIRtools.freqresp(self.N)

        for n in range(len(test)):
            self.assertAlmostEqual(np.abs(test[n]),
                                   np.abs(self.known_results[n]), places=6)
            self.assertAlmostEqual(np.angle(test[n], deg=True),
                                   np.angle(self.known_results[n], deg=True),
                                   places=6)


if __name__ == '__main__':
    unittest.main()
