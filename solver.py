import time
import numpy as np
import scipy.optimize
import simulator
import specs

def create_optimization_problem(guess, spec: specs.ModelSpec):
    pass

if __name__ == '__main__':
    mspec = specs.ModelSpec()
    N = mspec.num_steps
    guess = np.array([0.5] + [0.5]*N + [0.5]*N) # TODO: find a better guess
    lower_bds = np.array([0] + [mspec.mu_lower_bnd]*N + [mspec.savings_rate_lower_bnd]*N)
    upper_bds = np.array([1] + [mspec.mu_upper_bnd]*N + [mspec.savings_rate_upper_bnd]*N)
    bds = scipy.optimize.Bounds(lower_bds, upper_bds)

    objective = lambda x, args: -simulator.objective(x, args) # maximize instead of minimize

    tic = time.perf_counter()
    res = scipy.optimize.minimize(objective, guess, args=(mspec,), bounds=bds, tol=1e-8) # tolerance taken from Faulwasser
    toc = time.perf_counter()

    if res.success:
        welfare = simulator.objective(res.x, mspec)
        print(f"Solution found; exited with message: {res.message}.")
        print(f"Optimal welfare: f{welfare}")
    else:
        print(f"Solution attempt failed; exited with message: {res.message}")

    print()
    print(f'Solution time (in seconds): {toc-tic}')
