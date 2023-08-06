# -*- coding: utf-8 -*-
from yabs_test import __version__


def run():
    print(f"yabs_test {__version__}")
    print("This is a dummy project for the yabs release tool.")
    print("See https://github.com/mar10/yabs-test")
    return 42


# Script entry point
if __name__ == "__main__":
    # Just in case...
    from multiprocessing import freeze_support

    freeze_support()

    run()
