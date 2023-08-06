# tryst.py
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
# along with tryst.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
import json
from json.decoder import JSONDecodeError
import sys
import os

# Standardized JSONic behavior. @classmethod behaves similarly to C-style "static".
class JSONHelper:
    """Class to deliver consistent JSONic behavior -- saving, loading, to- and from-string conversion.
    """
    @classmethod
    def save(self, filepath, jsondata, indent_=4, sortkeys_=True) -> bool:
        """Save to `filepath` the indicated `jsondata` with specified indentation 
        and sorting. Return success."""
        try:
            with open(filepath, 'w') as jsonfile:
                json.dump(jsondata, jsonfile, indent=indent_, sort_keys=sortkeys_)
            return True
        except FileNotFoundError:
            return False

    @classmethod
    def load(self, filepath):
        """Load data in `filepath` as JSON to a dict; returns {} on failure."""
        jsondata = {}       # return an empty dict which evaluates to None
        try:
            f = open(filepath)
            jsondata = json.load(f)
            f.close()
        except FileNotFoundError:
            pass
        return jsondata

    @classmethod
    def tostring(self, jsondata, indent_=4, sortkeys_=True):
        """Convert `jsondata` to string with specified indentation and sorting."""
        return json.dumps(jsondata, indent=indent_, sort_keys=sortkeys_)
    
    @classmethod
    def fromstring(self, jsondata):
        """Convert `jsondata` to a JSON dictionary; returns None on failure."""
        retval = None
        try:
            retval = json.loads(jsondata)
        except JSONDecodeError:
            pass
        return retval
#================================================================================

class Option:
    """Data class to represent an option or option-argument.
    A debug option is created like so: `Option("debug", "Displays debug output during execution.", "d")`
    """
    def __init__(self, verbose, description, brief=None):
        """Do not include leading -- with verbose or - with brief identifiers.
        Brief identifiers are optional."""
        self.verbose = verbose
        self.description = description
        self.brief = brief
#================================================================================


class Tryst:
    """Like the rendesvouz of the same name, a tryst is a limited-scope engagement
    with context, parameters, input, and output.
    A Tryst represents a single entanglement of input and code which results in 
    output. Trysts are intended to abstract and simplify the definition of 
    options (switches) and option-arguments, as well as user input which may 
    activate or supply them respectively.
    """
    # TODO: add duplicate checking?
    def add_option(self, option):
        """Add an option as a switch; usage: [-o | --option]"""
        if option not in self.options:
            self.options.append(option)
    #----------------------------------------

    def add_option_argument(self, optionargument):
        """Add an option as an option-argument; usage: [-o=value | --optarg=value]"""
        if optionargument not in self.optionarguments:
            self.optionarguments.append(optionargument)
    #----------------------------------------

    def interpret(self, inputs=None):
        """Interpret specified input. Populates tryst.useroptions &
        tryst.useroptionarguments based on Option objects added via 
        tryst.add_option() and tryst.add_option_argument()."""
        if not inputs:
            inputs = list(sys.argv)

        self.debug("interpret inputs = " + str(inputs))

        userinput = inputs
        if str(inputs[0]).find(self.appname) > -1:  # Ignore the "tryst.py" 0th argument
            userinput = inputs[1:]
        for ui in userinput:
            if not isinstance(ui, str):     # Non-strings are considered userargs; this helps with code-time chaining   
                self.userargs.append(ui)
                userinput.remove(ui)

        # Simpler input; do we return a sub-object that is the results?
        # Return a namedtuple of useropts, useroptargs, userargs?
        self.userargs += [arg for arg in userinput if not str(arg).startswith("-")]

        # Options have either - or -- in front of them
        # - options can be stacked, e.g. -dv is equivalent to -d -v
        # -- options are slug-case, no spaces, e.g. --debug or --whole-row
        # option args can be either, and contain an =, e.g. -d=true or --debug=true, and will be worked on in the future
        # NOTE: options do not include leading - or --
        raw_verbose_options = [opt.replace("--", "") for opt in userinput if opt.startswith("--") and opt.find("=") < 0]
        raw_short_options = [opt.replace("-", "") for opt in userinput if opt.startswith("-") and not opt.startswith("--") and opt.find("=") < 0]

        # Look for each option rather than at each thing supplied by the user
        # This may be undesirable; it ignores incorrect/invalid/unexpected input
        # Check any user-supplied verbose options
        for opsh in self.options:
            for rawverb in raw_verbose_options:
                if opsh.verbose == rawverb:
                    self.useroptions.add(opsh)
                    break
            if opsh.brief:
                for shortstack in raw_short_options:
                    for letter in shortstack:                   # Allows stacking short commands, e.g. -dz
                        if opsh.brief == letter:
                            self.useroptions.add(opsh)
                            break
        # Parse raw optargs, short and verbose (e.g. -d=true and --debug=true)
        raw_short_optargs = []
        raw_verbose_optargs = []
        for opt in userinput:
            if opt.find("=") > -1:
                if opt.startswith("-") and not opt.startswith("--"):
                    raw_short_optargs.append(opt.replace("-", "", 1))
                elif opt.startswith("--"):
                    raw_verbose_optargs.append(opt.replace("--", "", 1))
        
        # self.useroptargs is a dict; keys are option namedtuples (i.e. self.optargs); values are the args supplied by the user
        # e.g. -d=true is parsed to: {("debug", "enables debug output", "d"), "true"}
        for oparg in self.optionarguments:
            # Search user-provided verbose optargs
            for rawv in raw_verbose_optargs:
                # Split on =
                opt_and_arg = rawv.split("=", 1)        # No compound =; this puts validating arg values on implementer, which feels correct
                rawpt = opt_and_arg[0]
                rawrg = opt_and_arg[1]
                if oparg.verbose == rawpt:
                    self.useroptionarguments[oparg] = rawrg

            # Search user-provided short optargs
            for raws in raw_short_optargs:
                # Split on =
                opt_and_arg = raws.split("=", 1)        # No compound =; this puts validating arg values on implementer, which feels correct
                rawpt = opt_and_arg[0]
                rawrg = opt_and_arg[1]
                if oparg.brief and oparg.brief == rawpt:
                    self.useroptionarguments[oparg] = rawrg
    #----------------------------------------

    def context(self, callarg):
        """Establish context when run from a shell, such as app location and config."""
        self.workdir = os.path.normpath(os.getcwd())
        self.appdir = os.path.split(callarg)[0]
    #----------------------------------------

    def silence(self, quiet=True):
        """Toggle tryst.SILENT which determines whether `write_stdout` and `write_stderr` will be called."""
        self.SILENT = quiet
    #----------------------------------------

    def __load_config(self, configfile="config.json"):
        """Load config data.
        Currently loads JSON from config.json. Flexible."""
        configpath = os.path.join(self.appdir, configfile)
        self._config = JSONHelper.load(configpath)
    #----------------------------------------

    def get_config_value(self, configkey, default=None, configfile="config.json"):
        """Get a config value; default allows specification of a default value."""
        if not self._config:
            self.__load_config(configfile)

        return self._config.get(configkey, default)
    #----------------------------------------

    def get_config(self, configfile="config.json"):
        """Retrieve the entire config object, a python dict.
        Returns empty dict rather than None."""
        if not self._config:
            self.__load_config(configfile)
        return self._config
    #----------------------------------------

    def get_secret(self, key, default=None):
        filepath = os.path.join(self.appdir, "secrets.json")
        secrets = JSONHelper.load(filepath)
        return secrets.get(key, default)
    #----------------------------------------

    def debug(self, message):
        """Debug output. Not buffered for better diagnostics. \"printf debugging\"."""
        if self.DEBUG:
            print(str(message))
    #----------------------------------------

    def output(self, message):
        """Record the specified message object as output in `self.outputbuffer`."""
        self.outputbuffer.append(message)
    #----------------------------------------

    def error(self, message):
        """Record the specified message object as an error in `self.errorbuffer`."""
        self.errorbuffer.append(message)
    #----------------------------------------

    def write(self, buff, force=False, destination=sys.stdout):
        """Write a buffer (list) to destination (file).
        Optionally force, which will print even if this Tryst has been silenced."""
        if not self.SILENT or force:
            for obj in buff:
                # Treat any dictionary as JSON to standardize more complex output
                if isinstance(obj, dict) or isinstance(obj, list):
                    print(JSONHelper.tostring(obj), file=destination)
                else:
                    print(str(obj), file=destination)
    #----------------------------------------

    def write_stdout(self, force=False):
        """Write `tryst.outputbuffer` to std out."""
        self.write(self.outputbuffer, force)
    #----------------------------------------

    def write_stderr(self, force=False):
        """Write `tryst.errorbuffer` to std err."""
        self.write(self.errorbuffer, force, sys.stderr)
    #----------------------------------------

    def finish(self):
        """Finish the current tryst, write to stdout and stderr.
        Does not call sys.exit(). Intended for use with chaining."""
        self.write_stdout()
        self.write_stderr()
    #----------------------------------------

    def quit(self):
        """Quit the current tryst; write to stdout and stderr then call sys.exit().
        Ends the current session. Used chiefly by `show_usage()` and `show_version()`"""
        self.write_stdout()
        self.write_stderr()
        sys.exit()
    #----------------------------------------

    def __build_usage_token(self, opsh):
        """Build a usage token, e.g. [--debug] or [--help|-?]."""
        opshline = " [--" + opsh.verbose
        if opsh.brief:
            opshline += "|-" + opsh.brief
        opshline += "] "
        return opshline
    #----------------------------------------

    def __write_options(self, collection=[], skiplist=[]):
        """Write `collection` of options for usage instruction; skip objects in `skiplist`."""
        max_verbose_length = len(max([v.verbose for v in collection], key=len))
        for opsh in collection:
            if opsh in skiplist:
                continue
            message = ""
            if opsh.brief:
                message += str("-" + str(opsh.brief) + ",").ljust(5)
            else:
                message += " ".ljust(5)
            message += str("--" + opsh.verbose).ljust(max_verbose_length + 3)
            message += str(" | " + opsh.description)
            self.output(message)
    #----------------------------------------

    def show_usage(self):
        # Use the terse but expressive syntax of GNU/POSIX e.g.
        # app [options] [args] [etc.]
        self.output(self.appname + "; " + self.summary + "\n")
        default_options = [self.debug_option, self.help_option, self.version_option]

        usagetemplate = self.appname
        for opsh in self.options:
            if opsh.verbose in [v.verbose for v in default_options]:
                continue
            usagetemplate += self.__build_usage_token(opsh)
        for parg in self.optionarguments:
            usagetemplate += self.__build_usage_token(parg)
        usagetemplate += " [args]"

        self.output(usagetemplate)

        # Form: -x=, --xyz= | description, input instructions
        self.output("\noptions:")
        self.__write_options(self.options, default_options)

        if self.optionarguments:
            self.output("\noption-arguments:")
            self.__write_options(self.optionarguments)

        self.output("\ncommon options:")
        self.__write_options(default_options)
    #----------------------------------------

    def show_version(self):
        versionmessage = self.appname + " version " + self.version
        versionmessage += " by " + self.authors
        self.output(versionmessage)
    #----------------------------------------

    def add_default_options(self):
        """Add default options:
        --help | display usage instructions
        --version  | display version information
        --verbose  | provides additional output"""
        self.debug_option = Option("debug", "Displays additional output for diagnostics.")
        self.help_option = Option("help", "Displays usage instructions.")
        self.version_option = Option("version", "Displays version information.")

        self.add_option(self.debug_option)
        self.add_option(self.help_option)
        self.add_option(self.version_option)
    #----------------------------------------

    def handle_default_options(self):
        """Handle default options specified in tryst.add_default_options()."""
        if self.help_option in self.useroptions:
            self.show_usage()
            self.quit()
        if self.version_option in self.useroptions:
            self.show_version()
            self.quit()
        if self.debug_option in self.useroptions:
            self.DEBUG = True
    #----------------------------------------

    def consort(self, inputs=None):
        """Engage tryst. Add default options, interpret inputs, and establish context.
        0th argument should always be the name of the implementing module, e.g. 'tryst.py'."""
        if not inputs:
            inputs = list(sys.argv)
        self.add_default_options()
        self.interpret(inputs)
        self.context(inputs[0])

        # handle default arguments: help, debug, version
        self.handle_default_options()
    #----------------------------------------

    # TODO: mark deprecated
    def initialize(self, appname, authors, summary, version):
        """Initialize tryst with metadata; appname, authors, summary, version."""
        self.appname = appname
        self.authors = authors
        self.summary = summary
        self.version = version
    #----------------------------------------

    def __init__(self):
        """Lightweight construction sets meaningful defaults."""
        self.options = []
        self.optionarguments = []
        
        self.useroptions = set()            # duplicates are disregarded
        self.useroptionarguments = {}       # (option-class, user-input)
        self.userargs = []
        self.START_TIME = None              # TODO: change to TRYSTTIME or some such and actually initialize
        self.SILENT = False
        self.DEBUG = False
        self.appname = ""
        self.summary = ""
        self.authors = ""
        self.version = ""
        self.appdir = ""
        self.workdir = ""
        self._config = {}

        self.outputbuffer = []
        self.errorbuffer = []
    #----------------------------------------

    def main(self, inputs = None):
        self.appname = "tryst"
        self.authors = "wholesomenecromancer"
        self.summary = "Demonstrates basic usage of the tryst module."
        self.summary += "\ntryst performs trivial operations on string arguments."
        self.version = "0.0.2"

        # build options and optargs
        two_option = Option("two", "Print all args twice", "2")
        err_option = Option("error", "Intentionally write a line to stderr", "e")
        times_optarg = Option("times", "How many times to print all args", "t")

        # add options
        self.add_option(two_option)
        self.add_option(err_option)

        # add optargs
        self.add_option_argument(times_optarg)

        # consort
        self.consort(inputs)

        self.debug("Example debug statement.")

        # use the tryst to govern app behavior
        if len(self.userargs) < 1:
            self.debug("No args given.")
            self.show_usage()

        if err_option in self.useroptions:
            self.error("Example error statement.")

        times = int(self.useroptionarguments.get(times_optarg, 1))
        if two_option in self.useroptions:
            times *= 2

        for t in range(times):
            for arrg in self.userargs:
                self.output(arrg)

        self.write_stdout()
        self.write_stderr()
#================================================================================

if __name__ == "__main__":
    Tryst().main()
#------------------------------
