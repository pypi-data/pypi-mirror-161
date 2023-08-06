import numpy as np

from pypop7.optimizers.es.es import ES


class DSAES(ES):
    """Derandomized Self-Adaptation Evolution Strategy (DSAES, Derandomized (1,λ)-σSA-ES).

    Reference
    ---------
    Hansen, N., Arnold, D.V. and Auger, A., 2015.
    Evolution strategies.
    In Springer Handbook of Computational Intelligence (pp. 871-898). Springer, Berlin, Heidelberg.
    https://link.springer.com/chapter/10.1007%2F978-3-662-43505-2_44
    (See Algorithm 44.5 for details.)

    Ostermeier, A., Gawelczyk, A. and Hansen, N., 1994.
    A derandomized approach to self-adaptation of evolution strategies.
    Evolutionary Computation, 2(4), pp.369-380.
    https://direct.mit.edu/evco/article-abstract/2/4/369/1407/A-Derandomized-Approach-to-Self-Adaptation-of
    """
    def __init__(self, problem, options):
        if options.get('n_individuals') is None:
            options['n_individuals'] = 10  # mandatory setting for DSAES
        ES.__init__(self, problem, options)
        if self.eta_sigma is None:
            self.eta_sigma = 1 / 3
        self._axis_sigmas = None
        # E[|N(0,1)|]: expectation of half-normal distribution
        self._e_hnd = np.sqrt(2 / np.pi)

    def initialize(self, is_restart=False):
        self._axis_sigmas = self._sigma_bak * np.ones((self.ndim_problem,))
        x = np.empty((self.n_individuals, self.ndim_problem))  # offspring population
        mean = self._initialize_mean(is_restart)  # mean of Gaussian search distribution
        sigmas = np.ones((self.n_individuals, self.ndim_problem))  # individual step-sizes for all offspring
        y = np.empty((self.n_individuals,))  # fitness (no evaluation)
        return x, mean, sigmas, y

    def iterate(self, x=None, mean=None, sigmas=None, y=None, args=None):
        for k in range(self.n_individuals):  # sample population (Line 4)
            if self._check_terminations():
                return x, sigmas, y
            sigma = self.eta_sigma * self.rng_optimization.standard_normal()  # Line 5
            z = self.rng_optimization.standard_normal((self.ndim_problem,))  # Line 6
            x[k] = mean + np.exp(sigma) * self._axis_sigmas * z  # Line 7
            # Line 8 (to mimick the effect of intermediate recombination)
            sigmas_1 = np.power(np.exp(np.abs(z) / self._e_hnd - 1), 1 / self.ndim_problem)
            sigmas_2 = np.power(np.exp(sigma), 1 / np.sqrt(self.ndim_problem))
            sigmas[k] = self._axis_sigmas * sigmas_1 * sigmas_2
            y[k] = self._evaluate_fitness(x[k], args)
        return x, sigmas, y

    def _restart_initialize(self):
        self._fitness_list.append(self.best_so_far_y)
        is_restart_1, is_restart_2 = np.all(self._axis_sigmas < self.sigma_threshold), False
        if len(self._fitness_list) >= self.stagnation:
            is_restart_2 = (self._fitness_list[-self.stagnation] - self._fitness_list[-1]) < self.fitness_diff
        is_restart = bool(is_restart_1) or bool(is_restart_2)
        if is_restart:
            self.n_restart += 1
            self.n_individuals *= 2
            self._fitness_list = [np.Inf]
        return is_restart

    def restart_initialize(self, x=None, mean=None, sigmas=None, y=None):
        if self._restart_initialize():
            x, mean, sigmas, y = self.initialize(True)
        return x, mean, sigmas, y

    def optimize(self, fitness_function=None, args=None):  # for all generations (iterations)
        fitness = ES.optimize(self, fitness_function)
        x, mean, sigmas, y = self.initialize()
        while True:
            # sample and evaluate offspring population
            x, sigmas, y = self.iterate(x, mean, sigmas, y, args)
            if self.record_fitness:
                fitness.extend(y)
            if self._check_terminations():
                break
            order = np.argsort(y)[0]  # Line 9
            self._axis_sigmas = np.copy(sigmas[order])  # Line 10
            mean = np.copy(x[order])  # Line 11
            self._n_generations += 1
            self._print_verbose_info(y)
            if self.is_restart:
                x, mean, sigmas, y = self.restart_initialize(x, mean, sigmas, y)
        results = self._collect_results(fitness, mean)
        results['_axis_sigmas'] = self._axis_sigmas
        return results
