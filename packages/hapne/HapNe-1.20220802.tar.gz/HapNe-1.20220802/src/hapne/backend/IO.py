from configparser import ConfigParser
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
import random
from scipy.stats import chi2, ttest_1samp
import logging
from hapne.ld import get_analysis_name, get_ld_output_folder
from hapne.utils import get_regions, get_region
from os.path import exists


class DataHandler:
    """
    This class handles the access and processing of the summary statistics
    """

    def __init__(self, config: ConfigParser, suffix="", extension=""):
        """
        :param config: see example.ini in the repository to know which information are available in the config file
        """
        self.output_folder = str(config["CONFIG"]["output_folder"]).strip("'")
        self.config = config

        self.genome_split = get_regions()

        self.nb_chromosomes = self.genome_split.shape[0]  # legacy

        self.u_min = config['CONFIG'].getfloat('u_min', fallback=self.get_default_u_min())
        self.u_max = config['CONFIG'].getfloat('u_max', fallback=self.get_default_u_max())

        self.suffix = suffix
        self.extension = extension

        self.sample_size = self.get_sample_size()

        message = f"Analysing {self.sample_size} "
        message += "diploid individuals"
        logging.info(message)

        self._bins = self.read_bins()
        bin_from = self.apply_filter_u(self._bins[0, :].reshape(-1, 1))
        bin_to = self.apply_filter_u(self._bins[1, :].reshape(-1, 1))
        self.bins = np.append(bin_from.reshape(-1), bin_to[-1, 0]).reshape(-1)
        self._mu = None
        self.selected_regions = np.arange(self.genome_split.shape[0])

        default_loc = config["CONFIG"].get("output_folder")
        popname = config["CONFIG"].get("population_name")
        default_loc += f"/DATA/{popname}.age"
        self.time_heterogeneity_file = config['CONFIG'].get('age_samples', fallback=default_loc)
        if not exists(self.time_heterogeneity_file):
            self.time_heterogeneity_file = None

        self.apply_filter = config['CONFIG'].getboolean('filter_regions', fallback=True)

    def get_default_u_min(self):
        raise Exception("Not Implemented Error", "Data Handler should not be used directly")

    @property
    def mu(self):
        return self._mu[self.selected_regions, :]

    def nb_regions(self):
        return len(self.selected_regions)

    def read_bins(self):
        raise Exception("Not Implemented Error", "Data Handler should not be used directly")

    def read_file(self, region_index, column):
        raise Exception("Not Implemented Error", "Data Handler should not be used directly")

    def apply_filter_u(self, data):
        """
        Remove the data that are not between self.u_min and self.u_max
        :param data: nd array nb_bins x any columns
        """
        bins_from = self._bins[0, :]
        bins_to = self._bins[1, :]

        # find the index that are in the desired range
        start_from = np.argmax(bins_from >= self.u_min)

        if np.max(bins_to) < self.u_max:
            end_at = len(bins_to)
        else:
            end_at = np.argmax(bins_to >= self.u_max) + 1

        return data[start_from:end_at, :]

    def load_data(self, column, apply_filter_u=True):
        """
        Load and concatenate data from all chromosomes files.
        :param col_name: name or number of the column in the data file
        :param apply_filter_u: bool True if we want to filter data outside the desired bin range
        """
        cumulated_data = []

        for region in range(1, self.nb_regions() + 1):
            data = self.read_file(region, column)
            if apply_filter_u:
                data = self.apply_filter_u(data.reshape(-1, 1))

            cumulated_data.append(data.flatten())

        return np.asarray(cumulated_data).T

    def k_fold_split(self, nb_folds=10, return_indices=False):
        """
        :return: generator (mu_train, mu_test)
        """
        kf = KFold(n_splits=nb_folds, shuffle=True)
        for train, test in kf.split(self.mu):
            if return_indices:
                yield self.mu[train, :], self.mu[test, :], train, test
            else:
                yield self.mu[train, :], self.mu[test, :]

    def bootstrap(self, return_indices=False):
        """
        return a bootstrap based on the current mu
        :return: self.mu.shape ndarray
        """
        selected_indices = random.choices(np.arange(self.nb_regions()), k=self.nb_regions())
        if return_indices:
            return self.mu[selected_indices, :], selected_indices
        else:
            return self.mu[selected_indices, :]

    def get_region_name(self, index):
        """
        Process the file describing the genomic regions
        :param index: 1-nb regions
        :return: name of the ith file
        """
        return str(self.genome_split.loc[index - 1, 'NAME']).strip()


class LDLoader(DataHandler):
    def __init__(self, config: ConfigParser):
        super().__init__(config, suffix="_", extension="r2")
        self.ld = self.load_data('R2', apply_filter_u=False)
        try:
            output_folder = get_ld_output_folder(config)
            bias_filename = output_folder + get_analysis_name(config) + ".ccld"
            data = pd.read_csv(bias_filename)
            self.ccld = data.values[:, 2].mean()
            self.bessel_cor = data.values[:, 4].mean()
            _, self.pval_no_admixture = ttest_1samp(data.values[:, 2].astype(float) -
                                                    data.values[:, 3].astype(float), 0)

        except FileNotFoundError:
            logging.warning("Bias file not found, running HapNe-LD assuming no admixture LD and high coverage.")
            self.missingness = config.getfloat("CONFIG", "missingness", fallback=0)
            n_eff = self.sample_size * (1 - self.missingness)
            self.ccld = 4 / (n_eff - 1.) ** 2
            self.bessel_cor = (n_eff / (n_eff - 1.)) ** 2
            self.pval_no_admixture = np.nan

        self._mu = self.ld_to_p_ibd(self.apply_filter_u(self.ld)).T
        # Combine bins if we are dealing with a small genotype or high missingness
        # self.merge_bins_if_required()

        # Discard suspicious Regions
        self.filter_tolerance = config['CONFIG'].getfloat('filter_tol', fallback=6)
        if self.apply_filter:
            self.apply_region_filter()
        logging.info(f"Analyzing {self.mu.shape[0]} regions ")

        self.phi2 = np.var(self.mu, axis=0).reshape(-1)
        self.sigma = np.diag(self.phi2)

        if self.time_heterogeneity_file is not None:
            logging.info("Using time heterogeneity correction ")
            self.time_heterogeneity = LDTimeIO(self.time_heterogeneity_file, self.bins)
        else:
            logging.info("No age of samples found, assuming they originate from the same generation...")
            self.time_heterogeneity = None

    def get_sample_size(self):
        pseudo_diploid = self.config.getboolean("CONFIG", "pseudo_diploid", fallback=None)
        if pseudo_diploid is None:
            pseudo_diploid = False
            logging.warning("[CONFIG]pseudo_diploid not found in config file, assuming diploid. \n \
                            If you are analysing aDNA, set the flag to True.")

        region1 = get_region(1)
        default_loc = self.config.get("CONFIG", "output_folder") + "/DATA/GENOTYPES"
        genotypes_loc = self.config.get("CONFIG", "genotypes", fallback=default_loc)
        fam_file = pd.read_csv(f"{genotypes_loc}/{region1['NAME']}.fam", header=None, sep="\t")
        return (2 - pseudo_diploid) * fam_file.shape[0]

    def apply_region_filter(self):
        """
        discard suspicious regions
        :return:
        """
        mu_med = np.median(self._mu, axis=0)
        mu_std_up = np.quantile(self._mu, 0.16, axis=0)
        mu_std_down = np.quantile(self._mu, 0.84, axis=0)
        mu_std = np.abs(mu_std_down - mu_std_up) / 2.
        mu_se = mu_std / np.sqrt(self._mu.shape[0]) * self.filter_tolerance
        self.selected_regions = \
            np.where((((self._mu > (mu_med - mu_se)).max(axis=1) == 1)
                     * ((self._mu > (mu_med + mu_se)).min(axis=1) == 0))
                     * ((np.abs(self._mu - mu_med) > self.filter_tolerance * mu_std).sum(axis=1) <= 1))[0]

    def read_bins(self):
        region = self.get_region_name(1)
        bins = pd.read_csv(f"{self.input_files_location()}/{region}.{self.extension}",
                           sep=",").values[:, 1:3].T
        return bins

    def ld_to_p_ibd(self, ld):
        """
        Convert ld + bias into probability of being IBD
        :param ld:
        """
        p_ibd = (ld - self.ccld) / (self.bessel_cor - 0.25 * self.ccld)
        # Approximated correction for the continuous-time approximation
        p_ibd *= np.exp(self.bins[:-1]).reshape((-1, 1))
        return p_ibd

    def read_file(self, region_index, column):
        region = self.get_region_name(region_index)
        filename = f"{self.input_files_location()}/{region}.{self.extension}"
        data = pd.read_csv(filename, sep=",")
        return data[column].values

    def is_admixture_significant(self):
        NotImplementedError

    def merge_bins_if_required(self):
        # Compute the average weight
        weights = self.load_data('WEIGHT', apply_filter_u=True).mean()
        # if the weight is less than 1e4, merge 2 bins into 1
        if weights < 2e4:
            bins_to_merge = 2
            nb_bins_first = self.bins.shape[0]
            nb_bins_end = (nb_bins_first - 1) // bins_to_merge + 1
            new_bins = np.zeros(nb_bins_end)
            new_mu = np.zeros([self.nb_regions(), nb_bins_end - 1])
            for ii in range(nb_bins_end - 1):
                new_bins[ii] = self.bins[bins_to_merge * ii]
                new_mu[:, ii] = 1. / bins_to_merge * (np.sum(self.mu[:, ii:(ii + bins_to_merge)], axis=1))
            new_bins[-1] = self.bins[14]

            self._mu = new_mu
            self.bins = new_bins

    def get_default_u_min(self):
        return 0.01

    def get_default_u_max(self):
        return 0.1

    def input_files_location(self):
        default_loc = self.output_folder + "/LD"
        return self.config["CONFIG"].get("ld_files", fallback=default_loc)


class IBDLoader(DataHandler):
    def __init__(self, config: ConfigParser):
        super().__init__(config, suffix=".", extension="ibd.hist")
        self.trim = config["CONFIG"].getfloat('segment_center_threshold_M', fallback=0.0)
        self._region_length = self.genome_split["LENGTH"].values / 100 - 2 * self.trim

        self._mu = self.load_data(2, apply_filter_u=True).T
        self.phi2 = np.ones(self.mu.shape[1])

        self.adjust_for_count()
        if self.apply_filter:
            self.apply_ibd_region_filter()
            self.adjust_for_count()
            logging.info(f"({self.genome_split.shape[0] - self.mu.shape[0]} were discarded)")
        logging.info(f"Last bin considered after filtering out small counts: {self.bins[-1]}")
        logging.info(f"Analyzing {self.mu.shape[0]} regions ")
        data = self._mu[self.selected_regions, :]
        mu = compute_poisson_mean(self.mu, self.region_length())
        mu = np.maximum(1. / self.region_length().sum(), mu)
        self.phi2 = np.var((data - mu) / np.sqrt(mu), axis=0, ddof=1)

        if self.time_heterogeneity_file is not None:
            logging.warning(
                "Samples with time offsets is not implemented for the IBD model yet,"
                + " falling back to no time offset")
            self.time_heterogeneity = None
        else:
            self.time_heterogeneity = None

    def adjust_for_count(self):
        mu_hat = self.mu.sum(axis=0) / self.region_length().sum()
        threshold = 1. / self.region_length().sum()
        has_hit = mu_hat >= threshold
        nb_valid_bins = np.max(np.nonzero(has_hit)) + 1
        self.bins = self.bins[:nb_valid_bins + 1]
        self._mu = self._mu[:, :nb_valid_bins]
        self.phi2 = self.phi2[:nb_valid_bins]

    def get_sample_size(self):
        return self.config["CONFIG"].getint("nb_samples")

    def read_bins(self):
        region = self.get_region_name(1)
        hist_files = self.input_files_location()
        return pd.read_csv(f"{hist_files}/{region}.{self.extension}",
                           sep="\t", header=None).values[0:, 0:2].T

    def input_files_location(self):
        default_loc = self.output_folder + "/HIST"
        return self.config["CONFIG"].get("hist_files", fallback=default_loc)

    def read_file(self, region_index, column):
        region = self.get_region_name(region_index)
        filename = f"{self.input_files_location()}/{region}.{self.extension}"
        data = pd.read_csv(filename, header=None, sep="\t").values[:, column]
        return data

    def get_default_u_min(self):
        return 0.02

    def get_default_u_max(self):
        return 0.5

    def region_length(self):
        return self._region_length[self.selected_regions]

    def apply_ibd_region_filter(self):
        """
        discard suspicious regions, assuming the data follow a negative binomial model
        :return:
        """

        def get_jackknife_residuals(data, indices, index):
            """
            Compute the residuals of genomic region index by computing the mean and
            the overdispersion parameter from all other regions.
            :param data:
            :param indices:
            :param index:
            :return:
            """
            train = np.delete(data, index, axis=0)
            validation = data[index, :]

            r_length = (self._region_length - 2 * self.trim)[indices]
            mu = compute_poisson_mean(data, r_length)
            mu_train = np.delete(mu, index, axis=0)
            phi2 = np.var((train - mu_train) / np.sqrt(mu_train), ddof=1, axis=0)

            return norm_residuals(validation, mu[index, :], phi2)

        def norm_residuals(y, mu, phi2):
            return (y - mu) / np.sqrt(mu) / np.sqrt(phi2)

        def get_jackknife_r2(data, indices, index):
            res = get_jackknife_residuals(data, indices, index)
            return np.sum(res ** 2)

        discarded = []
        n_bins = len(self.bins) - 1
        for iteration in range(2):
            current_ibd = np.delete(self._mu, discarded, axis=0)
            indices = np.delete(np.arange(self.nb_regions()), discarded)

            for ii in range(len(indices)):
                sse = get_jackknife_r2(current_ibd, indices, ii)
                if min(chi2.cdf(sse, n_bins), 1 - chi2.cdf(sse, n_bins)) < 1e-12:
                    discarded.append(indices[ii])

        self.selected_regions = np.delete(self.selected_regions, discarded)


class LDTimeIO:
    def __init__(self, timefile, u=np.zeros(1)):
        """
        Precompute
        :param timefile: file containing the age of the samples.
        :param u : time at which we compute the time offsets
        """
        u = u.reshape((1, -1))

        self.times = pd.read_csv(timefile, sep=",")
        self.times.columns = self.times.columns.str.replace(' ', '')
        self.t_start = np.min(self.times["FROM"].values)
        self.times -= self.t_start
        self.t_end = np.max(self.times["TO"].values) + 1

        self.age_density = self._compute_age_density()
        self.t_max_density = self._compute_tmax_density()
        # dt_density[ii, :] = P(Delta_t | tmax == ii)
        self.dt_density = self._compute_dt_density()
        # offset_correction[tmax, u] = E[exp(-dt u)|tmax]
        self.offset_correction = self._compute_offset_correction(u)

    def _compute_age_density(self):
        """
        Convert a list of times at which individuals lived into the density of age of a ramdomly sampled individual
        :return:
        """
        times = self.times.values
        list_time = np.arange(self.t_end)
        # One row per samples. 1 when they are alive
        samples_alive = np.zeros((times.shape[0], self.t_end))
        for ii in range(times.shape[0]):
            samples_alive[ii, :] = (list_time >= times[ii, 0]) * (list_time <= times[ii, 1])
        return samples_alive.sum(axis=0) / samples_alive.sum()

    def _compute_tmax_density(self):
        tmax_cumulative = np.cumsum(self.age_density) ** 2
        tmax_density = np.zeros_like(tmax_cumulative)
        tmax_density[0] = tmax_cumulative[0]
        tmax_density[1:] = np.diff(tmax_cumulative)
        return tmax_density

    def _compute_dt_density(self):
        dt_density = np.zeros(shape=(self.t_end, self.t_end))
        for ii in range(self.t_end):
            dt_density[ii, :ii + 1] = np.flip(self.age_density[:ii + 1]) / np.sum(self.age_density[:ii + 1])
        return dt_density

    def _compute_offset_correction(self, u):
        list_times = np.arange(self.t_end).reshape((-1, 1))
        u = u.reshape((1, -1))
        exponential_decays = 1. / 6 * (1 * np.exp(-list_times * u[0, 1:].reshape((1, -1))) +
                                       4 * np.exp(-list_times * u[0, :-1].reshape((1, -1))) +
                                       1 * np.exp(-list_times * 0.5 * (u[0, 1:] + u[0, :-1]))
                                       )
        offset = np.zeros((self.t_end, u.shape[1] - 1))
        for ii in range(self.t_end):
            offset[ii, :] = (self.dt_density[ii].reshape((-1, 1)) * exponential_decays).sum(axis=0)
        return offset


def compute_poisson_mean(data, region_length):
    p = data.sum(axis=0) / region_length.sum()
    mu = p.reshape((1, -1)) * region_length.reshape(-1, 1)
    return mu
