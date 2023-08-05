import unittest
import time
import numpy as np

from pypop7.benchmarks.base_functions import ellipsoid, rosenbrock, rastrigin
from pypop7.optimizers.es.fmaes import FMAES as Solver


class TestFMAES(unittest.TestCase):
    def test_optimize(self):
        start_run = time.time()
        ndim_problem = 1000
        for f in [ellipsoid, rosenbrock, rastrigin]:
            print('*' * 7 + ' ' + f.__name__ + ' ' + '*' * 7)
            problem = {'fitness_function': f,
                       'ndim_problem': ndim_problem,
                       'lower_boundary': -5 * np.ones((ndim_problem,)),
                       'upper_boundary': 5 * np.ones((ndim_problem,))}
            options = {'max_function_evaluations': 2e6,
                       'fitness_threshold': 1e-10,
                       'max_runtime': 3600,  # 1 hours
                       'seed_rng': 0,
                       'x': 4 * np.ones((ndim_problem,)),  # mean
                       'sigma': 0.1,
                       'verbose_frequency': 200,
                       'record_fitness': True,
                       'record_fitness_frequency': 200000}
            solver = Solver(problem, options)
            results = solver.optimize()
            print(results)
            print('*** Runtime: {:7.5e}'.format(time.time() - start_run))


if __name__ == '__main__':
    unittest.main()
