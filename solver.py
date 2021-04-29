import time
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.optimize import Bounds, minimize
import simulator
import specs

# Faulwasser tolerance == 1e-8
TOL = 1e-5

def create_optimization_problem(guess, spec: specs.ModelSpec):
    pass

if __name__ == '__main__':
    # try to reproduce Ikefuji
    mspec = specs.ModelSpec(specs.ModelTypes.SICE)
    N = mspec.num_steps

    guess_baseline = 0.9
    guess = np.array([guess_baseline] + [guess_baseline]*N + [guess_baseline]*N) # TODO: find a better guess
    lower_bds = np.array([0] + [mspec.mu_lower_bnd]*N + [mspec.savings_rate_lower_bnd]*N)
    upper_bds = np.array([1] + [mspec.mu_upper_bnd]*N + [mspec.savings_rate_upper_bnd]*N)
    bds = Bounds(lower_bds, upper_bds)

    objective = lambda x, args: -simulator.objective(x, args) # maximize instead of minimize

    tic = time.perf_counter()
    res = minimize(objective, guess, args=(mspec,), bounds=bds, tol=TOL) # tolerance taken from Faulwasser
    toc = time.perf_counter()

    if res.success:
        welfare = simulator.objective(res.x, mspec)
        print(f"Solution found; exited with message: {res.message}.")
        print(f"Optimal welfare: {welfare}")

        policies = res.x[1:]
        policies = simulator.reshape_policies(policies)
        print(f"res: {res}")
        print(f"policies: {policies}")

    else:
        print(f"Solution attempt failed; exited with message: {res.message}")
        print(f"{res}")

    print()
    print(f'Solution time (in seconds): {toc-tic}')

    df = simulator.save_simulation(res.x, mspec)
    df.to_csv(f"SICE_sim_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.csv", index=False)