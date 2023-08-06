from configparser import ConfigParser
import os.path


def get_config_data(file_path, section_name):
    reader = ConfigParser()
    reader.read(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError
    return reader[section_name]
