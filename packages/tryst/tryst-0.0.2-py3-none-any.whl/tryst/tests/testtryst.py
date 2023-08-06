# testtryst.py
# Copyright 2021 Travis Gates

# One's body is inviolable, subject to one's own will alone.

# This file is part of Tryst.

# Tryst is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Tryst is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Tryst.  If not, see <https://www.gnu.org/licenses/>.

import json
import unittest
from tryst import Tryst
from tryst import Option
import os

# testcase = unittest.FunctionTestCase(testFunc,
#                                 setUp=setupFunc,
#                                 tearDown=teardownFunc)

class TestInterpret(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Whatever setup should happen before any tests in this class
        pass

    @classmethod
    def tearDownClass(self):
        # Whatever cleanup should occur after all tests in this class
        pass

    def setUp(self):
        # Setup that will be performed before EACH test* function
        self.tryst = Tryst()

    def tearDown(self):
        # Cleanup performed after EACH test* function
        pass

    def add_default_options(self):
        vopt = Option("verbose", "Speak!", "v")
        veropt = Option("version", "gimme dat ver doe")
        hopt = Option("help", "help me for the love of all!", "?")
        self.tryst.add_option(vopt)
        self.tryst.add_option(veropt)
        self.tryst.add_option(hopt)
        return [vopt, veropt, hopt]

    def test_interpret_noinputs(self):
        self.tryst.interpret(["testtryst.py"])      # "false" arg0 i.e. name of script

        self.assertEqual(len(self.tryst.options), 0, "implementer defined no options")
        self.assertEqual(len(self.tryst.optionarguments), 0, "implementer defined no optionarguments")
        self.assertEqual(len(self.tryst.userargs), 0, "user supplied no args")
        self.assertEqual(len(self.tryst.useroptions), 0, "user supplied no options")
        self.assertEqual(len(self.tryst.useroptionarguments), 0, "user supplied no optargs")

    def test_interpret_oneopt(self):
        vopt = Option("verbose", "Speak!", "v")
        self.tryst.add_option(vopt)

        self.tryst.interpret(["tryst.py", "-v"])

        self.assertEqual(len(self.tryst.options), 1, "implementer defined one option")
        self.assertEqual(len(self.tryst.optionarguments), 0, "implementer defined no optionarguments")
        self.assertEqual(len(self.tryst.userargs), 0, "user supplied no args")
        self.assertEqual(len(self.tryst.useroptions), 1, "user supplied one option")
        self.assertEqual(len(self.tryst.useroptionarguments), 0, "user supplied no optargs")
        
    def test_interpret_all_verbose_opts(self):
        defopts = self.add_default_options()

        self.tryst.interpret(["tryst.py", "--version", "--verbose", "--help"])

        self.assertEqual(len(self.tryst.options), 3, "implementer defined 3 options")
        self.assertEqual(len(self.tryst.optionarguments), 0, "implementer defined 0 option arguments")
        self.assertEqual(len(self.tryst.useroptions), 3, "user specified 3 user options")
        self.assertTrue(defopts[0] in self.tryst.useroptions, "user specified verbose option")
        self.assertTrue(defopts[1] in self.tryst.useroptions, "user specified version option")
        self.assertTrue(defopts[2] in self.tryst.useroptions, "user specified help option")
    
    def test_interpret_all_short_opts(self):
        defopts = self.add_default_options()

        self.tryst.interpret(["tryst.py", "-v", "-?", "--version"])

        self.assertEqual(len(self.tryst.options), 3, "implementer defined 3 options")
        self.assertEqual(len(self.tryst.optionarguments), 0, "implementer defined 0 option arguments")
        self.assertEqual(len(self.tryst.useroptions), 3, "user specified 3 user options")
        self.assertTrue(defopts[0] in self.tryst.useroptions, "user specified verbose option")
        self.assertTrue(defopts[1] in self.tryst.useroptions, "user specified version option")
        self.assertTrue(defopts[2] in self.tryst.useroptions, "user specified help option")

    def test_interpret_doubleshortstack(self):
        defopts = self.add_default_options()

        self.tryst.interpret(["tryst.py", "-v?", "--version"])

        self.assertEqual(len(self.tryst.options), 3, "implementer defined 3 options")
        self.assertEqual(len(self.tryst.optionarguments), 0, "implementer defined 0 option arguments")
        self.assertEqual(len(self.tryst.useroptions), 3, "user specified 3 user options")
        self.assertTrue(defopts[0] in self.tryst.useroptions, "user specified verbose option")
        self.assertTrue(defopts[1] in self.tryst.useroptions, "user specified version option")
        self.assertTrue(defopts[2] in self.tryst.useroptions, "user specified help option")

    def test_interpret_really_long_option(self):
        longopt = Option("this-is-a-really-long-option", "longbottom!")
        self.tryst.add_option(longopt)

        self.tryst.interpret(["tryst.py", "--this-is-a-really-long-option"])

        self.assertEqual(len(self.tryst.options), 1, "implementer defined one option")
        self.assertEqual(len(self.tryst.optionarguments), 0, "implementer defined no optionarguments")
        self.assertEqual(len(self.tryst.userargs), 0, "user supplied no args")
        self.assertEqual(len(self.tryst.useroptions), 1, "user supplied one option")
        self.assertTrue(longopt in self.tryst.useroptions, "user specified really long option")
        self.assertEqual(len(self.tryst.useroptionarguments), 0, "user supplied no optargs")
    
    # Possible Test Scenarios (e.g. functions):
    # no options, no user options
    # no options, some user options
    # options, no user options
    # options, user options
    #   >- options without briefs, user options
    #   >- options with briefs, user options
    #   >- options with briefs, stacked short user options
    # FunctionTestCase allows for a very small and lightweight test case with function pointers

    def test_interpret_optarg(self):
        secsoptarg = Option("seconds", "specify seconds", "s")
        self.tryst.add_option_argument(secsoptarg)

        self.tryst.interpret(["tryst.py", "--seconds=10"])

        self.assertEqual(len(self.tryst.optionarguments), 1, "implementer defined one option argument")
        self.assertEqual(len(self.tryst.useroptionarguments), 1, "user specified one option argument")
        self.assertEqual(len(self.tryst.options), 0, "implementer defined no options")
        self.assertEqual(int(self.tryst.useroptionarguments.get(secsoptarg)), 10, "user specified --seconds=10")

    def test_interpret_longoptarg(self):
        secsoptarg = Option("user-seconds", "specify seconds", "s")
        self.tryst.add_option_argument(secsoptarg)

        self.tryst.interpret(["tryst.py", "--user-seconds=10"])

        self.assertEqual(len(self.tryst.optionarguments), 1, "implementer defined one option argument")
        self.assertEqual(len(self.tryst.useroptionarguments), 1, "user specified one option argument")
        self.assertEqual(len(self.tryst.options), 0, "implementer defined no options")
        self.assertEqual(int(self.tryst.useroptionarguments.get(secsoptarg)), 10, "user specified --user-seconds=10")

    def test_interpret_shortoptarg(self):
        secsoptarg = Option("seconds", "specify seconds", "s")
        self.tryst.add_option_argument(secsoptarg)

        self.tryst.interpret(["tryst.py", "-s=10"])

        self.assertEqual(len(self.tryst.optionarguments), 1, "implementer defined one option argument")
        self.assertEqual(len(self.tryst.useroptionarguments), 1, "user specified one option argument")
        self.assertEqual(len(self.tryst.options), 0, "implementer defined no options")
        self.assertEqual(int(self.tryst.useroptionarguments.get(secsoptarg)), 10, "user specified --seconds=10")

    def test_interpret_dictarg(self):
        someopsh = Option("someotherarg", "does something else")
        self.tryst.add_option(someopsh)
        dictarg = {}
        dictarg["key"] = "value"
        dictarg["key2"] = True
        
        self.tryst.interpret(["tryst.py", dictarg, "--someotherarg"])

        self.assertEqual(len(self.tryst.useroptions), 1, "user supplied one option")
        self.assertEqual(len(self.tryst.userargs), 1, "user supplied one arg")
        self.assertTrue(isinstance(self.tryst.userargs[0], dict), "user supplied one user arg that should have type dict")

    def test_interpret_boolarg(self):
        boolthing = True
        self.tryst.interpret(["tryst.py", boolthing])

        self.assertEqual(len(self.tryst.userargs), 1, "user supplied one arg")
        self.assertTrue(isinstance(self.tryst.userargs[0], bool), "user-supplied arg was of type bool")
        self.assertEqual(self.tryst.userargs[0], True, "user-supplied bool arg was True")

    def test_interpret_intarg(self):
        intthing = 7
        self.tryst.interpret(["tryst.py", intthing])

        self.assertEqual(len(self.tryst.userargs), 1, "user supplied one arg")
        self.assertTrue(isinstance(self.tryst.userargs[0], int), "user-supplied arg was of type int")
        self.assertEqual(self.tryst.userargs[0], 7, "user-supplied int arg was 7")

    def test_interpret_floatarg(self):
        floatthing = 18.5
        self.tryst.interpret(["tryst.py", floatthing])

        self.assertEqual(len(self.tryst.userargs), 1, "user supplied one arg")
        self.assertTrue(isinstance(self.tryst.userargs[0], float), "user-supplied arg was of type float")
        self.assertEqual(self.tryst.userargs[0], 18.5, "user-supplied int arg was 18.5")
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class TestTrystContext(unittest.TestCase):
    def setUp(self):
        self.tryst = Tryst()
    
    def test_context_viapython(self):
        self.tryst.context("tryst.py")

        self.assertIsNotNone(self.tryst.workdir)
        self.assertEqual(self.tryst.workdir, os.path.normpath(os.getcwd()))
        self.assertIsNotNone(self.tryst.appdir)
        self.assertEqual(self.tryst.appdir, "")

    def test_context_viapythonabspath(self):
        abbypath = os.path.normpath(os.path.abspath(os.getcwd()))
        abbypath = os.path.join(abbypath, "tryst.py")
        self.tryst.context(abbypath)

        self.assertIsNotNone(self.tryst.workdir)
        self.assertEqual(self.tryst.workdir, os.path.normpath(os.getcwd()))
        self.assertIsNotNone(self.tryst.appdir)
        self.assertEqual(self.tryst.appdir, os.path.abspath(os.getcwd()))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TODO: add tests to ensure that specifying a tryst.config before calling e.g.
# tryst.get_config_value() allows for proper 'overriding' of config
class TestTrystConfig(unittest.TestCase):
    def setUp(self):
        # Setup that will be performed before EACH test* function
        self.tryst = Tryst()

    def make_config_file(self):
        configdata = {"egkey": "egval"}
        configpath = "tempconfig.json"
        with open(configpath, 'w') as configfile:
            json.dump(configdata, configfile, indent=4, sort_keys=True)
    
    def cleanup_config_file(self):
        if os.path.isfile("tempconfig.json"):
            os.remove("tempconfig.json")

    def test_config_pythonvalid(self):
        self.make_config_file()

        egval = self.tryst.get_config_value("egkey", configfile="tempconfig.json")
        self.assertEqual(egval, "egval", "egkey was set to egval")
        self.cleanup_config_file()

    def test_config_pythoninvalidkey(self):
        self.make_config_file()

        egval = self.tryst.get_config_value("fakekey", configfile="tempconfig.json")
        self.assertIsNone(egval, "fakekey is not present")
        self.cleanup_config_file()

    def test_config_pythonnoconfigfile(self):
        egval = self.tryst.get_config_value("fakekey", configfile="tempconfig.json")
        self.assertIsNone(egval, "fakekey is not present")

    def test_config_pythongivendefault(self):
        egval = self.tryst.get_config_value("fakekey", "notthere", configfile="tempconfig.json")
        self.assertEqual(egval, "notthere", "fakekey is not present")

    def test_config_set_before_get(self):
        self.make_config_file()
        man_config = {}
        man_config["somekey"] = "someval"
        self.tryst._config = man_config
        
        retval = self.tryst.get_config_value("somekey")
        
        self.assertIsNotNone(retval)
        self.assertEqual(retval, "someval", "config[\"somekey\"] should = someval")

        self.cleanup_config_file()
    
    def test_config_set_before_consort(self):
        self.make_config_file()
        man_config = {}
        man_config["somekey"] = "someval"
        self.tryst._config = man_config

        self.tryst.consort(["tryst.py", "a"])

        retval = self.tryst.get_config_value("somekey")
        self.assertEqual(len(self.tryst.userargs), 1, "user supplied 1 arg")
        self.assertIsNotNone(retval)
        self.assertEqual(retval, "someval", "config should contain somekey with value someval")

        self.cleanup_config_file()

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#----------------------------------------
if __name__ == "__main__":
    # This basically instructs the Python package unittest to do all its work --
    # assemble test cases into a suite and run them.
    unittest.main()
#----------------------------------------
