# testmisc.py
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

class TestTryst(unittest.TestCase):
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

    def testlistremoval(self):
        thing3 = {}
        thing3["key"] = "value"
        thing3["key2"] = True
        things = ["thing1", "thing2", thing3]

        # print("before removal: " + str(things))
        for thing in things:
            if isinstance(thing, dict):
                things.remove(thing)
        # print("after removal: " + str(things))

        pass

#----------------------------------------
if __name__ == "__main__":
    # This basically instructs the Python package unittest to do all its work --
    # assemble test cases into a suite and run them.
    unittest.main()
#----------------------------------------