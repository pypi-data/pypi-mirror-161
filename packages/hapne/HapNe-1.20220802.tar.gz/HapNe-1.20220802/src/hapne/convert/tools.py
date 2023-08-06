from configparser import ConfigParser

import hapne.convert.mathii_scripts.py3Eigenstrat as pyEigenstrat
import os
import pandas as pd
from hapne.utils import get_region, get_regions


def eigenstrat2vcf(config: ConfigParser) -> None:
    """
    Convert Eigenstrat files to VCF format.
    :param config: ConfigParser object with the following sections:
    """
    # Get the config parameters
    eigen_root = config.get("CONFIG", "eigen_root")
    vcf_file = get_vcf_location(config) + ".vcf"
    keep = config.get("CONFIG", "keep", fallback=None)

    if keep is None:
        inds = None
    else:
        inds = pd.read_csv(keep, header=None)[0].tolist()

    conversion = {2: "0/0", 1: "0/1", 0: "1/1", 9: "./."}

    data = pyEigenstrat.load(eigen_root, inds=inds)
    header = "##fileformat=VCFv4.0\n" \
             "##source=eigenstrat2vcf.py\n" \
             "##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n" \
             "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(data.ind["IND"])

    with open(vcf_file, "w") as f:
        f.write(header)
        for ii, d in enumerate(data):
            this_snp = data.snp[ii]
            line = "\t".join([this_snp["CHR"], str(this_snp["POS"]), this_snp["ID"],
                              this_snp["REF"], this_snp["ALT"], "100", "PASS", ".", "GT"])
            line = line + "\t" + "\t".join([conversion[x] for x in d])
            f.write("\n" + line)
    command = f"plink --vcf {vcf_file} \
        --export vcf \
        --const-fid \
        --out {get_vcf_location(config)}_tmp \
        --mind 0.8 \
        --geno 0.8 "
    os.system(command)
    # execute the gzip command to compress the file
    os.system(f"mv {get_vcf_location(config)}_tmp.vcf {vcf_file}")
    os.system("gzip " + vcf_file)

    # create the map from the .snp file
    save_maps_in = config.get("CONFIG", "output_folder") + "/DATA"
    for _, region in get_regions().iterrows():
        chr = region["CHR"]
        chr_from = region["FROM_BP"]
        chr_to = region["TO_BP"]

        bim = pd.read_csv(eigen_root + ".snp", header=None, delim_whitespace=True)
        bim = bim[bim[1] == chr]
        map = bim[[3, 2, 2]]
        map.columns = ["position", "COMBINED_rate(cM/Mb)", "Genetic_Map(cM)"]
        map.loc[:, "Genetic_Map(cM)"] = map.loc[:, "Genetic_Map(cM)"] * 100
        map.loc[:, "COMBINED_rate(cM/Mb)"] = map.loc[:, "COMBINED_rate(cM/Mb)"] * 100
        map.to_csv(save_maps_in + f"/chr{chr}.from{chr_from}.to{chr_to}.map", sep=" ", index=False)


def get_vcf_location(config: ConfigParser) -> str:
    """
    return the path where the vcf file must be saved/loaded
    Note that the extension .vcf(.gz) is not added
    """
    vcf_file = config.get("CONFIG", "vcf_file", fallback=None)
    if vcf_file is None:
        output_folder = config.get("CONFIG", "output_folder") + "/DATA"
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        population = config.get("CONFIG", "population_name", fallback="population")
        vcf_file = output_folder + f"/{population}"
    return vcf_file


def get_map_location(config: ConfigParser, fallback: str):
    location = config.get("CONFIG", "map", fallback=fallback)
    return location


def split_convert_vcf(config: ConfigParser) -> None:
    """
    Split the VCF file into multiple bed files.
    :param config: ConfigParser object with the following sections:
    """
    # Get the config parameters
    for ii in range(39):
        split_convert_vcf_in_parallel(ii, config)


def split_convert_vcf_in_parallel(index: int, config: ConfigParser):
    # check if ii in between 0 and 38
    if not (0 <= index < 39):
        raise ValueError(f"index must be between 0 and 38, but index={index}")

    save_in = config.get("CONFIG", "output_folder") + "/DATA/GENOTYPES"
    if not os.path.isdir(save_in):
        os.makedirs(save_in)

    region = get_region(index)
    chr = region["CHR"]
    chr_from = region["FROM_BP"]
    chr_to = region["TO_BP"]

    eigen_root = config.get("CONFIG", "eigen_root", fallback=None)
    keep = None
    keep_command = ""
    # The filtering option is carried out when converting eigenstrat files to vcf
    if eigen_root is not None:
        keep = config.get("CONFIG", "keep", fallback=None)
    if keep is not None:
        keep_command = f"--keep {keep}"
    # run plink to convert
    vcf_loc = get_vcf_location(config)
    fallback = config.get("CONFIG", "output_folder") + f"/DATA/chr@.from{chr_from}.to{chr_to}.map"
    map_loc = get_map_location(config, fallback)
    command = f"plink --vcf {vcf_loc}.vcf.gz \
            --make-bed \
            {keep_command} \
            --out {save_in}/{region['NAME']} \
            --cm-map {map_loc} \
            --chr {chr} \
            --from-bp {chr_from} \
            --to-bp {chr_to} \
            --const-fid \
            --threads 1 \
            --memory 2048 \
            --maf 0.249 \
            --snps-only \
            --geno 0.8 "
    os.system(command)


def vcf2fastsmc(config: ConfigParser) -> None:
    """
    Split the VCF file into multiple haps files, ready to be analysed by FastSMC
    :param config: ConfigParser object
    """
    for ii in range(39):
        vcf2fastsmc_in_parallel(ii, config)


def vcf2fastsmc_in_parallel(index: int, config: ConfigParser) -> None:
    # check if ii in between 0 and 38
    if not (0 <= index < 39):
        raise ValueError(f"index must be between 0 and 38, but index={index}")

    save_in = config.get("CONFIG", "output_folder") + "/DATA/GENOTYPES"
    if not os.path.isdir(save_in):
        os.makedirs(save_in)

    region = get_region(index)
    chr = region["CHR"]
    chr_from = region["FROM_BP"]
    chr_to = region["TO_BP"]
    keep = config.get("CONFIG", "keep", fallback=None)
    if keep is not None:
        keep_command = f"--keep {keep}"

    # run plink to convert
    vcf_loc = get_vcf_location(config)
    command = f"plink2 --vcf {vcf_loc}.vcf.gz \
            --export haps bgz \
            {keep_command} \
            --out {save_in}/{region['NAME']} \
            --chr {chr} \
            --from-bp {chr_from} \
            --to-bp {chr_to} \
            --const-fid \
            --threads 1 \
            --memory 2048 \
            --maf 0.01 \
            --snps-only \
            --max-alleles 2"
    os.system(command)
