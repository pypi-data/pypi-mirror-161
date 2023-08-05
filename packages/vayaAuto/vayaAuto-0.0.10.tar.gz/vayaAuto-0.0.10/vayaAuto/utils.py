import yaml
import json
from re import sub, search
import configparser


def get_vaya_config():
    with open("../vaya_configuration/vaya_config.yaml", "r") as stream:
        try:
            vaya_config = yaml.safe_load(stream)
        except Exception as exc:
            print(exc)
        return vaya_config


def convert_ini_to_yaml(ini_path, output):
    def camel_case(s):
        s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
        return ''.join([s[0].lower(), s[1:]])
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ini_path)
    config_dict = {}

    with open(output, 'w') as file:
        for section in config.sections():
            config_dict[section] = {}
            section_dict = {section: {}}
            for option in config[section]:

                if '_' not in option:
                    f_name = [char for char in option if char != '_']
                    f_name[0] = f_name[0].lower()
                    f_name = ''.join(f_name)
                else:
                    split_name = option.split('_')
                    try:
                        split_name.remove('Enum')
                    except ValueError:
                        pass
                    try:
                        split_name.remove('Bool')
                    except ValueError:
                        pass
                    s = split_name[0] + '_' + '_'.join(split_name[1:])
                    f_name = camel_case(s)

                config_dict[section][option] = f_name

        documents = yaml.dump(config_dict, file, indent=4)
    print('ini converted')


def convert_ini_to_json(ini_path, output):

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(ini_path)
    config_dict = {}

    with open(r'vaya_configuration/vaya_config.json', 'w') as file:
        for section in config.sections():
            config_dict[section] = {}
            section_dict = {section: {}}
            for option in config[section]:
                try:
                    value = config.getfloat(section, option)
                except:
                    try:
                        value = config.getboolean(section, option)
                    except:
                        try:
                            value = config.get(section, option)
                        except:
                            pass
                config_dict[section][option] = value
                section_dict[section][option] = str(type(value))
        documents = json.dump(config_dict, file, indent=4)
    print('ini converted')


def generate_config(ini_path):
    config = configparser.ConfigParser()
    config.read(ini_path)
    section_list = []

    for section in config.sections():
        section_dict = {section: []}
        for option in config[section]:
            section_dict[section].append(option)
        section_list.append(section_dict)
    return section_list


def search_regex_and_return_str(ptrn, string_to_search, padding=(0, 0)):
    match = search(ptrn, string_to_search)
    if match:
        indexes = match.span()
        front_pad, back_pad = padding
        return string_to_search[indexes[0] + front_pad:indexes[1] - back_pad]
    return ''

