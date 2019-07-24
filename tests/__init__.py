import unittest
import pandas
import os
import json


class Base(unittest.TestCase):
    @staticmethod
    def fixtures(name):
        with open('fixtures/' + name, 'r') as input:
            input_file = input.read()
        return input_file

    @staticmethod
    def path(name):
        return os.path.join(os.getcwd(), 'fixtures', name)

    @staticmethod
    def read_input_csv(input_path, **kwargs):
        return pandas.read_csv(input_path,  **kwargs)

    @staticmethod
    def remove_files_from(path):
        file_list = os.listdir(path)
        for filep in file_list:
            file_path = os.path.join(path, filep)
            os.unlink(file_path)

    @staticmethod
    def get_json(filepath):
        with open(filepath) as f:
            expected_result = json.load(f, parse_int=int())
            f.close()
        return expected_result

    @staticmethod
    def compare_dataframe(src, dest):
        for c in dest.columns:
            src_list = src[c].tolist()
            dest_list = dest[c].tolist()
            for r in dest_list:
                if r not in src_list:
                    print(r)

            assert all([r in src_list for r in dest_list])


class TestCase(Base):
    basepath = os.getcwd()
