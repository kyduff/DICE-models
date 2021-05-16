import time
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.optimize import Bounds, minimize
import simulator
import specs

# Faulwasser tolerance == 1e-8
TOL = 1e-8

def create_optimization_problem(guess, spec: specs.ModelSpec):
    pass

def make_guess(shape):
    # guess_baseline = 0.9
    # guess = np.array([guess_baseline] + [guess_baseline]*N + [guess_baseline]*N) # TODO: find a better guess
    guess = np.random.rand(*shape)
    return guess


if __name__ == '__main__':
    # try to reproduce Ikefuji
    TYPE = 'SICE_GOL'

    if TYPE == 'SICE':
        mspec = specs.ModelSpec(specs.ModelTypes.SICE)
    elif TYPE == 'SICE_GOL':
        mspec = specs.ModelSpec(specs.ModelTypes.SICE_GOL)

    N = mspec.num_steps

    guess = make_guess((2*N+1,))
    lower_bds = np.array([0] + [mspec.mu_lower_bnd]*N + [mspec.savings_rate_lower_bnd]*N)
    upper_bds = np.array([1] + [mspec.mu_upper_bnd]*N + [mspec.savings_rate_upper_bnd]*N)
    bds = Bounds(lower_bds, upper_bds)

    objective = lambda x, args: -simulator.objective(x, args) # maximize instead of minimize

    METHOD = 'SLSQP'
    OPTS = {
        'ftol': TOL,
        'maxiter': 1000,
    }
    
    print('Running optimization problem...', end='', flush=True)

    tic = time.perf_counter()
    res = minimize(objective, guess, args=(mspec,), bounds=bds, tol=TOL, method=METHOD, options=OPTS) # tolerance taken from Faulwasser
    toc = time.perf_counter()

    print('Done', flush=True)

    print(f"res: {res}")
    policies = res.x[1:]
    policies = simulator.reshape_policies(policies)
    print(f"policies: {policies}")
    print(f"sol time: {toc-tic} seconds")

    if res.success:
        df = simulator.save_simulation(res.x, mspec)
        df.to_csv(f"{TYPE}_{METHOD}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.csv", index=False)