# standard lib imports
import colorama as color

color.init()

from collections import defaultdict
import os, re, sys, time
import unittest

# test package imports
import boakboak.src.settings as sts
import boakboak.src.params as params


# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.boakInstance = params.Params()
        cls.verbose = 0

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        try:
            pass
        except Exception as e:
            print(f"UnitTest, tearDownClass, e: {e}")

    def test_get_params(self, *args, **kwargs):
        """
        finds boakboak runtime params.yml files and extracts paramsters from them
        returns a dict of parameters

        """
        # case: test.yml exits in boakboak/apps/*, therefore test.yml params dict is returned
        b = params.Params()
        ps = b.get_params(*args, apps=["test"], **kwargs)
        self.assertEqual(ps["test"].get("name"), "test_boakboak")

        # case: boakboak.yml NOT existing in boakboak/apps/*, hence boakboak.yml params dict
        # is returned from boakboak app folder
        b = params.Params()
        ps = b.get_params(*args, apps=["boakboak"], **kwargs)
        self.assertEqual(ps["boakboak"]["name"], "boakboak")

    def test_get_params_file(self, *args, **kwargs):
        ### finds parameter fieles by serching throu relevant boakboak/app folders and packages
        b = params.Params()
        files = b.get_params_file("boakboak", sts.appsParamsDir)
        self.assertEqual(files, (sts.os_sep(sts.appBasePath), "boakunittest.yml"))

    def test_find_package_params_file(self, *args, **kwargs):
        ### finds parameter fieles by serching throu relevant boakboak/app folders and packages
        b = params.Params()
        files = self.boakInstance.find_package_params_file("boakboak", *args, **kwargs)
        self.assertEqual(files, (sts.os_sep(sts.appBasePath), "boakunittest.yml"))


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
