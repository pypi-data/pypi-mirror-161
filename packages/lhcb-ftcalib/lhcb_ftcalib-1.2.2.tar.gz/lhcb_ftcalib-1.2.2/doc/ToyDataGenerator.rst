Toy Data Generator
==================

The toy data generator module generates the flavour ground truth of 
a simulated measurement, i.e. the production and detection flavour
as well as pairs of distributions for the raw and calibrated mistag given
a calibration function with custom parameters. Those parameters can be 
reproduced by calibrating the raw mistag distribution.

The following data are generated:

* **FLAV_PROD**: The true production flavour
* **FLAV_DECAY**: The true decay flavour
* **FLAV_PRED**: The predicted production flavour given the decay flavour and the decay time
* **TOYX_DEC**: The tagging decisions of toy tagger Nr. X
* **TOYX_ETA**: The raw mistag distribution of toy tagger Nr. X
* **TOYX_OMEGA**: The calibrated mistag distribution of toy tagger Nr. X
* **TRUETAU**: If osc=True: The generated true decay time distribution
* **TAU**: If osc=True: The "reconstructed" decay time distribution
* **TAUERR**: If osc=True: The reconstructed decay time uncertainty

* **OSC**: If osc=True: 1 if B meson of entry has oscillated, else 0
* **eventNumber**: An event counter

In addition, the MultiComponentToyDataGenerator generates

* **MASS**: Invariant mass distribution
* **CATEGORY**: Index of generated component starting at 0
* **WEIGHT**: If mass pdf was configured: sWeights
* **WEIGHT_BKG**: If mass pdf was configured: Background sWeights


.. autoclass:: lhcb_ftcalib.toy.ToyDataGenerator
   :members:
   :special-members: __call__


Example use: Basic MC-like toy data
-----------------------------------

.. code-block:: python

   import lhcb_ftcalib as ft

   gen = ft.toy.ToyDataGenerator(0, 20)
   df = gen(
    N            = 50000,
    func         = ft.PolynomialCalibration(2, ft.link.logit),
    params       = [[0, 1, 0, 1], [0.1, 0.9, -0.1, 1.1]],
    osc          = True,
    tagger_types = ["OSKaon", "SSPion"],
    lifetime     = 1.52,  # ps
    DM           = 0.5065,  # ps^-1
    DG           = 0,
    Aprod        = 0.01,
    tag_effs     = [0.4, 0.8],
    acceptance   = "arctan"
   )

Example use: MC-like toy data with CP violation
-----------------------------------------------
CP violation is simulated by sampling the decay time distribution from the time dependent decay rate
:math:`\Gamma(P_\pm\to f)\propto\exp(-\Gamma t)(\mp S\sin(\Delta m t) \pm C\sin(\Delta m t) + A_{\Delta\Gamma}\sinh(\Delta\Gamma t/2) + \cosh(\Delta\Gamma t/2))`
and by adjusting the TRUEID (i.e. the "PROD_FLAV") so that the time dependent CP asymmetry is centered around :math:`A(t)=0`. At the moment,
CP violation is only supported for decays to CP eigenstates.

.. code-block:: python

   import lhcb_ftcalib as ft

   gen = ft.toy.ToyDataGenerator(0, 20)
   df = gen(
    N            = 50000,
    func         = ft.PolynomialCalibration(2, ft.link.logit),
    params       = [[0, 1, 0, 1], [0.1, 0.9, -0.1, 1.1]],
    osc          = True,
    tagger_types = ["OSKaon", "SSPion"],
    lifetime     = 1.52,  # ps
    DM           = 0.5065,  # ps^-1
    DG           = 0,
    tag_effs     = [0.4, 0.8],
    acceptance   = "sigmoid",
    CPV = {
        S : 0.7,  # ~sin(2β)
        C : 0,    # C
        A : 0,    # A_ΔΓ
    })



.. autoclass:: lhcb_ftcalib.toy.MultiComponentToyDataGenerator
   :members:
   :special-members: __call__


Example use
-----------

.. code-block:: python

   import lhcb_ftcalib as ft
   import uproot

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
    gen.add_component(ft.toy.exponential_background, e=0.0003)
    gen.configure_component(N                = 150000,
                            func             = func,
                            params           = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0] ],
                            osc              = True,
                            DM               = 0,
                            lifetime         = 1.0,
                            tagger_types     = ["OSElectron", "OSElectron", "OSElectron"],
                            tag_effs         = [0.6, 0.6, 0.6],
                            resolution_scale = 8e-2)

    # Signal background
    gen.add_component(ft.toy.mass_peak, mu=5279, sigma=15)
    gen.configure_component(N                = 15000,
                            func             = func,
                            params           = [[0, 0, 0, 0], [0, 0.1, 0, -0.1], [0.1, 0.1, 0.055, 0] ],
                            osc              = True,
                            DM               = 0.5065,
                            tagger_types     = ["OSKaon", "OSElectron", "SSPion"],
                            tag_effs         = [0.8, 0.8, 0.8])

    # Set mass pdfs and starting parameters
    gen.set_mass_pdf(mass_pdf_EML, signal_pdf, background_pdf, Nsig=15000, Nbkg=150000, mu=5270, sigma=20, E=0.001)

    # generate toys
    data = gen()

    with uproot.recreate("FakeData.root") as FILE:
        FILE["DecayTree"] = data
