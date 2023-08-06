from configparser import ConfigParser
from hapne.backend.DemographicHistory import PieceWiseExpDemographicHistory
from hapne.backend.StatsModel import StatsModel, IBDModel, LDModel, DemographicHistory2StatsModelAdapter
from hapne.backend.IO import DataHandler, IBDLoader, LDLoader
import numpy as np
from scipy.optimize import minimize
from numpy import log, exp
import scipy
import os
import pandas as pd
from hapne.utils import smoothing, LogBijection
import logging


class HapNe:
    def __init__(self, config: ConfigParser):
        """
        Class HapNe allows to fit a demographic history based on summary statistics
        :param config: see example config file
        """
        self.config = config
        self.method = self.config["CONFIG"]['method'].lower()
        # Logging
        verbose = self.config.get("CONFIG", "verbose", fallback=False)
        if verbose:
            logging.basicConfig(level=logging.INFO)
        # Method specific instances
        self.io = self.get_loader()
        self.stats_model = self.get_stats_model()

        # Parameter related to the model
        self.parameter_grid = np.array([10.**(-5 + ii) for ii in range(0, 7)])
        self.u_min = self.get_default_u_min()  # Minimum value of u
        self.u_quantile = self.config.getfloat("CONFIG", "u_quantile", fallback=self.u_min)
        self.dt_min = max(0.25, self.config.getint("CONFIG", "dt_min", fallback=1))
        self.dt_max = self.config.getint("CONFIG", "dt_max", fallback=5000)
        self.t_max = self.config.getint("CONFIG", "t_max", fallback=125)
        self.buffer_time = self.t_max - 25  # the times averages the deep time effect
        # Parameters related to the fitting procedure
        # this value can be tuned (tested between 2 and 24) to increase/reduce resolution
        pseudo_diploid = self.config.getboolean("CONFIG", "pseudo_diploid", fallback=False)
        default_params = 16 if pseudo_diploid else 21
        self.nb_parameters = self.config.getint("CONFIG", "nb_parameters", fallback=default_params)
        self.random_restarts = 3
        self.eps = 1e-4
        self.ftol = 1e-3
        self.n_min = 1e2
        self.n_max = 1e9
        self.signal_threshold = 6.635 if self.config['CONFIG']['METHOD'] == "ld" else 9.210
        self.nb_bootstraps = self.config.getint("CONFIG", "nb_bootstraps", fallback=100)

        # Initialisations
        self.times = scipy.stats.erlang.ppf(np.linspace(0, 1, self.nb_parameters + 1)[:-1], a=2,
                                            scale=1. / (2 * self.u_quantile))
        self.init_times()

    def get_loader(self) -> DataHandler:
        """
        Initialise the loader based on the method
        :return: subclass of DataHandler
        """
        if self.method == "ibd":
            dh = IBDLoader(self.config)
        elif self.method == "ld":
            dh = LDLoader(self.config)
        else:
            raise Exception("not implemented error", "method must either be LD or IBD")
        return dh

    def get_default_u_min(self):
        """
        Depending on the method, the default value is different.
        :return: minimum genetic distance in morgan
        """
        if self.method == "ibd":
            return 0.025
        elif self.method == "ld":
            return 0.005
        else:
            raise Exception("not implemented error", "method must either be LD or IBD")

    def get_stats_model(self) -> StatsModel:
        """
        Initialise the stats model to be used based on the method
        :return: subclass of StatsModel
        """
        if self.config["CONFIG"]['method'].lower() == "ibd":
            number_haploid_samples = 2 * self.config.getint("CONFIG", "nb_samples")
            nb_pairs = 0.5 * number_haploid_samples * (number_haploid_samples - 1)
            stats_model = IBDModel(nb_pairs, self.io.region_length().reshape([-1, 1]), self.io.phi2)

        elif self.config["CONFIG"]['method'].lower() == "ld":
            stats_model = LDModel(sigma=self.io.sigma)
        else:
            raise Exception("not implemented error", "method must either be LD or IBD")

        return stats_model

    def init_times(self):
        const_estimator = self.fit_constant()
        ne = np.ones(self.nb_parameters) * const_estimator
        self.update_times(ne)

    def fit_constant(self) -> float:
        def local_loss(ne):
            n = np.ones(self.nb_parameters) * ne
            return self.sse(n)
        res = minimize(lambda x: local_loss(self.x2n(x)), np.log(10_000))
        return self.x2n(res.x)[0]

    def fit(self):
        """
        Perform HapNe fitting procedure and save the results.
        """
        # Step 1 : calibrate times and get MAP Ne and best regularisation
        logging.info("Starting the calibration step...")
        ne_hat, sig2 = self.calibrate_method()
        logging.info(f"Calibration step done, {sig2:.5f} selected!")
        # Step 2 : bootstrap results
        logging.info("Starting the bootstrapping procedure...")
        ne_bootstrap = self.bootstrap(ne_hat, sig2)
        # Step 3 : save results
        logging.info("Saving results...")
        self.save_results(ne_bootstrap)

    def calibrate_method(self):
        """
        Find the best regularisation parameter and time intervals
        """
        nb_iterations = 5
        # Save the results of each iterations
        times, nes = [np.zeros((nb_iterations, self.nb_parameters)) for _ in range(2)]
        sigmas, sses = [np.inf + np.zeros(nb_iterations) for _ in range(2)]
        # Run all iterations
        for ii in range(nb_iterations):
            times[ii, :] = self.times.copy()
            logging.info(f"Starting iteration {ii+1}")
            logging.info("*****")
            ne_hat, sig2, sse = self.run_relaxation()
            sigmas[ii], sses[ii] = sig2, sse
            logging.info(f"Iteration {ii+1}/{nb_iterations} : {sig2:.5f} - {sse:.2f} ")
            nes[ii, :] = ne_hat.ravel().copy()
            self.update_times(ne_hat)
            # Escape the iterations if time intervals have converged
            if self.time_intervals_have_converged(old_times=times[ii, :]):
                logging.info(f"Converged at iteration {ii}")
                return self.select_calibration(times[:ii + 1, :], nes[:ii + 1, :], sigmas[:ii + 1], sses[:ii + 1])
        return self.select_calibration(times, nes, sigmas, sses)

    def run_relaxation(self):
        """
        Run a grid-search over different values of the hyperparameters
        Select the highest regularisation consistent with the signal.
        """
        nb_points = len(self.parameter_grid)
        # The loss is -log likelihood, hence does not depend on regularisation
        sses = np.inf + np.zeros(nb_points)
        nes = np.zeros((nb_points, self.nb_parameters))
        # Initialize the population size with the constant estimator
        ne_ini = np.ones(self.nb_parameters) + self.fit_constant()
        for ii, sigma2 in enumerate(self.parameter_grid):
            # minimize the penalized likelihood and get ne and loss (- log likelihood, no reg.)
            ne, sse = self.argmin_loss(ne_ini, sigma2)
            # Update the results if there is an improvement
            if sse < np.max(sses):
                nes[ii, :] = ne.copy()
                sses[ii] = sse
            # If not, the optimisation has not worked, do not save the results
            else:
                nes[ii, :] = nes[ii - 1, :]
                sses[ii] = sses[ii - 1]
            # Get the new inital paramter
            ne_ini = nes[ii, :]
            logging.info(f"{sigma2:.5f} - {sses[ii]:.2f}")
        # Select the best hyperparameter based on the grid search
        index = self.get_best_hyperparameter_index(sses)
        return nes[index, :], self.parameter_grid[index], self.sse(nes[index, :])

    def argmin_loss(self, ne_ini: np.ndarray, sigma2: float, data=None) -> tuple:
        best_loss = np.inf
        for _ in range(self.random_restarts):
            res = minimize(lambda x: self.loss(self.x2n(x), sigma2, data), self.n2x(ne_ini),
                           method='L-BFGS-B',
                           options={
                'ftol': self.ftol,
                'maxcor': 100,
                'eps': self.eps
            }
            )
            # Save the results if improved
            if res.fun < best_loss:
                ne = self.x2n(res.x)
                best_loss = res.fun
            # Add a perturbation to the initial guess
            ne_ini = ne_ini * np.random.uniform(0.75, 1.33, len(ne_ini))
        return ne, self.sse(ne)

    def loss(self, ne, sigma2, observations=None) -> float:
        return self.sse(ne, observations) - self.log_prior(ne, sigma2)

    def sse(self, ne, observations=None) -> float:
        """
        Compute the SSE of the Deviance residuals.
        :param : ne
        :param : observations : either none to use all data, or set of data
        """
        if observations is None:
            observations = self.io.mu
        predictions = self.predict(ne)
        return np.sum(self.stats_model.residuals(observations, predictions)**2)

    def log_prior(self, ne: np.ndarray, sigma2: float) -> float:
        """
        Returns the log prior, up to a constant
        """
        return -(np.sqrt(np.diff(np.log(ne))**2 + np.diff(self.times)**2).sum() - self.times[-1]) / sigma2

    def x2n(self, x: np.ndarray) -> np.ndarray:
        n = exp(x)
        return np.clip(n, self.n_min, self.n_max)

    def n2x(self, n: np.ndarray) -> np.ndarray:
        n = np.clip(n, self.n_min, self.n_max)
        return log(n)

    def get_best_hyperparameter_index(self, losses: np.ndarray) -> int:
        """
        Select the best hyperparameter consistent with the data
        """
        sig2_index = np.argmin(losses > np.min(losses) + self.signal_threshold)
        return sig2_index

    def time_intervals_have_converged(self, old_times: np.ndarray):
        """
        Determine whether the time intervals have converged.
        """
        # Return True if the maximum difference between two intervals is less than 2 generations
        return np.max(np.abs(old_times - self.times)) < 2

    def select_calibration(self, times: np.ndarray, nes: np.ndarray, sigmas: np.ndarray, losses: np.ndarray):
        """
        The calibration methods saves all intermediary results, this method returns the best one
        """
        best_calibration_index = np.argmin(losses)
        ne_hat = nes[best_calibration_index, :].ravel()
        sigma2 = sigmas[best_calibration_index]
        times = times[best_calibration_index, :].ravel()
        self.times = times
        return ne_hat, sigma2

    def update_times(self, ne):
        """
        Update the time intervals to match quantiles based on ne
        """
        demo = self.n2demohist(ne)
        self.times = demo.time_quantiles(self.u_quantile, self.nb_parameters,
                                         min_interval_length=self.dt_min,
                                         max_interval_length=self.dt_max, last_t=self.t_max)

    def n2demohist(self, n, return_coefs=False):
        """
        convert the parameters theta into a demographic history
        :param n: population size at the beginning of each interval
        :param return_coefs : if True also return the exponential coefficients
        :return : Demographic History 2 StatsModel Adapter
        """
        n = np.clip(n, 1e2, 1e8)
        demo_hist = PieceWiseExpDemographicHistory(n, u_min=self.u_quantile, delta_t_max=1,
                                                   time_thresholds=self.times)
        coefs = demo_hist.exp_coef
        demo_hist = DemographicHistory2StatsModelAdapter(demo_hist.time[:-1], demo_hist.n)
        if return_coefs:
            return demo_hist, coefs
        else:
            return demo_hist

    def predict(self, n):
        demo_hist = self.n2demohist(n, return_coefs=False)
        if self.io.time_heterogeneity is None:
            return self.stats_model.predict(self.io.bins, demo_hist)
        else:
            predictions = np.zeros((1, len(self.io.bins) - 1))
            for t in np.arange(self.io.time_heterogeneity.t_end):
                demo_hist_truncated = DemographicHistory2StatsModelAdapter(demo_hist.time[t:-1] - demo_hist.time[t],
                                                                           demo_hist.n[t:])
                predictions += self.io.time_heterogeneity.t_max_density[t] \
                    * self.io.time_heterogeneity.offset_correction[t].reshape((1, -1)) \
                    * self.stats_model.predict(self.io.bins, demo_hist_truncated).reshape((1, -1))
            return predictions.ravel()

    def bootstrap(self, ne_ini, sig2):
        """
        Sample chromosome arms with replacements to get an approximate CI for Ne
        """
        ne_boot = np.zeros((self.nb_bootstraps, self.t_max - 1), dtype=int)

        for ii in range(self.nb_bootstraps):
            mu_boot, indices = self.io.bootstrap(return_indices=True)
            self.stats_model.set_dataset(indices)
            sig2_boot = sig2 * 10.**np.random.uniform(0, 1)
            ne_hat, _ = self.argmin_loss(ne_ini, sig2_boot, mu_boot)
            ne_boot[ii, :] = self.n2demohist(ne_hat).n.ravel()[:self.t_max - 1]
        self.stats_model.set_dataset(np.arange(self.io.nb_regions()))
        return ne_boot

    def save_results(self, n_boot: np.ndarray):
        output_folder = self.config["CONFIG"]["output_folder"] + "/HapNe"
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        n_quantiles = np.quantile(n_boot, [0.025, 0.25, 0.5, 0.75, 0.975], axis=0).T
        times = np.arange(1, 1 + n_boot.shape[1]).reshape(-1, 1)
        to_save = np.concatenate([times, n_quantiles], axis=1).astype(int)
        df = pd.DataFrame(data=to_save, columns=["TIME", "Q0.025", "Q0.25", "Q0.5", "Q0.75", "Q0.975"])
        transformer = LogBijection()
        w = 20
        for key in ['Q0.025', 'Q0.25', 'Q0.5', 'Q0.75', 'Q0.975']:
            df[key] = smoothing(df[key], transformer, w)
        df = df.astype(int)

        df.head(self.buffer_time).to_csv(f"{output_folder}/hapne.csv", index=False)
