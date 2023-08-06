from configparser import ConfigParser, NoOptionError
from hapne.utils import get_bins, get_region, get_regions
import numpy as np
from numpy import sqrt
from numba import njit
import pandas_plink as pdp
import pandas as pd
import os
import logging


def get_analysis_name(config: ConfigParser):
    name = config.get("CONFIG", "population_name", fallback=None)
    if name is None:
        name = "hapne"
    return name


def get_genotypes_location(config: ConfigParser):
    output_folder = config["CONFIG"].get("output_folder")
    default = output_folder + "/DATA/GENOTYPES"
    return config["CONFIG"].get("genotypes", fallback=default)


def compute_ld(config: ConfigParser):
    nb_regions = get_regions().shape[0]
    for ii in range(nb_regions):
        compute_ld_in_parallel(ii, config)


def compute_ccld(config: ConfigParser):
    nb_regions = get_regions().shape[0]
    nb_pairs = nb_regions * (nb_regions - 1) // 2
    create_cc_file(config)
    for ii in range(nb_pairs):
        compute_cc_quantities_in_parallel(ii, config)


def compute_ld_in_parallel(region_index: int, config: ConfigParser):
    """ Compute the (biased) LD for a given region and save the results in a config['output']/region.r2 file.
    :param config : see readme for an example
    :param region : index of the region
    :param save_hist: if True, also save a .ld file, which can be use to filter out problematic regions or SNPs
    """
    region = get_region(region_index)
    maf = config.getfloat("CONFIG", "maf", fallback=0.25)
    genotype_folder = get_genotypes_location(config)
    genotype, chr_map = load_and_preprocess_file(genotype_folder + "/" + region["NAME"] + ".bed",
                                                 maf)

    bins = get_bins()

    ld, weights = _compute_r2(genotype, chr_map, bins)
    save_ld_results(config, region["NAME"], ld, weights, bins)


def create_cc_file(config: ConfigParser):
    output_folder = get_ld_output_folder(config)
    output_file = output_folder + get_analysis_name(config) + ".ccld"
    with open(output_file, "w") as f:
        f.write("REGION1, REGION2, CCLD, CCLD_H0, BESSEL_FACTOR, S_CORR\n")


def compute_cc_quantities_in_parallel(job_index: int, config: ConfigParser, nb_points=int(1e6)):
    """ Compute the (biased) bias computed from the two regions provided as parameter.
    :param config : see preprocess_ld.config for an example
    :param nb_points : number of points to consider when computing the cross-chromosome bias
    """
    reg1, reg2 = get_regions_from_index(job_index)
    maf = config.getfloat("CONFIG", "maf", fallback=0.25)

    try:
        pseudo_diploid = config.getboolean("CONFIG", "pseudo_diploid")
    except NoOptionError:
        pseudo_diploid = config.getboolean("CONFIG", "pseudo_diploid", fallback=False)
        logging.warning("[CONFIG]pseudo_diploid not found in config file, assuming diploid. \n \
                        If you are analysing aDNA, set the flag to True.")
    folder = get_genotypes_location(config)
    genotype1, _ = load_and_preprocess_file(folder + "/" + reg1 + ".bed", maf)
    genotype2, _ = load_and_preprocess_file(folder + "/" + reg2 + ".bed", maf)

    ccld, expected_ccld, bessel_factor, s_corr = _compute_cc_quantities(genotype1, genotype2,
                                                                        int(nb_points), pseudo_diploid)

    output_folder = get_ld_output_folder(config)
    output_file = output_folder + get_analysis_name(config) + ".ccld"
    with open(output_file, "a") as f:
        f.write(f"{reg1},{reg2},{ccld},{expected_ccld},{bessel_factor},{s_corr}\n")


@njit(cache=True)
def _compute_r2(genotype: np.ndarray, gen_map, bins: np.ndarray):
    """ For a given genotype, compute LD within the bins
    :param genotype: (nb ind x nb snps) unphased genotype
    :param gen_map: distance between sites
    :param bins: nb_bins x 2 corresponding to the start and the end of each bin, respectively
    :return: r2 in each bin
    """
    nb_bins = bins.shape[0]

    r2_in_bin = np.zeros(shape=nb_bins)
    weight_in_bin = np.zeros_like(r2_in_bin)
    # Loop over all pairs of columns
    for index_x in range(genotype.shape[1] - 2):
        index_y = index_x + 1
        delta_xy = genetic_distance(index_x, index_y, gen_map)
        while delta_xy < np.max(bins[:, 1]) and index_y < np.shape(genotype)[1]:
            delta_xy = genetic_distance(index_x, index_y, gen_map)
            bb = get_bin_index(delta_xy, bins)
            if bb is not None:
                bb = int(bb)
                valid_snps_x, valid_snps_y, weight = get_valid_xy(genotype[:, index_x],
                                                                  genotype[:, index_y])
                if weight > 0 and valid_snps_x.shape[0] > 1:
                    current_mean = r2_in_bin[bb]
                    observation = two_snp_correlation(valid_snps_x, valid_snps_y)
                    r2_in_bin[bb] = (current_mean * weight_in_bin[bb] + observation * weight) \
                        / (weight_in_bin[bb] + weight)
                    weight_in_bin[bb] += weight
            index_y += 1
    return r2_in_bin, weight_in_bin


def load_and_preprocess_file(bed_file: str, maf=0.25):
    """
    Load the bed file and apply the normalisation procedure.
    Variants under the maf threshold will be set to np.nan
    :param bed_file : path to the bed file, including the .bed
    :param maf : minor allele frequency threshold
    :return genotype and chromosome_map
    """
    genotype, chr_map = load_files(bed_file)
    genotype = preprocess_genotype(genotype, maf_filter=maf)
    return genotype, chr_map


def get_regions_from_index(job_index: int):
    region_list = get_regions().values[:, 3]
    n = len(region_list)
    k = job_index

    # job_index corresponds to regions i and j
    # basically, this will map k to {(0, 1), (0, 2)... (1, 2), (1, 3) .. (37,38)}
    i = int(n - 2 - int(sqrt(-8 * k + 4 * n * (n - 1) - 7) / 2.0 - 0.5))
    j = int(k + i + 1 - n * (n - 1) / 2 + (n - i) * ((n - i) - 1) / 2)

    # find the name of the regions
    return region_list[i], region_list[j]


@njit(cache=False)
def _compute_cc_quantities(gen1, gen2, nb_points, is_pseudoDiploid) -> float:
    """
    for a given chromosome, compute the cross-chromosome quantities of interest
    :param gen1: (nb ind x nb snps) unphased genotype for chr 1
    :param gen2: (nb ind x nb snps) unphased genotype for chr 2
    :param nb_points: number of points on which we average the bias

    :returns: ccld, expected_ccld, cov_squared
    """
    sample_size_factor = 1 if is_pseudoDiploid else 2

    ccld = 0
    expected_ccld = 0
    bessel_factor = 0
    s_corr = 0

    total_weight = 0

    # Loop over all pairs of columns
    for _ in range(nb_points):
        index1 = np.random.randint(0, gen1.shape[1])
        index2 = np.random.randint(0, gen2.shape[1])
        valid_snps_x, valid_snps_y, weight = get_valid_xy(gen1[:, index1],
                                                          gen2[:, index2])
        if weight > 0 and valid_snps_x.shape[0] > 1:
            # CCLD
            observation = two_snp_correlation(valid_snps_x, valid_snps_y)
            ccld += observation * weight
            # Expected CCLD (if no admixture is present)
            nx = np.sum(~np.isnan(gen1[:, index1])) * sample_size_factor
            ny = np.sum(~np.isnan(gen2[:, index2])) * sample_size_factor
            expected_ccld += 4. / (nx - 1) * 1. / (ny - 1) * weight
            # Bessel correction factor
            bessel_factor += nx / (nx - 1.) * ny / (ny - 1.) * weight
            # E[Gx2Gy2] - 1 for pseudo-diploid data
            s_corr += (np.mean((valid_snps_x * valid_snps_y * sample_size_factor)**2) / 4. - 1) * weight
            # Updating the weight
            total_weight += weight
    return ccld / total_weight, expected_ccld / total_weight, bessel_factor / total_weight, s_corr / total_weight


@njit(cache=True)
def genetic_distance(index1: int, index2: int, gen_map: np.ndarray) -> float:
    """ Get the distance between to SNPs
    :param gen_map: ndarray representation of the genetic map
    :param index1: (integer) index of snp x
    :param index2: (integer) index of snp y
    :return: distance in Morgan
    """
    return np.abs(gen_map[index1] - gen_map[index2])


@njit(cache=True)
def two_snp_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """ Compute r^2 between x and y
    :param x: (l,) (normalised) values of the genotype at site x
    :param y: (l,) (normalised) values of the genotype as site at y
    :return: r2(x, y)
    """
    n = len(x)
    if n > 1:
        xy = x * y
        ld = 1. / n / (n - 1.) * ((np.sum(xy)) ** 2 - np.sum(xy ** 2))
        return ld
    return 0


def preprocess_genotype(genotype: np.ndarray, maf_filter: float) -> np.ndarray:
    """ Normalise the genotype (0 mean and theoretical variance 1 for each column)
    Note that the variance is normalised by treating the variable as Bernoulli RV, and not by computing the
    empirical variance.
    :param genotype: (nb ind x nb snps)
    :param maf_filter: consider snp whose frequency satisfies |f-0.5|<maf_filter
    :return: (nb ind x nb snps) with  variance and 0 mean, nan for missing values
    """
    gen = genotype.copy()

    freq = np.nanmean(genotype, axis=0) / 2.
    # Apply MAF criteria ( must not be further away from 0.5 than the MAF )
    gen[:, np.abs(freq - 0.5) > np.abs(maf_filter - 0.5)] = np.nan
    # normalise
    gen -= freq * 2
    gen /= np.sqrt(freq * (1 - freq) * 2)

    return gen


def load_files(prefix):
    """ Load binary plink files
    :param prefix: prefix of the files (prefix.bed, bim, fam must exist)
    :return : genotype (bed file), map (location of each SNP in Morgan)
    """
    genotype_object = pdp.read_plink1_bin(prefix)
    return genotype_object.values, genotype_object.cm.values / 100.


@njit(cache=True)
def get_valid_xy(x, y):
    """ Return the non-missing entries of xy, together with the percentage of those values if return_percentage is True
    :param x: nb_individual, normalised value of SNP x
    :param y: nb_individual, normalised value of SNP y
    :return: valid entries of x, valid entries of y, fraction of valid entries (if return_percentage is True)
    """
    x = x.ravel()
    y = y.ravel()
    selected_index = np.isfinite(x * y)
    valid_fraction = (np.sum(selected_index) + 0.0) / len(x)
    return x[selected_index], y[selected_index], valid_fraction


@njit(cache=True)
def get_bin_index(u: float, bins: np.ndarray):
    """ Get the index of the bin which encompasses the genetic distance u
    :param u: scalar distance in Morgan
    :param bins: n x 2 ndarray (bin_start, bin_end)
    :return: index of the first bin containing u, None if no bin contains u
    """
    in_bin = ((u >= bins[:, 0]) * (u < bins[:, 1]))
    if np.any(in_bin):
        return int(np.argmax(in_bin))
    else:
        return None


def save_ld_results(config: ConfigParser, region: str, r2: np.ndarray, weights, bins: np.ndarray):
    """ Save the LD results in a file. The output file contains 3 columns, "BIN_FROM", "BIN_TO", "R2", "Weight"
    :param config: see the example config file
    :param region : name of the current genetic region
    :param r2: average r2 within each bin
    :param weights: total weight for the bin
    :param bins: nb_bins x 2 ndarray (bin_from, bin_to)
    """
    output_folder = get_ld_output_folder(config)
    save_in = output_folder + region + ".r2"
    to_be_saved = pd.DataFrame(columns=["BIN_FROM[M]", "BIN_TO[M]", "R2", "WEIGHT"])
    to_be_saved["BIN_FROM[M]"] = bins[:, 0]
    to_be_saved["BIN_TO[M]"] = bins[:, 1]
    to_be_saved["R2"] = r2
    to_be_saved["WEIGHT"] = weights
    to_be_saved.to_csv(save_in)


def get_ld_output_folder(config: ConfigParser):
    output_folder = config["CONFIG"]["output_folder"] + "/LD/"
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    return output_folder
