import os
import unittest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, "deveba"))

from githandlertestcase import GitRepoTestCase, GitHandlerTestCase
from configtestcase import ConfigTestCase

def main():
    unittest.main()

if __name__ == "__main__":
    main()
# vi: ts=4 sw=4 et
