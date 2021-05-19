import time
import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import scipy.optimize
import simulator
import specs

VERSION = '0.1'

# Faulwasser tolerance == 1e-8
TOL = 1e-8

IMPLEMENTED_MODELS = [
    'SICE',
    'SICE_GOL',
]

# setup interactions
parser = argparse.ArgumentParser(description='Find the optimal policy in some DICE-like IAMs.')
parser.add_argument('--type',
    type=str,
    choices=IMPLEMENTED_MODELS,
    help='specify the type of model, options are "SICE" which runs SICE, and "SICE_GOL" which runs SICE with temperature dynamics from Golosav et. al.',
    default='SICE_GOL',
)
parser.add_argument('--verbose', '-v', action='count', default=0, help="specify how much output to print; adding more 'v's will add more ouput, for example -vvv will make the output very verbose.")
parser.add_argument('--dry-run', action='store_true', help=argparse.SUPPRESS) # useful for debugging
parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')


def make_guess(shape):
    # guess_baseline = 0.9
    # guess = np.array([guess_baseline] + [guess_baseline]*N + [guess_baseline]*N) # TODO: find a better guess
    guess = np.random.rand(*shape)
    return guess

class Optimizer():
    def __init__(self, mspec: specs.ModelSpec):
        self.mspec = mspec

    def setup_optimization(self):
        mspec = self.mspec

        # horizon size
        N = mspec.num_steps

        # configer pre-conditions
        self.guess = make_guess((2*N+1,))
        lower_bds = np.array([mspec.savings_rate_lower_bnd] + [mspec.mu_lower_bnd]*N + [mspec.savings_rate_lower_bnd]*N)
        upper_bds = np.array([mspec.savings_rate_upper_bnd] + [mspec.mu_upper_bnd]*N + [mspec.savings_rate_upper_bnd]*N)
        self.bds = scipy.optimize.Bounds(lower_bds, upper_bds)

        self.objective = lambda x, args: -simulator.objective(x, args) # maximize instead of minimize

        self.METHOD = 'SLSQP'
        self.OPTS = {
            'ftol': TOL,
            'maxiter': 1000,
        }

    def optimize(self):
        res = scipy.optimize.minimize( # scipy.optimize.minimize
            self.objective,
            self.guess,
            args=(self.mspec,),
            bounds=self.bds,
            tol=TOL, # tolerance taken from Faulwasser
            method=self.METHOD,
            options=self.OPTS
        )
        return res


if __name__ == '__main__':
    # parse user options
    opts = parser.parse_args()
    verbosity = opts.verbose
    if opts.type == 'SICE':
        mspec = specs.ModelSpec(specs.ModelTypes.SICE)
    elif opts.type == 'SICE_GOL':
        mspec = specs.ModelSpec(specs.ModelTypes.SICE_GOL)
    dry_run = opts.dry_run

    # configure optimization problem
    problem = Optimizer(mspec)
    problem.setup_optimization()

    print(f'Running optimization problem for model type {opts.type}...', end='', flush=True)

    # perform optimization
    save_output = False
    tic = time.perf_counter()
    if not dry_run:
        res = problem.optimize()
        save_output = res.success
    toc = time.perf_counter()

    print('Done.', flush=True)

    if verbosity > 0:
        print(f'Total simulation time: {toc-tic:.3f} seconds.')

    if verbosity > 1 and not dry_run: # debugging output
        print(f"{res = }")
        policies = res.x[1:]
        policies = simulator.reshape_policies(policies)
        print(f"{policies = }")

    # save results to a csv for analysis
    if save_output:
        output_name = f"{opts.type}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.csv"
        df = simulator.save_simulation(res.x, mspec)
        df.to_csv(output_name, index=False)

        if verbosity > 0:
            print(f'Results saved into {output_name}.')
