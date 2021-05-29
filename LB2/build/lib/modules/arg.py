import sys 
import argparse
import os
import configparser


def read_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    ifr = config.get("Settings", "ifr") 
    ofr = config.get("Settings", "ofr")
    ifl = config.get("Settings", "ifl") 
    ofl = config.get("Settings", "ofl")

    args = {
        'ifr': ifr,
        'ofr': ofr,
        'ifl': ifl,
        'ofl': ofl,
    }

    return args


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-ifr', help="input format", default="toml")
    parser.add_argument('-ofr', help="output format", default="yaml")
    parser.add_argument ('-ifl', help="input file", default="docs/input.toml")
    parser.add_argument('-ofl', help="output file", default="output/output.yaml")
    parser.add_argument('-c', '--config', help="config file path")
    return parser


def check_validation(ifr, ofr, ifl, ofl):
    if (not ifr) and (not ofr) and (not ifl) and (not ofl) :
        return

    real_form1 = get_format(ifl)
    form1 = ifr

    real_form2 = get_format(ofl)
    form2 = ofr

    if (real_form1 != form1 or real_form2 != form2):
        raise Exception("Check formats!!!")
    elif (os.stat(ifl).st_size == 0):
        raise Exception('Input file has no data!')




def get_format(str):
    for i in range(len(str) - 1, 0, -1):
        if (str[i - 1] == '.'):
            return str[i:]
