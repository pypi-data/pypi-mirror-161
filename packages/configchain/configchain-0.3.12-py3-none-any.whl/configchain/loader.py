import os
from os import path

from .types import ConfigFile


class FileLoader:
    def __init__(self, workdir: str = None):
        if workdir is None:
            workdir = os.getcwd()
        self.workdir = workdir

    def key(self, file):
        return path.abspath(file)

    def read(self, relative_path):
        with open(relative_path, "r") as fh:
            return fh.read()

    def _snippet(self):
        def _read_file(self, file: ConfigFile) -> str:
            key = path.abspath(file)
            if key in self.keys():
                return None
            with open(file, "r") as fh:
                return fh.read()
