import glob
import os
import yaml 

def yaml_load():
    with open("config.yaml") as stream:
        param = yaml.safe_load(stream)
    return param

def get_path(dir, extension='csv'):
    """
    Return path files on dir
    """
    all_path = [i for i in glob.glob(dir + r'\*.{}'.format(extension))]

    return all_path

def get_filename(path):
    """
    Return filename from path
    """
    filename = os.path.splitext(os.path.basename(path))[0]

    return filename