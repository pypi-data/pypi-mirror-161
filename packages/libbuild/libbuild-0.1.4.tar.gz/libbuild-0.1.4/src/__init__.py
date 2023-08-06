import os
import sys
import subprocess

""" This is the official build library file. This is also a part of PyBuild. """

def cmd(command):
    subprocess.run(command, shell=True)
