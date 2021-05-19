from collections import defaultdict
import numpy as np
import pandas as pd
import specs
from math import exp, log, log2

def utility(x, alpha=1.45):
    return (x**(1-alpha) - 1)/(1-alpha) if x != 0 else 0

def dynamic_update(state, policy, spec: specs.ModelSpec):
    """
    Return updated state based on model specification.
    @p state takes the form of a dictionary containing values for state variables
    """
    # unpack some state vars
    next_state = dict()
    next_state['mu'], next_state['savings_rate'] = policy[0], policy[1]

    # scale for numerical stability
    if spec.do_stability_adjustments:
        state['labor'] *= spec.sc_labor
        state['emissions'] *= spec.sc_emissions
        state['welfare_obj'] *= spec.sc_obj
        state['capital'] *= spec.sc_capital
        state['consumption'] *= spec.sc_consump


    # exogenous updates
    next_state['time'] = state['time'] + 1
    next_state['exog_forcing'] = spec.f0 + min(spec.f1-spec.f0, (spec.f1-spec.f0)*next_state['time']/spec.tforce)
    next_state['labor'] = state['labor'] * (spec.asymp_labor/state['labor'])**spec.labor_growth
    next_state['A'] = state['A'] / (1 - spec.g_A * exp(-spec.delta_A * 5 * (state['time'])))
    next_state['sigma'] = (state['sigma']
                            * exp(
                                -spec.g_sigma
                                * (((1-spec.delta_sigma)**spec.timestep) ** (state['time']) * spec.timestep)
                            ))
    next_state['land_emissions'] = spec.init_land_emissions * (1-spec.delta_land_emissions)**next_state['time']

    # endogenous updates
    next_state['capital'] = (1-spec.delta)*state['capital'] + state['damage_coeff']*state['Y']*state['savings_rate']
    next_state['Y'] = next_state['A'] * next_state['capital']**spec.gamma * (next_state['labor']/spec.labor_discount)**(1-spec.gamma)
    next_state['emissions'] = next_state['sigma']*(1-next_state['mu'])*next_state['Y'] + next_state['land_emissions']
    next_state['stock_carbon'] = spec.phi_star*state['stock_carbon'] + state['emissions']

    if spec.type == specs.ModelTypes.SICE_GOL:
        next_state['forcing'] = spec.CO2_forcing_coeff * log2(next_state['stock_carbon']/spec.atmospheric_CO2_1750) + next_state['exog_forcing']
        next_state['temp'] = spec.forcing_temp_coeff * next_state['forcing']
    elif spec.type == specs.ModelTypes.SICE:
        next_state['temp'] = spec.eta_0_star + spec.eta_1_star*state['temp'] + spec.eta_2_star*log(next_state['stock_carbon'])

    next_psi = spec.p_b * (1-spec.delta_pb)**(next_state['time']) * next_state['sigma'] / (1000*spec.theta_2)
    next_omega = next_psi * next_state['mu']**spec.theta
    next_state['damage_coeff'] = (1-next_omega) / (1 + spec.xi_star * next_state['temp']**2)
    
    next_net_output = next_state['damage_coeff'] * next_state['Y']
    next_state['consumption'] = next_net_output * (1-next_state['savings_rate'])

    # labor discount doesn't affect optimization problem but is consistent with Ikefuji et. al
    next_state['welfare_obj'] = (state['welfare_obj'] 
                                    + next_state['labor']
                                    * utility(spec.labor_discount * next_state['consumption'] / next_state['labor'], alpha=spec.alpha)
                                    / (1+spec.rho)**next_state['time'])


    # numerical scaling
    if spec.do_stability_adjustments:
        next_state['labor'] /= spec.sc_labor
        next_state['emissions'] /= spec.sc_emissions
        next_state['welfare_obj'] /= spec.sc_obj
        next_state['capital'] /= spec.sc_capital
        next_state['consumption'] /= spec.sc_consump
    
    return next_state

def create_init_state(values, spec: specs.ModelSpec):
    """
    Create the initial state inherited from the 5 year period PRIOR to the first period.
    """
    init_state = {
        'time': 0.,
        'welfare_obj': 0.,
        'mu': 0.03,
        'labor': 7403,
        'A': 5.115,
        'sigma': 0.3503,
        'capital': 223, # from Ikefuji
        'stock_carbon': 851.,
        'land_emissions': spec.init_land_emissions,
        'temp': 0.85, # from Ikefuji
        'savings_rate': values[0],
    }
    init_state['Y'] = init_state['A'] * init_state['capital']**spec.gamma * (init_state['labor']/spec.labor_discount)**(1-spec.gamma)
    
    psi = spec.p_b * init_state['sigma'] / (1000*spec.theta_2)
    init_state['damage_coeff'] = (1 - psi * init_state['mu']**spec.theta)/ (1 + spec.xi_star * init_state['temp']**2)
    init_state['emissions'] = init_state['sigma']*(1-init_state['mu'])*init_state['Y'] + init_state['land_emissions']
    init_state['consumption'] = init_state['damage_coeff'] * init_state['Y'] * (1-init_state['savings_rate'])
    
    return init_state

def reshape_policies(policies):
    N = len(policies)
    assert N % 2 == 0

    return policies.reshape(2,N//2).T


def simulate(policies, init_state, spec: specs.ModelSpec, store=False):
    """
    Run a full simulation of climate and economic activity given a sequence of policies.
    @p policies is assumed to generate policies like:
        [[mu_1, savings_rate_1],
         [mu_2, savings_rate_2],
          ...
         [mu_N, savings_rate_N]]
    """
    state = init_state
    N = spec.num_steps
    assert len(policies) == N # make sure number of policies coincides with number of iterations

    for policy in policies:
        # may want to save intermediate states in the future
        state = dynamic_update(state, policy, spec)
        yield state

def prepare_input(input_values, spec):
    # splice input
    init_values = input_values[:1]
    policies = input_values[1:]
    
    # reformat to fit in simulation
    init_state = create_init_state(init_values, spec)
    policies = reshape_policies(policies)

    return init_state, policies


def save_simulation(input_values, spec):
    init_state, policies = prepare_input(input_values, spec)
    simulation = defaultdict(list)

    for state in simulate(policies, init_state, spec):
        for state_var, value in state.items():
            simulation[state_var].append(value)
    
    df = pd.DataFrame(simulation)
    return df


def objective(input_values, spec):
    """
    Objective function producing finite horizon welfare estimate from
    model specification and inputs
    """
    # prepare input for simulation
    init_state, policies = prepare_input(input_values, spec)

    for state in simulate(policies, init_state, spec): final_state = state
    return final_state['welfare_obj']
