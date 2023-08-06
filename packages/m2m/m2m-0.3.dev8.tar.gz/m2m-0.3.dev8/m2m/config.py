import os
import yaml

import m2m.path

DEFAULT_CONFIG_PATH = "~/.m2m/config.yml"

def get_config(config_path=None):
    if config_path is None:
        if 'M2M_CONFIG_PATH' in os.environ:
            config_path = os.environ['M2M_CONFIG_PATH']
        else:
            config_path = DEFAULT_CONFIG_PATH

    config_path = m2m.path.expand_path(config_path)

    with open(config_path) as stream:
        config_dict = yaml.safe_load(stream)

    return config_dict, config_path