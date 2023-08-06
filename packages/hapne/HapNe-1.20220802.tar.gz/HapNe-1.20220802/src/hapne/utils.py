import pkg_resources
import pandas as pd
import numpy as np
from configparser import ConfigParser
from os.path import exists


def get_regions():
    """
    read the regions files
    :return: pandas dataframe
    """
    stream = pkg_resources.resource_stream("hapne", 'files/regions.txt')
    return pd.read_csv(stream, sep="\t")


def get_region(region_index: int):
    regions = get_regions()
    return regions.iloc[region_index]


def get_bins():
    """ Provide the bins for which we want to perform the analysis part
    NEXT : Read from a file instead
    """
    bin_borders = np.linspace(0.01, 0.1, 19)
    bins = np.zeros([18, 2])
    bins[:, 0] = bin_borders[:-1]
    bins[:, 1] = bin_borders[1:]
    return bins


def get_age_from_anno(config: ConfigParser):
    """
    Note that this method should be called after having converted the vcf into
    HapNe's input format, so that the individuals who did not pass the
    quality test are not included in the samples.age file.

    If a .fam file is found, the individuals from this file will be used,
    otherwise the individuals from the .keep file will be included.
    """
    years_per_gen = 29
    anno_file = pd.read_csv(config.get("CONFIG", "anno_file"), sep="\t")

    individuals_in_study = get_individuals_in_study(config)
    individuals_in_study.columns = [anno_file.columns[1]]
    anno = pd.merge(individuals_in_study, anno_file, how='inner', on=[anno_file.columns[1]]).values
    col_bp = config.getint("CONFIG", "anno_bp_column", fallback=8)
    col_stdbp = config.getint("CONFIG", "anno_bp_column", fallback=col_bp + 1)
    age_from = ((anno[:, col_bp] - 2 * anno[:, col_stdbp]) / years_per_gen).reshape((-1, 1)).astype(int)
    age_to = ((anno[:, col_bp] + 2 * anno[:, col_stdbp]) / years_per_gen).reshape((-1, 1)).astype(int)
    to_save = pd.DataFrame(np.concatenate((age_from, age_to), axis=1), columns=["FROM", "TO"])
    save_as = config["CONFIG"].get("output_folder")
    popname = config["CONFIG"].get("population_name")
    save_as += f"/DATA/{popname}.age"
    to_save.to_csv(save_as, index=False)


def get_individuals_in_study(config: ConfigParser):
    """
    See get_age_from_anno
    """
    output_folder = config["CONFIG"].get("output_folder")
    # Check if a .fam file is present
    genotypes = config["CONFIG"].get("genotypes", fallback=None)
    if genotypes is None:
        genotypes = f"{output_folder}/DATA/GENOTYPES"
    fam_path = f"{genotypes}/{get_region(1)['NAME']}.fam"
    if exists(fam_path):
        fam_file = pd.read_csv(fam_path, header=None, sep=" ")
        df = pd.DataFrame(fam_file[1])
        df = df.applymap(lambda x: '_'.join(str(x).split('_')[1:]))
        return df
    else:
        keep_inds = pd.read_csv(config.get("CONFIG", "keep"), header=None)
        return keep_inds


class Bijection:
    def __init__(self):
        x = np.random.randint(1, 10)
        try:
            assert np.abs(self.forward(self.backward(x)) - x) < 1e-9
            assert np.abs(self.backward(self.forward(x)) - x) < 1e-9
        except AssertionError:
            print("The bijection is not set properly")
            raise

    @staticmethod
    def forward(x):
        return x

    @staticmethod
    def backward(x):
        return x


class LogBijection(Bijection):
    @staticmethod
    def forward(x):
        return np.log(x)

    @staticmethod
    def backward(x):
        return np.exp(x)


def smoothing(n: np.ndarray, transformer: Bijection, window: int) -> np.ndarray:
    """ Apply a rolling window to transform(n) and project it back to the original space
    the first and last window//2 elements are unchanged
    Args:
        n : function
        transformer: apply the rolling mean to forward(n)
        window : length of the window in the rolling averaging process
    Retuns:
        smoothed_n: a smoother version of n
    """
    n = n.ravel()
    w = np.ones(window)
    y = transformer.forward(n)
    y_smooth = np.convolve(y, w, 'valid') / window
    y[window // 2:-window // 2 + 1] = y_smooth
    return transformer.backward(y)
