from configparser import ConfigParser
from hapne.backend.HapNe import HapNe


def hapne_ld(config: ConfigParser):
    config["CONFIG"]["method"] = "ld"
    hapne = HapNe(config)
    hapne.fit()


def hapne_ibd(config: ConfigParser):
    config["CONFIG"]["method"] = "ibd"
    hapne = HapNe(config)
    hapne.fit()
