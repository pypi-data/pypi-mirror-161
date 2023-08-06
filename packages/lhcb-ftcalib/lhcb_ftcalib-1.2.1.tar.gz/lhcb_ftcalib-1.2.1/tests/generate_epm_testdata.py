import os
import sys
import uproot
import numpy as np

import lhcb_ftcalib as ft


def generate_reference_data(N):
    if not os.path.exists("tests/epm_reference_data"):
        os.mkdir("tests/epm_reference_data")

    with uproot.recreate("tests/epm_reference_data/reference.root") as File:
        poly1_MISTAG = ft.PolynomialCalibration(2, ft.link.mistag)
        poly2_MISTAG = ft.PolynomialCalibration(3, ft.link.mistag)
        poly1_LOGIT  = ft.PolynomialCalibration(2, ft.link.logit)

        params_poly1 = [[0, 0, 0, 0],
                        [0.01, 0.3, 0.01, 0],
                        [0.01, -0.05, 0.01, 0.1]]
        params_poly2 = [[0, 0, 0, 0, 0, 0],
                        [0.01, 0.3, -0.03, 0.01, 0, 0.04],
                        [0.01, -0.05, -0.3, 0.01, 0.1, 0.8]]

        generator = ft.toy_tagger.ToyDataGenerator(0, 20)

        File["BU_POLY1_MISTAG"] = generator(
            N            = N,
            func         = poly1_MISTAG,
            params       = params_poly1,
            osc          = False,
            DM           = 0,
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BD_POLY1_MISTAG"] = generator(
            N            = N,
            func         = poly1_MISTAG,
            params       = params_poly1,
            osc          = True,
            DM           = 0.51,  # EPM value
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BS_POLY1_MISTAG"] = generator(
            N            = N,
            func         = poly1_MISTAG,
            params       = params_poly1,
            osc          = True,
            DM           = 17.761,  # EPM value
            DG           = 0.0913,  # EPM value
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BD_POLY1_LOGIT"] = generator(
            N            = N,
            func         = poly1_LOGIT,
            params       = params_poly1,
            osc          = True,
            DM           = 0.51,  # EPM value
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BD_POLY2_MISTAG"] = generator(
            N            = N,
            func         = poly2_MISTAG,
            params       = params_poly2,
            osc          = True,
            DM           = 0.51,  # EPM value
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BD_POLY1_MISTAG_HUGETAUERR"] = generator(
            N            = N,
            func         = poly1_MISTAG,
            params       = [[0.1, 0, -0.1, 0]],
            osc          = True,
            DM           = 0.51,  # EPM value
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            resolution_scale = 0.3,
            tagger_types = ["OSMuon"],
            tag_effs     = [0.99])

        mass_range = [5000, 6000]

        def signal_pdf(X, mu, sigma):
            # Normalized gaussian distribution
            return ft.toy.mass_peak(X, mu, sigma)

        def background_pdf(X, E):
            # Background component normalized to mass range
            return np.exp(-E * X) * E / (np.exp(-E * mass_range[0]) - np.exp(-E * mass_range[1]))

        def mass_pdf_EML(X, Nsig, Nbkg, mu, sigma, E):
            # Full mass pdf according to requirements of ExtendedUnbinnedNLL of iminuit
            exponential = Nbkg * background_pdf(X, E)
            signal = Nsig * signal_pdf(X, mu, sigma)
            return Nsig + Nbkg, (exponential + signal)

        gen = ft.toy.MultiComponentToyDataGenerator(mass_range, [0, 20])

        # Combinatorial background
        nbkg = 10000
        nsig = 30000
        gen.add_component(ft.toy.exponential_background, e=0.0003)
        gen.configure_component(N                = nbkg,
                                func             = poly1_MISTAG,
                                params           = [ [0, 0.1, 0.2, -0.1] ],
                                osc              = True,
                                DM               = 0,
                                lifetime         = 0.8,
                                tagger_types     = ["OSKaon"],
                                tag_effs         = [0.6],
                                resolution_scale = 8e-2)

        # Signal
        gen.add_component(ft.toy.mass_peak, mu=5279, sigma=15)
        gen.configure_component(N                = nsig,
                                func             = poly1_MISTAG,
                                params           = [[0, 0.1, 0.2, -0.1]],
                                osc              = True,
                                DM               = 0.5065,
                                lifetime         = 1.52,
                                tagger_types     = ["OSKaon"],
                                tag_effs         = [0.9])

        gen.set_mass_pdf(mass_pdf_EML, signal_pdf, background_pdf, Nsig=nsig, Nbkg=nbkg, mu=5279, sigma=15, E=0.00031)

        File["BD_POLY1_MISTAG_SWEIGHTS"] = gen()


if __name__ == "__main__":
    generate_reference_data(int(sys.argv[1]))
