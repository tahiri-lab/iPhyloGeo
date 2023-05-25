import yaml


def read_config():
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config


def update_config(new_config):
    with open('config/config.yaml', 'w') as f:
        yaml.dump(new_config, f)


def update_inputYaml(feature_name, value):
    # Load the YAML file
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Update the values
    config['input'][feature_name] = value

    # Write the updated dictionary back to the YAML file
    with open('config/config.yaml', 'w') as file:
        yaml.dump(config, file)


def update_paramsYaml(feature_name, value):
    # Load the YAML file
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Update the values
    config['params'][feature_name] = value

    # Write the updated dictionary back to the YAML file
    with open('config/config.yaml', 'w') as file:
        yaml.dump(config, file)


def update_thresholdsYaml(feature_name, value):
    # Load the YAML file
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Update the values
    config['thresholds'][feature_name] = value

    # Write the updated dictionary back to the YAML file
    with open('config/config.yaml', 'w') as file:
        yaml.dump(config, file)


def update_seqinfoYaml(feature_name, value):
    # Load the YAML file
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Update the values
    config['seqinfo'][feature_name] = value

    # Write the updated dictionary back to the YAML file
    with open('config/config.yaml', 'w') as file:
        yaml.dump(config, file)
