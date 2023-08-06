from configparser import ConfigParser
import os
from hapne.utils import get_region, get_regions


def build_hist(config: ConfigParser):
    for ii in range(get_regions.shape[0]):
        build_hist_in_parallel(ii, config)


def build_hist_in_parallel(region_index: int, config: ConfigParser):
    region = get_region(region_index)
    name = region["NAME"]

    ibd_folder = config.get("CONFIG", "ibd_files")
    hist_folder = get_hist_folder(config)
    # needs for on macos instead of zcat *
    command = f"for IBDFILE in `ls {ibd_folder}/{name}.*.ibd.gz`" \
        + "; do " \
        + "gunzip -c $IBDFILE; " \
        + "done | " \
        + "awk -F\"\\t|_\" '{l=sprintf(\"%d\", 2*$12); c[l]++;} END{ for (i=1; i<=40; i++) " \
        + "print i/2/100 \"\\t\" (i+1)/2/100 \"\\t\" 0+c[i]; }'" \
        + f"> {hist_folder}/{name}.ibd.hist"
    os.system(command)


def get_hist_folder(config: ConfigParser):
    output_folder = config.get("CONFIG", "output_folder") + "/IBD"
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)
    return output_folder
