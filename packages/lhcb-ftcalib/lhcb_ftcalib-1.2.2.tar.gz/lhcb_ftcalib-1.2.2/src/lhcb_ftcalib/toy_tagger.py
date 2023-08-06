import os
import iminuit
from iminuit import cost
import pickle
import numpy as np
import pandas as pd


class _PDF_RNG:
    # Generator class for arbitrary numerical probability distribution
    def __init__(self, xmin, xmax, precision, func, *args, **kwargs):
        # Sample distribution func
        self._X = np.linspace(xmin, xmax, precision)
        self._PDF = func(self._X, *args, **kwargs)
        self._PDF /= np.sum(self._PDF)

        self._dx = (xmax - xmin) / precision

    def __smear(self, x):
        # Smear sampled value randomly inside sampling bin
        # In the limit precision -> infinity, this generates a smooth distribution
        x += np.random.uniform(-0.5 * self._dx, 0.5 * self._dx, size=len(x))
        return x

    def __call__(self, N):
        return self.__smear(np.random.choice(self._X, size=N, p=self._PDF))


class ToyDataGenerator:
    """
    Flavour Tagging toy data generator

    :param tmin: Lower bound of decay time range
    :type tmin: float
    :param tmax: Upper bound of decay time range
    :type tmax: float
    :param sampling_precision: Number of interpolation bins for sampling probability distributions
    :type sampling_precision: int
    :param seed: Random seed
    :type seed: int
    """
    def __init__(self, tmin, tmax, sampling_precision=10000, seed=384994875):
        self.tmin = tmin
        self.tmax = tmax
        self.sampling_precision = sampling_precision
        if seed is not None:
            np.random.seed(seed)

    def __arctan_acceptance(self, t):
        return 2 * np.arctan(2 * t) / np.pi

    def __sigmoid_acceptance(self, t):
        return 2 * (1 / (1 + np.exp(-1.5 * t)) - 0.5)

    def __decay(self, t, gamma, acceptance):
        return acceptance(t) * np.exp(-gamma * t)

    def __decay_oscil(self, t, gamma, acceptance, S, C, A, DM, DG, d):
        pdf = -d * S * np.sin(DM * t)
        pdf += d * C * np.cos(DM * t)
        pdf += A * np.sinh(0.5 * DG * t)
        pdf += np.cosh(0.5 * DG * t)
        pdf *= np.exp(-gamma * t)

        # Normalization needs to be done elsewhere
        # norm = d * (C * gamma - S * DM) / (gamma**2 + DM**2)
        # norm += (gamma + A * DG) / (gamma**2 - DG**2)
        # pdf /= norm

        pdf *= acceptance(t)

        return pdf

    def __generate_decay(self, N, lifetime, acceptance):
        # Returns decay time distribution with acceptance model
        return _PDF_RNG(self.tmin, self.tmax, self.sampling_precision, self.__decay, 1 / lifetime, acceptance)(N)

    def __generate_true_decay_time_CPV(self, N, lifetime, prod_flavour, S, C, A, DM, DG, acceptance):
        gamma = 1 / lifetime
        assert gamma > DG, "Decay time pdf cannot be normalized"

        gen_Bdecay = _PDF_RNG(self.tmin, self.tmax, self.sampling_precision, self.__decay_oscil,
                              gamma, acceptance, S=S, C=C, A=A, DM=DM, DG=DG, d=prod_flavour)

        return gen_Bdecay(N)

    def __generate_decaytime_CPV(self, Nplus, Nminus, lifetime, S, C, A, DM, DG, acceptance):
        # Returns true tau distribution given lifetime and CPV parameters
        tau_plus  = self.__generate_true_decay_time_CPV(Nplus,  lifetime, prod_flavour=+1, S=S, C=C, A=A, DM=DM, DG=DG, acceptance=acceptance)
        tau_minus = self.__generate_true_decay_time_CPV(Nminus, lifetime, prod_flavour=-1, S=S, C=C, A=A, DM=DM, DG=DG, acceptance=acceptance)

        return tau_plus, tau_minus

    def __generate_reco_tau(self, truetau, resolution_scale=5e-2):
        # Returns reconstructed tau distribution given true tau distribution
        # std(B_TRUETAU - B_TAU) ~ 5.0e-2 ps

        # Tau = Truetau + resolution noise
        tau = truetau + np.random.normal(loc=0, scale=resolution_scale, size=len(truetau))
        # Reassign tau < 0 values to some arbitrary tau in range
        tau[tau <= 0] = np.random.uniform(0.001, tau.max(), (tau <= 0).sum())

        return tau

    def __get_trueid_asymmetry(self, lifetime, DM, DG, CPV, acceptance):
        # If B / Bbar pdf normalisation is not properly taken into account
        # CP asymmetry has vertical offset and is warped even if #B == #Bbar is generated
        # By creating a (huge) TRUEID imbalance, the asymmetry is correctly centered
        gamma = 1 / lifetime
        assert gamma > DG, "Decay time pdf cannot be normalized"

        tlin = np.linspace(self.tmin, self.tmax, self.sampling_precision)
        dx = (self.tmax - self.tmin) / self.sampling_precision
        shapeBdecay    = self.__decay_oscil(tlin, gamma, acceptance, S=CPV["S"], C=CPV["C"], A=CPV["A"], DM=DM, DG=DG, d=+1)
        shapeBbardecay = self.__decay_oscil(tlin, gamma, acceptance, S=CPV["S"], C=CPV["C"], A=CPV["A"], DM=DM, DG=DG, d=-1)
        norm_B    = 0.5 * np.sum(dx * (shapeBdecay[1:] + shapeBdecay[:-1]))
        norm_Bbar = 0.5 * np.sum(dx * (shapeBbardecay[1:] + shapeBbardecay[:-1]))

        return norm_B / norm_Bbar

    def __mistag_distribution(self, Npos, Nneg, tagger_type, func, params):
        # Draw random mistag values from pre-sampled distributions
        # These distributions were sampled for positive and negative tag decisions
        def smear(distr, binwidth):
            # Add noise to sampled values so that they are uniformly distributed between bins
            N = len(distr)
            smear = np.random.uniform(-binwidth / 2, binwidth / 2, size=N)
            distr += smear
            distr[distr > 0.5] -= 0.5
            return distr

        taghists = pickle.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "tagger_distributions.dict"), "rb"))

        histbins      = taghists["nbins"]
        histcenters   = taghists["centers"]
        dist_pos      = taghists[tagger_type][1]["bins"]
        dist_neg      = taghists[tagger_type][-1]["bins"]
        p_density_pos = dist_pos / (2 * histbins)
        p_density_neg = dist_neg / (2 * histbins)

        # Generate raw eta distributions
        eta_plus  = smear(np.random.choice(histcenters, size=Npos, p=p_density_pos), 0.5 / histbins)
        eta_minus = smear(np.random.choice(histcenters, size=Nneg, p=p_density_neg), 0.5 / histbins)

        # omega distribution can exceed 0.5. This does not make sense but it
        # can happen for a given calibration function. By default the toy
        # generator should scale the eta distribution so that the calibrated
        # mistag does not exceed 0.5. The same could happen for omega < 0 which
        # are equally nonsensical, but those values can be forced to be
        # perfectly tagged.
        func.init_basis(eta_plus)
        omega_plus  = func.eval(params, eta_plus,  +np.ones(Npos))
        omega_minus = func.eval(params, eta_minus, -np.ones(Nneg))

        def rescale(eta, omega):
            # Rescale eta so that omega stays in range
            omega_max = omega.max()
            if omega_max <= 0.5:
                # All good
                return eta

            eta_critical = eta[np.argmin(np.abs(omega - 0.5))] - 1e-2

            eta_max = eta.max()
            eta *= eta_critical / eta_max
            return eta

        eta_plus  = rescale(eta_plus,  omega_plus)
        eta_minus = rescale(eta_minus, omega_minus)

        return eta_plus, eta_minus

    def __call__(self, N, func, params, osc, tagger_types, lifetime=1.52, DM=0.5065, DG=0, Aprod=0, tag_effs=None, resolution_scale=5e-2, acceptance="arctan", CPV=None):
        r"""
        Call of toy data generator functor.

        :param N: Number of events to generate
        :type N: int
        :param func: Calibration function
        :type func: CalibrationFunction
        :param params: List of calibration parameters set in flavour convention for each tagger.
        :type params: list of list
        :param osc: If true, will simulate B oscillation
        :type osc: bool
        :param tagger_types: Pre-sampled distribution to use. One of ["SSKaon", "SSproton", "SSPion", "OSElectron", "VtxCh", "OSMuon", "OSCharm", "OSKaon"]
        :type tagger_types: list of str
        :param lifetime: B meson lifetime
        :type lifetime: float
        :param DM: :math:`\Delta m`
        :type DM: float
        :param DG: :math:`\Delta\Gamma`
        :type DG: float
        :param Aprod: Production asymmetry
        :type Aprod: float
        :param tag_effs: List of tagging efficiencies. Default: 100% for each tagger
        :type tag_effs: list of float or None
        :param resolution_scale: With of resolution gaussian (width of TRUETAU - TAU)
        :type resolution_scale: float
        :param acceptance: Which acceptance function to use ("arctan" or "sigmoid")
        :type acceptance: str
        :param CPV: dict of CPV parameters S, C, and A for decay to CP-invariant final state
        :type CPV: dict
        """
        df = pd.DataFrame({"FLAV_PROD" : np.ones(N, dtype=np.int32)})

        use_acceptance = {
            "arctan" : self.__arctan_acceptance,
            "sigmoid" : self.__sigmoid_acceptance,
        }[acceptance]

        Nplus = int(N * 0.5 * (1 + Aprod))
        Nminus = N - Nplus

        if osc:
            # Generate decay time distributions
            if CPV is not None:
                cpvaprod = self.__get_trueid_asymmetry(lifetime, DM, DG, CPV, use_acceptance)

                # Scale B0 fraction
                Nplus *= cpvaprod
                Nplus = int(Nplus)

                # Scale up statistics so that N events are generated
                inflate = N / (Nminus + Nplus)
                Nplus *= inflate
                Nminus *= inflate
                Nplus = int(Nplus)
                Nminus = int(Nminus)
                Nminus += N - Nplus - Nminus

                df.loc[Nplus:, "FLAV_PROD"] *= -1

                df["TRUETAU"] = np.zeros(len(df))
                tau_B, tau_Bbar = self.__generate_decaytime_CPV(Nplus, Nminus, lifetime,
                                                                S=CPV["S"], C=CPV["C"], A=CPV["A"],
                                                                DG=DG, DM=DM, acceptance=use_acceptance)
                df.loc[df.FLAV_PROD ==  1, "TRUETAU"] = tau_B
                df.loc[df.FLAV_PROD == -1, "TRUETAU"] = tau_Bbar
            else:
                Nplus = int(N * 0.5 * (1 + Aprod))
                Nminus = N - Nplus
                df.loc[Nplus:, "FLAV_PROD"] *= -1
                df["TRUETAU"] = self.__generate_decay(N, lifetime, acceptance=use_acceptance)

            df.eval("FLAV_DECAY=FLAV_PROD", inplace=True)

            df["TAUERR"] = self.__generate_decay(N, lifetime=4.5e-2, acceptance=use_acceptance)
            df["TAU"] = self.__generate_reco_tau(df.TRUETAU, resolution_scale=resolution_scale)

            # Oscillate mesons by inverting decay flavour if oscillation is likely
            # This way, there is a time oscillation for prod!=pred and prod!=pred
            Amix = np.cos(DM * df.TAU) / np.cosh(0.5 * DG * df.TAU)
            osc_prob = 0.5 * (1 - Amix)
            rand = np.random.uniform(0, 1, N)
            has_oscillated = rand < osc_prob
            df.loc[has_oscillated, "FLAV_DECAY"] *= -1

            # Compute predicted flavour
            df.eval("FLAV_PRED=FLAV_DECAY", inplace=True)
            df.loc[np.sign(Amix) == -1, "FLAV_PRED"] *= -1

            df["OSC"] = has_oscillated
        else:
            df.loc[Nplus:, "FLAV_PROD"] *= -1
            df.eval("FLAV_DECAY=FLAV_PROD", inplace=True)
            df.eval("FLAV_PRED=FLAV_DECAY", inplace=True)

        # Simulate tagging
        for t, tparams in enumerate(params):
            name = f"TOY{t}"
            dec_branch = f"{name}_DEC"
            eta_branch = f"{name}_ETA"
            omg_branch = f"{name}_OMEGA"

            # Compute mistag distribution eta
            df.eval(f"{dec_branch}=FLAV_PROD", inplace=True)  # perfect tagging
            eta_plus, eta_minus = self.__mistag_distribution(Npos = (df[dec_branch] == +1).sum(),
                                                             Nneg = (df[dec_branch] == -1).sum(),
                                                             tagger_type = tagger_types[t],
                                                             func        = func,
                                                             params      = tparams)
            df.eval(f"{eta_branch} = 0.5", inplace=True)
            df.loc[df[dec_branch] == +1, eta_branch] = eta_plus
            df.loc[df[dec_branch] == -1, eta_branch] = eta_minus

            # Test monotonicity (which is an assumpting we make here)
            lineshape_plus = func.eval(tparams, np.linspace(0.001, 0.5, 1000), np.ones(1000))
            lineshape_minus = func.eval(tparams, np.linspace(0.001, 0.5, 1000), -np.ones(1000))
            if not np.all(np.diff(lineshape_plus) >= 0) or not np.all(np.diff(lineshape_minus) >= 0):
                print(f"Toy warning: Calibration function is not monotonic for parameters {tparams} -> Abort")
                return None

            # Calibrate mistag distribution
            # func.init_basis(df[eta_branch])
            df[omg_branch] = func.eval(tparams, df[eta_branch], df[dec_branch])

            Noverflow = (df[omg_branch] > 0.5).sum()
            if Noverflow > 0:
                print(f"Toy warning: {Noverflow} calibrated mistags still exceed 0.5"
                      f"with a maximum at {df.loc[df[omg_branch] > 0.5, omg_branch].max()}."
                       "Make sure calibration function is monotone! Will force those values to 0.5")
                df.loc[df[omg_branch] >= 0.5, dec_branch] = 0
                df.loc[df[omg_branch] >= 0.5, omg_branch] = 0.5
            df.loc[df[omg_branch] < 0, omg_branch] = 0  # Underflow

            # Simulate tagging decisions (this is where the magic happens and
            # the calibration parameters are encoded into the (eta, dec)
            # information)
            rand = np.random.uniform(0, 1, N)
            df.loc[df[omg_branch] > rand, dec_branch] *= -1

        df = df.sample(frac=1)
        df.reset_index(drop=True, inplace=True)

        if tag_effs is not None:
            assert len(tag_effs) == len(tagger_types)
            for i, tag_eff in enumerate(tag_effs):
                df.loc[int(tag_eff * len(df)):, f"TOY{i}_OMEGA"] = 0.5
                df.loc[int(tag_eff * len(df)):, f"TOY{i}_ETA"] = 0.5
                df.loc[int(tag_eff * len(df)):, f"TOY{i}_DEC"] = 0

            df = df.sample(frac=1)
            df.reset_index(drop=True, inplace=True)

        df["eventNumber"] = np.arange(len(df))
        return df


def exponential_background(x, e):
    return np.exp(-e * x)


def mass_peak(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma)**2) / (sigma * np.sqrt(2 * np.pi))


class MultiComponentToyDataGenerator:
    """
    Toy generator for toy data of multiple dataset components like signal, background, CPViolating backgrounds etc.

    :param mass_range: List of lower and upper mass range to generate
    :type mass_range: list
    :param time_range: List of lower and upper decay time range to generate
    :type time_range: list
    :param sampling_precision: Number of interpolation bins for sampling probability distributions
    :type sampling_precision: int
    """
    def __init__(self, mass_range, time_range, sampling_precision=10000):
        assert isinstance(mass_range, list) and len(mass_range) == 2
        assert mass_range[1] > mass_range[0]
        assert isinstance(time_range, list) and len(time_range) == 2
        assert time_range[1] > time_range[0]
        self.mass_range = mass_range
        self.time_range = time_range
        self._sampling_precision = sampling_precision
        self._mass_distributions = []
        self._toy_tag_generators = []
        self._toy_tag_configs = []
        self._pdf = None
        self._startparams = None

    def add_component(self, distribution, *mass_args, **mass_kwargs):
        """ Add another data component

            :param distribution: probability distribution (not normalized) of a component of the data. Its first argument is the dependent variable.
            :type distribution: function
            :param args: arguments of distribution
            :type args: list
            :param kwargs: keyword arguments of distribution
            :type kwargs: dict
        """
        self._mass_distributions.append(_PDF_RNG(*self.mass_range, self._sampling_precision, func=distribution, *mass_args, **mass_kwargs))
        self._mass_arguments = [mass_args, mass_kwargs]

    def configure_component(self, *args, **kwargs):
        """ Configure tagging data of previously added component

            :param args: Arguments to pass to ToyDataGenerator
            :type args: list
            :param kwargs: Keyword arguments to pass to ToyDataGenerator
            :type kwargs: dict
        """
        self._toy_tag_generators.append(ToyDataGenerator(*self.time_range))
        self._toy_tag_configs.append((args, kwargs))

    def set_mass_pdf(self, pdf, signal, background, **startparams):
        """ Set the probability distribution for fitting the mass

            :param pdf: Full mass model, see requirements of iminuits ExtendedUnbinnedNLL. First two arguments need to be named "Nsig", and "Nbkg"
                for the signal and background normalization
            :type pdf: function
            :param signal: Normalized signal component of mass pdf.
            :type signal: function
            :param background: Normalized background component of mass pdf.
            :type background: function
            :param startparams: Starting parameters of full mass model
            :type startparams: dict
        """
        args_pdf = pdf.__code__.co_varnames[1:pdf.__code__.co_argcount]
        args_sig = signal.__code__.co_varnames[1:signal.__code__.co_argcount]
        args_bkg = background.__code__.co_varnames[1:background.__code__.co_argcount]

        assert args_pdf[0] == "Nsig", "The first argument of full pdf needs to be signal nomrmalization \"Nsig\""
        assert args_pdf[1] == "Nbkg", "The second argument of full pdf needs to be background nomrmalization \"Nbkg\""
        if set(args_sig).union(set(args_bkg)) != set([v for v in args_pdf[2:]]):
            raise AssertionError("Argument mismatch! signal and background pdfs do not contain all parameters of full pdf")

        self._pdf = [pdf, signal, background]
        self._startparams = startparams

    def __fit_mass(self, X):
        # Optimizing mass pdf
        print("EML mass fit...")
        mc = cost.ExtendedUnbinnedNLL(X, self._pdf[0])
        m = iminuit.Minuit(mc, **self._startparams)
        m.print_level = 2
        m.migrad()

        assert m.accurate, "Minimization did not converge"
        assert m.valid, "Invalid minimum"
        return m.values

    def __calculate_sweights(self, mass, fitresult):
        import sweights
        print("Calculating sweights...")

        signalvars = {v : fitresult[v] for v in self._pdf[1].__code__.co_varnames[1:self._pdf[1].__code__.co_argcount]}
        bkgvars    = {v : fitresult[v] for v in self._pdf[2].__code__.co_varnames[1:self._pdf[2].__code__.co_argcount]}

        sweighter = sweights.SWeight(data          = np.array(mass),
                                     pdfs          = [lambda x : self._pdf[1](x, **signalvars),
                                                      lambda x : self._pdf[2](x, **bkgvars)],
                                     yields        = [fitresult["Nsig"], fitresult["Nbkg"]],
                                     discvarranges = (self.mass_range,),
                                     method        = "summation",
                                     verbose       = True,
                                     compnames     = ["Nsig", "Nbkg"])

        return sweighter.get_weight(0, mass), sweighter.get_weight(1, mass)

    def __call__(self):
        """ Generates toy data for all components and returns merged pandas DataFrame of all data

            :return: Toy data
            :return type: pandas.DataFrame
        """
        datasets = []

        assert len(self._mass_distributions) == len(self._toy_tag_generators) == len(self._toy_tag_configs)

        for i, toy_generator in enumerate(self._toy_tag_generators):
            print("Generating component", i, "...")
            args   = self._toy_tag_configs[i][0]
            kwargs = self._toy_tag_configs[i][1]
            if len(args) > 0:
                N = args[0]
            elif "N" in kwargs:
                N = kwargs["N"]
            datasets.append(toy_generator(*args, **kwargs))
            datasets[-1]["MASS"] = self._mass_distributions[i](N)
            datasets[-1]["CATEGORY"] = i

        df = pd.concat(datasets)
        df = df.sample(frac=1)

        df.reset_index(drop=True, inplace=True)

        if self._pdf is not None:
            result = self.__fit_mass(df.MASS)
            weights = self.__calculate_sweights(df.MASS, result)
            df["WEIGHT"] = weights[0]
            df["WEIGHT_BKG"] = weights[1]

        df.OSC.replace(np.nan, False)
        df.OSC = df.OSC.astype(bool)
        df = df.replace(np.nan, 0)

        df["eventNumber"] = np.arange(len(df))

        return df
