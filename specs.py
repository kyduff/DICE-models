import numpy as np
from enum import Enum, auto

INIT_LAND_EMISSIONS = 2.6

class ModelTypes(Enum):
    SICE = auto()
    SICE_GOL = auto()

class ModelSpec():
    """
    Specify parameters for DICE models
    """
    def __init__(self, model_type: ModelTypes = None):
        """
        Parameters are picked to coincide with Ikefuji et. al unless unspecified.
        Then parameters are chosen to coincide with DICE 2016 but conventions
        from Ikefuji et. al are followed whenever possible
        """
        if model_type is None:
            self.type = ModelTypes.SICE_GOL
        else:
            self.type = model_type

        self.timestep = 5. # in years
        self.num_steps = 100 # 500 yr horizon

        # names chosen to coincide with Ikefuji et. al paper
        # NOTE: Ikefuji et. al elect to omit scalings, and their inputs are marked to the 5 yr timestep
        self.xi_star = 0.00265
        self.phi_star = 0.9942
        self.alpha = 1.45
        self.gamma = 0.3
        self.delta = 0.40951 # compounded assuming step size of 5 yrs
        self.rho = 0.077284 # compounded assuming step size of 5 yrs
        self.theta = 2.6

        # conventions from Faulwasser
        self.g_sigma = 0.0152
        self.delta_sigma = 0.001
        self.sigma_discount = 1/3.666 # Ikefuji et. al scale down Nordhaus's sigma
        self.g_A = 0.076
        self.delta_A = 0.005
        self.A_discount = 1/self.timestep # to match Ikefuji et. al
        self.delta_land_emissions = 0.115
        self.init_land_emissions = INIT_LAND_EMISSIONS
        self.theta_2 = 2.6
        self.p_b = 550
        self.delta_pb = 0.025

        # temp model is taken from Nordhaus and mixed with Golosav et. al to eliminate temp inertia
        self.forcing_temp_coeff = 0.842 # from Golosav et. al
        self.CO2_forcing_coeff = 3.6813
        self.f0 = 0.5
        self.f1 = 1.0
        self.tforce = 17.
        self.atmospheric_CO2_1750 = 588.

        # alternate temperature model from Ikefuji et. al
        if self.type == ModelTypes.SICE:
            self.eta_0_star = -2.8672
            self.eta_1_star = 0.8954
            self.eta_2_star = 0.4622

        # exogenous, following convention of DICE 2016
        self.asymp_labor = 11500
        self.labor_growth = 0.134
        self.labor_discount = 1000.

        self.mu_upper_bnd = 1.0 # change to 1.2 to allow negative emissions
        self.mu_lower_bnd = 0.0
        self.savings_rate_upper_bnd = 1.0
        self.savings_rate_lower_bnd = 0.0

        # scalars for numerical stability
        # values taken from Faulwasser
        self.do_stability_adjustments = True
        self.sc_labor = 1e2
        self.sc_emissions = 1e2
        self.sc_obj = 1e4
        self.sc_capital = 1e2
        self.sc_consump = 1e2