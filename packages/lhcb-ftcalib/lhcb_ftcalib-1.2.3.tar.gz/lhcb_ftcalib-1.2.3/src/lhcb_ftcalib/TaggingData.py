import numpy as np
import pandas as pd
import functools

from .printing import raise_error, raise_warning
from .resolution_model import mixing_asymmetry
from . import constants


class FTCWarning:
    def __init__(self, warntype, msg):
        self.warntype = warntype
        self.msg = msg

    def __str__(self):
        return f"\033[33m\033[1m[{self.warntype}]\033[0m {self.msg}"


class TaggingData:
    r"""
    TaggingData
    Type for computing and keeping track of tagging data and performance

    :param eta_data: Uncalibrated mistags
    :type eta_data: list
    :param dec_data: Uncalibrated tagging decisions
    :type dec_data: list
    :param ID: B meson particle IDs
    :type ID: list
    :param tau: Decay time in picoseconds
    :type tau: list
    :param tauerr: Decay time uncertainty in picoseconds
    :type tauerr: list
    :param weights: Per-event weights
    :type weights: list
    """

    def __init__(self, eta_data, dec_data, ID, tau, tauerr, weights, selection):
        def get_absid(ID):
            ids = np.unique(np.abs(ID))
            ids = list(ids[ids != 0])
            raise_error(len(ids) > 0, f"There are no nonzero particle IDs in the ID branch {ids}")
            raise_error(len(ids) == 1, f"There are too many particle IDs in the ID branch: {ids}")
            raise_warning(ids[0] in (511, 521, 531), f"Particle ID {ids[0]} does not belong to a Bu, Bd or Bs meson")
            return ids[0]

        self._absID = get_absid(np.array(ID))
        self._full_data = pd.DataFrame({
            "eta" : eta_data,
            "dec" : dec_data,
            "decay_flav" : ID // self._absID,
            "selected"   : selection }
        )
        self._full_data.decay_flav = self._full_data.decay_flav.astype(np.int32)
        if tau is not None:
            self._full_data["tau"] = tau
            self._has_tau = True
        else:
            self._has_tau = False

        if tauerr is not None:
            self._full_data["tau_err"] = tauerr
            self._has_tauerr = True
        else:
            self._has_tauerr = False

        if weights is None:
            self._full_data.eval("weight = 1", inplace=True)
        else:
            self._full_data["weight"] = weights

        self._can_propagate_error = False

        self._full_data.eval("""overflow   = eta > 0.5
                                underflow  = eta < 0
                                tagged     = (dec != 0)
                                tagged_sel = tagged & selected
                                prod_flav  = decay_flav""", inplace=True)

        # Initialize tagging data subset
        self._tagdata = self._full_data[self._full_data.tagged_sel].copy()  # Copy needed, otherwise view
        self._tagdata.reset_index(inplace=True, drop=False)

        self._tagdata.eval("""correct_tags = (dec == prod_flav)
                              wrong_tags   = ~correct_tags""", inplace=True)

        self._is_calibrated = False

    def is_calibrated(self):
        """ Returns True if calibrated statistics are available """
        return self._is_calibrated

    @property
    def N(self):
        """ Total number of events """
        return len(self._full_data)

    @property
    def Ns(self):
        """ Number of selected events """
        return self._full_data.selected.sum()

    @property
    def Nt(self):
        r""" Number of tagged events :math:`N_t = N_\mathrm{tagged} - N_\mathrm{overflow}`.
            Events with mistag > 0.5 are overflow events and are not tagged by convention.
        """
        return self._full_data.tagged.sum() - (self._full_data.eta > 0.5).sum()

    @property
    def Nts(self):
        """ Number of tagged events in selection without overflow """
        return len(self._tagdata) - self._tagdata.overflow.sum()

    @property
    def Nw(self):
        """ Sum of all event weights """
        return np.sum(self._full_data.weight)

    @property
    def Neff(self):
        r""" Effective number of events
            :math:`N_\mathrm{eff}=(\sum_i w_i)^2 / \sum_i w_i^2`
        """
        return self.Nw**2 / np.sum(self._full_data.weight**2)

    @property
    def Nwt(self):
        """ Sum of all event weights of tagged events without overflow event weights """
        return self._full_data.weight[self._full_data.tagged].sum() - self._full_data.weight[self._full_data.overflow].sum()

    @property
    def Nws(self):
        """ Sum of all event weights of selected events """
        return np.sum(self._full_data.weight[self._full_data.selected])

    @property
    def Neffs(self):
        r""" Effective number of events in selection
            :math:`(\sum_i w_i)^2 / \sum_i w_i^2`
        """
        return self.Nws**2 / np.sum(self._full_data.weight[self._full_data.selected]**2)

    @property
    def Nwts(self):
        """ Sum of all event weights of tagged events in selection """
        return np.sum(self._tagdata.weight)

    @property
    def Noverflow(self):
        """ Number of events with raw mistag > 0.5 """
        return self._tagdata.overflow.sum()

    @property
    def cal_Noverflow(self):
        """ Number of events with raw mistag > 0.5 """
        return self._tagdata.cal_overflow.sum()

    @property
    def cal_Nt(self):
        r""" Number of tagged events after the calibration :math:`N_t = N_\mathrm{tagged} - N_\mathrm{overflow}`.
            Events with mistag > 0.5 are overflow events and are not tagged by convention.
        """
        return self._tagdata.ctagged.sum() - self._tagdata.cal_overflow[self._tagdata.ctagged].sum()

    @property
    def cal_Nts(self):
        """ Number of tagged events after calibration in selection without overflow """
        return self._tagdata.ctagged_sel.sum() - self._tagdata.cal_overflow[self._tagdata.ctagged_sel].sum()

    @property
    def cal_Nwt(self):
        """ Sum of all event weights of tagged and calibrated events without overflow event weights """
        N  = self._full_data.weight[self._full_data.ctagged].sum()
        N -= self._full_data.weight[self._full_data.ctagged & self._full_data.cal_overflow].sum()
        return N

    @property
    def cal_Nwts(self):
        """ Sum of all event weights of tagged and calibrated events in selection """
        N  = self._tagdata.weight[self._tagdata.ctagged_sel].sum()
        # N -= self._tagdata.weight[self._tagdata.cal_overflow].sum()
        return N

    @property
    def avg_eta(self):
        r""" Mean mistag
            :math:`\langle\eta\rangle = \displaystyle\frac{\sum_i w_i \eta_i}{\sum_i w_i}`
            whereby the sums run over all tagged and selected events and :math:`w_i` are the event weights.
        """
        return np.average(self._tagdata.eta, weights=self._tagdata.weight)

    def _init_timeinfo(self, mode, DM, DG, resolution_model):
        # Computes flavour impurity for each event. If B oscillation probability
        # is > 50%, production flavour is assumed to be the opposite
        if mode == "Bu":
            self._full_data.eval("osc_dilution = 0", inplace=True)
            self._tagdata.eval("osc_dilution = 0", inplace=True)
            Amix = None
        else:
            Amix = mixing_asymmetry(self._full_data.tau,
                                    DM     = DM,
                                    DG     = DG,
                                    tauerr = self._full_data.tau_err if "tau_err" in self._full_data else None,
                                    a      = 0,
                                    res    = resolution_model)
            self._full_data.loc[:, "osc_dilution"] = 0.5 * (1.0 - np.abs(Amix))
            self._tagdata.loc[:, "osc_dilution"] = np.array(self._full_data.loc[self._full_data.tagged_sel, "osc_dilution"])

        # Update production asymmetry given mixing asymmetry
        # and measures of "tag correctness"
        if mode != "Bu":
            self._full_data.loc[np.sign(Amix) == -1, "prod_flav"] *= -1

            self._tagdata["prod_flav"] = np.array(self._full_data.loc[self._full_data.tagged_sel, "prod_flav"])

            self._tagdata.correct_tags = self._tagdata.dec == self._tagdata.prod_flav
            self._tagdata.wrong_tags   = ~self._tagdata.correct_tags

    def _compute_calibrated_statistics(self, func, params, covariance, accurate):
        warnings = []
        if not accurate:
            warnings.append(FTCWarning("MinimizerWarning", "Minimization did not converge!"))

        self.params.set_calibration_flavour(params, covariance)

        self._full_data.eval("omega = 0.5", inplace=True)
        self.func_ref = func

        # Convert to delta parameter convention, then evaluate using p's only
        if constants.ignore_mistag_asymmetry_for_apply:
            self._full_data.loc[self._full_data.tagged, "omega"] = self.func_ref.eval_averaged(self.params.params_average,
                                                                                               eta = self._full_data.eta[self._full_data.tagged])
        else:
            self._full_data.loc[self._full_data.tagged, "omega"] = self.func_ref.eval(self.params.params_flavour, eta = self._full_data.eta[self._full_data.tagged],
                                                                                      dec = self._full_data.prod_flav[self._full_data.tagged])
        self._full_data.loc[self._full_data.tagged, "omega_err"] = 0
        if constants.calculate_omegaerr:
            # Uncertainties have to be calculated in non-averaged representation, since the siplification of the model has a large impact on the uncertainties
            if constants.ignore_mistag_asymmetry_for_apply:
                self._full_data.loc[self._full_data.tagged, "omega_err"] = self.func_ref.eval_averaged_uncertainty(self.params.params_average, self.params.covariance_average,
                                                                                                                   eta = self._full_data.eta[self._full_data.tagged])
            else:
                self._full_data.loc[self._full_data.tagged, "omega_err"] = self.func_ref.eval_uncertainty(self.params.params_flavour, self.params.covariance_flavour,
                                                                                                          eta = self._full_data.eta[self._full_data.tagged],
                                                                                                          dec = self._full_data.prod_flav[self._full_data.tagged])

        self._full_data.eval("cal_overflow = omega > 0.5", inplace=True)
        nOverflow  = self._full_data.cal_overflow.sum()
        nUnderflow = (self._full_data.omega < 0).sum()
        if nOverflow > 0:
            warnings.append(FTCWarning("OverflowWarning", f"{nOverflow} calibrated mistag values > 0.5"))
        if nUnderflow > 0:
            warnings.append(FTCWarning("UnderflowWarning", f"{nUnderflow} calibrated mistag values < 0"))

        # self._full_data.loc[self._full_data.cal_overflow > 0.5, "cdec"] = 0

        self._full_data.eval("ctagged = (omega < 0.5)", inplace=True)
        self._full_data.eval("cdec = dec", inplace=True)
        self._full_data.loc[~self._full_data.ctagged, "cdec"] = 0
        self._full_data.eval("ctagged_sel = ctagged & selected", inplace=True)

        self._tagdata["omega"]        = np.array(self._full_data.omega[self._full_data.tagged_sel])
        self._tagdata["cdec"]         = np.array(self._full_data.cdec[self._full_data.tagged_sel])
        self._tagdata["ctagged"]      = np.array(self._full_data.ctagged[self._full_data.tagged_sel])
        self._tagdata["ctagged_sel"]  = np.array(self._full_data.ctagged_sel[self._full_data.tagged_sel])
        self._tagdata["cal_overflow"] = np.array(self._full_data.cal_overflow[self._full_data.tagged_sel])
        self._tagdata["omega_err"]    = np.array(self._full_data.omega_err[self._full_data.tagged_sel])

        self.tagging_efficiency.cache_clear()
        self.dilution_squared.cache_clear()
        self.mistag_rate.cache_clear()
        self.tagging_power.cache_clear()
        self.effective_mistag.cache_clear()

        self._is_calibrated = True

        return warnings

    def _compute_combination_statistics(self, eta, gradients, covariances):
        warnings = []
        self._full_data_gradients = gradients
        self._combination_covariance = covariances
        self._can_propagate_error = True

        self._full_data.eval("eta = 0.5", inplace=True)

        self._full_data.loc[self._full_data.tagged, "eta"] = eta[self._full_data.tagged]
        self._full_data.loc[self._full_data.tagged, "eta_err"] = 0

        cov = self._combination_covariance
        cal_error = np.array([np.sqrt(g @ cov @ g.T).item() for g in self._full_data_gradients])
        self._full_data.loc[self._full_data.tagged, "eta_err"] = cal_error[self._full_data.tagged]

        self._full_data.eval("cal_overflow = eta > 0.5", inplace=True)
        nOverflow  = self._full_data.cal_overflow.sum()
        nUnderflow = (self._full_data.eta < 0).sum()
        if nOverflow > 0:
            warnings.append(FTCWarning("OverflowWarning", f"{nOverflow} calibrated mistag values > 0.5"))
        if nUnderflow > 0:
            warnings.append(FTCWarning("UnderflowWarning", f"{nUnderflow} calibrated mistag values < 0"))

        self._tagdata["eta"]     = np.array(self._full_data.eta[self._full_data.tagged_sel])
        self._tagdata["eta_err"] = np.array(self._full_data.eta_err[self._full_data.tagged_sel])

        self.tagging_efficiency.cache_clear()
        self.dilution_squared.cache_clear()
        self.mistag_rate.cache_clear()
        self.tagging_power.cache_clear()
        self.effective_mistag.cache_clear()

        return warnings

    @functools.lru_cache(maxsize=4)
    def tagging_efficiency(self, calibrated, inselection=True):
        r"""
        Computes the fraction of tagged events
        :math:`\epsilon_{\mathrm{tag}}=\displaystyle\frac{N_t}{N}\pm\sqrt{\frac{N_t (N - N_t)}{N_\mathrm{eff}}}`

        :param calibrated: Whether to use calibrated statistics
        :type calibrated: bool
        :param inselection: Whether to only use events in selection
        :type inselection: bool

        :return: tuple(Tagging efficiency, Tagging efficiency uncertainty)
        :return type: tuple
        """
        if calibrated:
            if not self._is_calibrated:
                return None, None
            if inselection:
                N, Nt, Neff = self.Nws, self.cal_Nwts, self.Neffs
            else:
                N, Nt, Neff = self.Nw, self.cal_Nwt, self.Neff
        else:
            if inselection:
                N, Nt, Neff = self.Nws, self.Nwts, self.Neffs
            else:
                N, Nt, Neff = self.Nw, self.Nwt, self.Neff

        rate     = Nt / N
        untagged = N - Nt
        return rate, np.sqrt(Nt * untagged / Neff) / N

    @functools.lru_cache(maxsize=4)
    def dilution_squared(self, calibrated, inselection=True):
        r""" Returns the mean squared flavour tagging dilution, i.e. the tagging power of tagged events.

        :param calibrated: Whether to use calibrated statistics
        :type calibrated: bool
        :param inselection: Whether to only use events in selection
        :type inselection: bool
        :return: tuple(:math:`\langle\mathcal{D}^2\rangle`, :math:`\sigma(\langle\mathcal{D}^2\rangle)`, :math:`\sigma^{\mathrm{cal}}(\langle\mathcal{D}^2\rangle)`)
        :return type: tuple

        The expectation value of a power of the flavour tagging dilution is computed
        :math:`\langle\mathcal{D}^n\rangle = \displaystyle\frac{1}{N_{wts}}\sum_{\substack{i, \mathrm{tagged}\\\mathrm{selected}}}^N w_i(1-2\omega(\eta_i,\vec p))^n`

        whereby
        :math:`\displaystyle N_{wts} =\sum_{\substack{i, \mathrm{tagged}\\\mathrm{selected}}}^Nw_i`

        :math:`\displaystyle\sigma(\langle\mathcal{D}^2\rangle)=\sqrt{\frac{\langle\mathcal{D}^4\rangle-\langle\mathcal{D}^2\rangle^2}{N_{wts}-1}}`

        with :math:`\displaystyle\nabla_{\vec{p}}\langle\mathcal{D}^2\rangle= \frac{-4}{N_{wts}}\sum_{\substack{i, \mathrm{tagged}\\\mathrm{selected}}}^N \displaystyle \nabla_{\vec{p}} \omega(\eta_i, \vec p) (1-2\omega(\eta_i)) w_i`,

        where :math:`\omega` is the calibration function and :math:`\vec p` are its parameters follows the mean squared dilution error

        :math:`\sigma^{\mathrm{cal}}(\langle\mathcal{D}^2\rangle)=\sqrt{\nabla_{\vec{p}}\langle\mathcal{D}^2\rangle\cdot C \cdot\nabla_{\vec{p}}\langle\mathcal{D}^2\rangle^\top}`
        """
        if calibrated:
            if inselection:
                D = np.array(1 - 2 * self._tagdata.omega)
                mean_D_sq = np.sum(D**2 * self._tagdata.weight) / self.cal_Nwts
                mean_D_4  = np.sum(D**4 * self._tagdata.weight) / self.cal_Nwts

                if constants.ignore_mistag_asymmetry_for_apply:
                    grad_calib = self.func_ref.gradient_averaged(self.params.params_average, self._tagdata.eta)
                    grad_mean_D_sq = -4 * np.sum(grad_calib * D * np.array(self._tagdata.weight), axis=1) / self.cal_Nwts
                    cal_error = np.sqrt(grad_mean_D_sq @ self.params.covariance_average @ grad_mean_D_sq.T)
                else:
                    grad_calib = self.func_ref.gradient(self.params.params_flavour, self._tagdata.eta, self._tagdata.dec)
                    grad_mean_D_sq = -4 * np.sum(grad_calib * D * np.array(self._tagdata.weight), axis=1) / self.cal_Nwts
                    cal_error = np.sqrt(grad_mean_D_sq @ self.params.covariance_flavour @ grad_mean_D_sq.T)
            else:
                D = np.array(1 - 2 * self._full_data[self._full_data.tagged].omega)
                mean_D_sq = np.sum(D**2 * self._full_data[self._full_data.tagged].weight) / self.cal_Nwt
                mean_D_4  = np.sum(D**4 * self._full_data[self._full_data.tagged].weight) / self.cal_Nwt

                if constants.ignore_mistag_asymmetry_for_apply:
                    grad_calib = self.func_ref.gradient_averaged(self.params.params_average, self._full_data[self._full_data.tagged].eta)
                    grad_mean_D_sq = -4 * np.sum(grad_calib * D * np.array(self._full_data[self._full_data.tagged].weight), axis=1) / self.cal_Nwt
                    cal_error = np.sqrt(grad_mean_D_sq @ self.params.covariance_average @ grad_mean_D_sq.T)
                else:
                    grad_calib = self.func_ref.gradient(self.params.params_flavour, self._full_data[self._full_data.tagged].eta, self._full_data[self._full_data.tagged].dec)
                    grad_mean_D_sq = -4 * np.sum(grad_calib * D * np.array(self._full_data[self._full_data.tagged].weight), axis=1) / self.cal_Nwt
                    cal_error = np.sqrt(grad_mean_D_sq @ self.params.covariance_flavour @ grad_mean_D_sq.T)
        elif constants.propagate_errors and self._can_propagate_error:
            if inselection:
                D = np.array(1 - 2 * self._tagdata.eta)
                mean_D_sq = np.sum(D**2 * self._tagdata.weight) / self.Nwts
                mean_D_4  = np.sum(D**4 * self._tagdata.weight) / self.Nwts

                # Propagate errors of mean dilution squared
                grad_calib = self._full_data_gradients[self._full_data.tagged_sel]
                grad_mean_D_sq  = -4 * np.einsum("ijk,i", grad_calib, D * self._tagdata.weight) / self.Nwts
                cal_error = np.sqrt(grad_mean_D_sq @ self._combination_covariance @ grad_mean_D_sq.T).item()
            else:
                D = np.array(1 - 2 * self._full_data[self._full_data.tagged].eta)
                mean_D_sq = np.sum(D**2 * self._full_data[self._full_data.tagged].weight) / self.Nwt
                mean_D_4  = np.sum(D**4 * self._full_data[self._full_data.tagged].weight) / self.Nwt

                # Propagate errors of mean dilution squared
                grad_calib = self._full_data_gradients[self._full_data.tagged]
                grad_mean_D_sq  = -4 * np.einsum("ijk,i", grad_calib, D * self._full_data[self._full_data.tagged].weight) / self.Nwt
                cal_error = np.sqrt(grad_mean_D_sq @ self._combination_covariance @ grad_mean_D_sq.T).item()
        else:
            if inselection:
                D = np.array(1 - 2 * self._tagdata.eta)
                mean_D_sq = np.sum(D**2 * self._tagdata.weight) / self.Nwts
                mean_D_4  = np.sum(D**4 * self._tagdata.weight) / self.Nwts
            else:
                D = np.array(1 - 2 * self._full_data[self._full_data.tagged].eta)
                mean_D_sq = np.sum(D**2 * self._full_data[self._full_data.tagged].weight) / self.Nwt
                mean_D_4  = np.sum(D**4 * self._full_data[self._full_data.tagged].weight) / self.Nwt
            cal_error = None

        return mean_D_sq, np.sqrt((mean_D_4 - mean_D_sq**2) / (self.Nwt - 1)), cal_error

    @functools.lru_cache(maxsize=4)
    def tagging_power(self, calibrated, inselection=True):
        r"""
        Returns the effective tagging efficiency
        :math:`\epsilon_{\mathrm{tag,eff}}=\displaystyle\epsilon_\mathrm{tag}\langle\mathcal{D}^2\rangle`

        :param calibrated: Whether to use calibrated statistics
        :type calibrated: bool
        :param inselection: Whether to only use events in selection
        :type inselection: bool

        :return: tuple(:math:`\epsilon_{\mathrm{tag,eff}},\sigma(\epsilon_{\mathrm{tag,eff}})`)
        :return type: tuple
        """
        D_sq, D_sq_err, D_sq_calerr = self.dilution_squared(calibrated, inselection)
        tageff, tageff_err = self.tagging_efficiency(calibrated, inselection)

        if D_sq_calerr:
            return D_sq * tageff, np.sqrt(tageff**2 * D_sq_err**2 + D_sq**2 * tageff_err**2), tageff * D_sq_calerr
        else:
            return D_sq * tageff, np.sqrt(tageff**2 * D_sq_err**2 + D_sq**2 * tageff_err**2)

    @functools.lru_cache(maxsize=4)
    def mistag_rate(self, calibrated, inselection=True):
        r""" Returns Mean mistag rate of selected statistics with binomial uncertainty

            :math:`\langle\omega\rangle=\displaystyle\frac{N_\mathrm{wrong}}{N_\mathrm{wrong}+N_\mathrm{correct}}\pm\frac{1}{N_{wts}}\sqrt{\frac{N_\mathrm{correct}N_\mathrm{wrong}}{N_{wts}}}`

            whereby :math:`N_\mathrm{correct}`(:math:`N_\mathrm{wrong}`) is the sum of weights of events in selection where the tag decision does (not)
            match the predicted production flavour and :math:`N_{wts}` is the sum of weights of all tagged events in selection.

            :param calibrated: Whether to use calibrated mistag and decisions
            :type calibrated: bool
            :param inselection: Whether to only use events in selection
            :type inselection: bool
            :return: Mistag rate and uncertainty
            :rtype: tuple
        """
        if calibrated:
            if not self._is_calibrated:
                return None, None

            if inselection:
                Nright = self._tagdata.weight[self._tagdata.ctagged_sel & self._tagdata.correct_tags].sum()
                Nwrong = self._tagdata.weight[self._tagdata.ctagged_sel & self._tagdata.wrong_tags].sum()
                Nweighted = self.cal_Nwts
            else:
                return -999, -999  # WIP
        else:
            if inselection:
                Nright = self._tagdata.weight[self._tagdata.correct_tags].sum()
                Nwrong = self._tagdata.weight[self._tagdata.wrong_tags].sum()
                Nweighted = self.Nwts
            else:
                return -999, -999  # WIP

        return Nwrong / (Nwrong + Nright), np.sqrt(Nright * Nwrong / Nweighted) / Nweighted

    @functools.lru_cache(maxsize=4)
    def effective_mistag(self, calibrated, inselection=True):
        r""" Returns the effective mistag :math:`\omega^{\text{eff}}`

             From :math:`\langle\mathcal{D}^2\rangle=(1-2\omega^{\text{eff}})^2`

             follows

             :math:`\omega^{\text{eff}} = \displaystyle\frac{1}{2}\left(1-\sqrt{\langle\mathcal{D}^2\rangle}\right)
             \pm\frac{\sigma(\langle\mathcal{D}^2\rangle)}{4\sqrt{\langle\mathcal{D}^2\rangle}}
             \pm\frac{\sigma^\mathrm{cal}(\langle\mathcal{D}^2\rangle)}{4\sqrt{\langle\mathcal{D}^2\rangle}}`

             :param calibrated: Whether to use calibrated statistics
             :type calibrated: bool
             :param inselection: Whether to only use events in selection
             :type inselection: bool

             :return: Tuple of effective mistag, effective mistag uncertatiny, effective mistag calibration uncvertainty
             :return type: tuple
        """

        D_sq, D_sq_err, D_sq_calerr = self.dilution_squared(calibrated, inselection)

        if D_sq_calerr:
            return 0.5 * (1 - np.sqrt(D_sq)), D_sq_err / (4 * np.sqrt(D_sq)), D_sq_calerr / (4 * np.sqrt(D_sq))
        else:
            return 0.5 * (1 - np.sqrt(D_sq)), D_sq_err / (4 * np.sqrt(D_sq))
