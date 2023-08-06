# testjsonhelper.py
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

import unittest
from tryst import JSONHelper as jelper
import os

class TestJSONHelper(unittest.TestCase):
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
        pass

    def tearDown(self):
        # Cleanup performed after EACH test* function
        # When writing new test functions, if your test will create a file,
        # create jval.json to have it cleaned up by this tearDown function
        if os.path.isfile("jval.json"):
            os.remove("jval.json")

    def test_save_invalidfilepath(self):
        jsondata = { "key": "value" }
        invalidpath = os.path.join("C:", "noonenamesafolderthis", "jval.json")
        saveres = jelper.save(invalidpath, jsondata)
        # Check that the file exists
        self.assertFalse(saveres)
        self.assertFalse(os.path.exists(invalidpath))
        self.assertFalse(os.path.isfile(invalidpath))

    def test_save_validdict(self):
        jsondata = { "key": "value" }
        jelper.save("jval.json", jsondata)
        # Check that the file exists
        self.assertTrue(os.path.exists("jval.json"))
        self.assertTrue(os.path.isfile("jval.json"))
        # Read the file and validate its contents
        with open("jval.json", "r") as resfile:
            data = resfile.read()

        filestr = '{\n    "key": "value"\n}'
        self.assertEqual(str(data), str(filestr), "file data is wrong")
    
    def test_save_validdict_compact(self):
        jsondata = {"otherkey": "othervalue"}
        jelper.save("jval.json", jsondata, 0, False)

        jstr = '{\n"otherkey": "othervalue"\n}'

        with open("jval.json", "r") as resfile:
            data = resfile.read()
        self.assertEqual(str(data), str(jstr), "data in file is incorrect")

    def test_save_validlist(self):
        jsondata = ["item1", "item2", "item 3"]
        jelper.save("jval.json", jsondata)
        # Check that the file exists
        self.assertTrue(os.path.exists("jval.json"))
        self.assertTrue(os.path.isfile("jval.json"))
        # Read the file and validate its contents
        with open("jval.json", "r") as resfile:
            data = resfile.read()

        filestr = '[\n    "item1",\n    "item2",\n    "item 3"\n]'
        self.assertEqual(str(data), str(filestr), "file data is wrong")

    def test_save_invalidstr(self):
        jsondata = "bob"
        jelper.save("jval.json", jsondata)
        # Check that the file exists
        self.assertTrue(os.path.exists("jval.json"))
        self.assertTrue(os.path.isfile("jval.json"))
        # Read the file and validate its contents
        with open("jval.json", "r") as resfile:
            data = resfile.read()

        filestr = '"bob"'
        self.assertEqual(str(data), str(filestr), "file data is wrong")

    def test_save_invalidint(self):
        jsondata = "1"
        jelper.save("jval.json", jsondata)
        # Check that the file exists
        self.assertTrue(os.path.exists("jval.json"))
        self.assertTrue(os.path.isfile("jval.json"))
        # Read the file and validate its contents
        with open("jval.json", "r") as resfile:
            data = resfile.read()

        filestr = '"1"'
        self.assertEqual(str(data), str(filestr), "file data is wrong")

    def test_load_nofile(self):
        jsonfile = "somefile.json"
        data = jelper.load(jsonfile)

        self.assertEqual(data, {}, "data should be an empty dict")
        self.assertFalse(data, "empty dict should evaluate to false")

        datapoint = data.get("somekey")
        self.assertFalse(datapoint, "value from empty dict should be false")

    def test_tostring_fancy(self):
        jsondata = {"key": "value", "key2": "value"}
        jstr = """{
    "key": "value",
    "key2": "value"
}"""

        resstr = jelper.tostring(jsondata)

        self.assertEqual(str(resstr), str(jstr), "string ain't fancy enough!")

    def test_fromstring_dict(self):
        dic = {"key": "val"}
        dicstr = '{"key": "val"}'

        jdic = jelper.fromstring(dicstr)

        self.assertEqual(dic, jdic, "dicts are incorrect")

    def test_fromstring_list(self):
        litht = ["one", "two", "three"]
        lithtstr = '["one", "two", "three"]'

        jlitht = jelper.fromstring(lithtstr)

        self.assertEqual(litht, jlitht, "lists are incorrect")

    def test_tostring_string(self):
        bob = "bob"
        bobber = jelper.tostring(bob)

        self.assertEqual(bobber, '"bob"', "tostring a string via json gives you an escaped string.")

    def test_tostring_int(self):
        hundo = "100"
        hundor = jelper.tostring(hundo)

        self.assertEqual(hundor, '"100"', "tostring an int via json gives you an escaped int.")

    def test_fromstring_string(self):
        hmm = "hmm"
        hmmer = jelper.fromstring(hmm)

        self.assertIsNone(hmmer, "parsing a string might be bad")

    def test_fromstring_escapedstring(self):
        hmm = '"hmm"'
        hmmer = jelper.fromstring(hmm)

        self.assertEqual("hmm", hmmer, "parsing a string might be bad")

    # testcase = unittest.FunctionTestCase(testFunc,
    #                                 setUp=setupFunc,
    #                                 tearDown=teardownFunc)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":
    # This basically instructs the Python package unittest to do all its work --
    # assemble test cases into a suite and run them.
    unittest.main()
