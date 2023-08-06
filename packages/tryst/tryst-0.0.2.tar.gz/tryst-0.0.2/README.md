# Tryst
CLI support package.

[tryst on Github](https://github.com/WholesomeNecromancer/tryst)

[GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0-standalone.html)

>One's body is inviolable, subject to one's own will alone.

# What Tryst is:
A lightweight interface and context package for basic cli features intended for rapid atomic problem-solving. Built to support code-time chaining between apps for efficient code-reuse and 'build-outward' problem-solving methodologies.

Tryst is lightweight but means to compy with SOLID design principles and is a learning experience in action to build a better understanding of Python, CLI development, unit testing, deployment, support, and more.

# What Tryst is not:
Tryst is not fancy or comprehensive. It is not intended to be flawless, nor to replace more fully-functional and well-established CLI support packages such as [argparse](https://docs.python.org/3/library/argparse.html) or [getopt](https://docs.python.org/3/library/getopt.html). It is a project for learning and for rapid development of personal workflow enhancements and automation.

This is evidenced by very little validation; the burden of understanding is left to the implementing developer. For example, options and option-arguments are not duplicate-checked; undefined behavior will occur if you define more than one option object with the same brief or verbose tokens. Additionally, most of Tryst's methods are public rather than private; this is by design, to provide maximum flexibility to the implementer.

# Features
- Options and Option-Arguments specifiable via verbose (e.g. `--debug`) and brief (e.g. `-d`) tokens
    - Brief tokens for options can be stacked e.g. `-abc`
- Configuration via `config.json` file and `get_config*` API
- Decoupled output; easily avoid unnecessary spew to `stdout` or `stderr`
    - `write*` api allows easy *to-file* functionality
- Procedural usage instructions
- Secrets (e.g. credentials) Support via `get_secret` API
    - Future development may include credential encryption or similar security features

# Usage
Tryst has recently been upgraded. To implement your own Tryst-based app, inherit Tryst and implement `main()`. Note the `inputs` argument which allows you or another developer to call your Tryst's `main` method with specifiable arguments at code-time, greatly expediting code reuse.

``` python
from tryst import Tryst     # Tryst class defines your app and its main
from tryst import Option    # Option defines options and option-arguments e.g. --debug

class MyTrystApp(Tryst):
    def main(self, inputs = None):
        self.appname = "my-tryst-app"

        # ...1. define and add your options and option-arguments here

        self.consort(inputs)

        # ...2. implement your app's behavior here based on self.userargs, self.useroptions, and self.useroptionarguments

        self.finish()   # Wrap-up and output
```

## Additional Implementation Details

Options, or switches, allow users to toggle functionality in your app. Option-Arguments allow for value-based user-input.

1. Define and add your `options` and `optionarguments`, establishing the rules of engagement for your tryst:
``` python
# Option("verbose-token", "description", "optional-brief-token")

# This option can be used with --my-option or -m
self.myoption = Option("my-option", "switches behavior in my app", "m")

# Add the option to your Tryst
self.add_option(self.myoption)

# This option-argument can be used with --my-option-argument="some value" or -a="some value"
self.myoptionargument = Option("my-option-argument", "lets a user specify a value for my app", "a")

# Add the option-argument to your tryst
self.add_option_argument(self.myoptionargument)
```

2. Govern your app behavior based on the arguments, options, and option-arguments the user specified:
``` python
if self.myoption in self.useroptions:
    # Act on --my-option

myoptargval = self.useroptionarguments.get(self.myoptionargument)
if myoptargval:
    # Act on --my-option-argument="some value"
```

### Provide Usage Instructions to Users
`mytryst.show_usage()`
>Note: this may be appropriate in your app due to various criteria, such as if the user specified no arguments, or no options; because every app is different, the burden of making the call to provide this usage is on the developer. The `show_usage()` method creates procedural instructions based on your Tryst's specified `options` and `optionarguments`.

### Decouple & Buffer Your Output
Use `self.output(message)` for result output and `self.error(message)` for error output.
>If you are working to diagnose your app while developing, use `self.debug(message)` to only display output when `--debug` is specified or `self.DEBUG` is set to `True`.

>*Keep in mind that `self.output` and `self.error` buffer output to `self.outputbuffer` and `self.errorbuffer` respectively, which are written/flushed via `self.write_stdout()` and `self.write_stderr()`.*

### Write Your Output
To write output and errors to stdout and stderr respectively and simply, call `self.finish()`.

This indicates that your Tryst has concluded and its outputs are ready.

>`finish()` does not call `sys.exit()`, while `quit()` does. `sys.exit()` interferes with app chaining because it ends the current python session completely. To build your app to be easily callable from another and to support app chaining, use `self.finish()` or call the appropriate write methods manually:

``` python
self.write_stdout()
self.write_stderr()
```

Tryst uses `JSONHelper` internally to cleanly format Python `dict` or `list` objects that may be in your Tryst's `outputbuffer` when writing. Expect dictionary and list objects you've passed to `self.output` to be written in an alphabetically sorted, readable, 4-space indented multiline string.

# CLI Conventions
- short options can be stacked
    - e.g. `tryst -e2` is equivalent to `tryst -e -2` and `tryst --error --two` respectively
- option-arguments only allow `=`, not spaces; complex values should be quoted at the shell
    - e.g. `--debug=true`, not `--debug true`
    - e.g. `--name="Wholesome Necromancer"`, not `--name=Wholesome Necromancer`
- order of options, option-arguments, and arguments does not matter in usage
    - e.g. `tryst.py --debug -e2 arg1`, `tryst.py -2e arg1 --debug`, and `tryst.py -e arg1 -2 --debug` are equivalent

# Best Practices
- Get configuration data *after* `consort()` is called to ensure the correct configuration file and path are loaded.

# Examples
Trivial example of app chaining:

``` python
#! trystchild.py

from tryst import Tryst
from tryst import Option

class TrystCapitalize(Tryst):
    def main(self, inputs = None):
        # self.DEBUG = True
        self.appname = "tryst-capitalize"
        self.authors = "wholesomenecromancer"
        self.summary = "Progeny of Tryst. Capitalizes strings."
        self.version = "0.x.y"

        self.consort(inputs)

        for argg in self.userargs:
            self.output(argg.upper())
        self.finish()
#================================================================================

class TrystChild(Tryst):
    def main(self, inputs = None):
        # self.DEBUG = True
        self.appname = "trystchild"
        self.authors = "wholesomenecromancer"
        self.summary = "Descends from Tryst. Echoes strings."
        self.version = "0.0.12a"

        # Options
        self.capitalize_option = Option("capitalize-inputs", "Capitalizes arguments before echoing using tryst-chaining.", "C")
        self.add_option(self.capitalize_option)

        # consort
        self.consort(inputs)

        self.debug("Example debug statement.")

        # use the tryst to govern app behavior
        if len(self.userargs) < 1:
            self.debug("No args given.")
            self.show_usage()
            self.quit()
        
        # Capitalize by using TrystCapitalize
        if self.capitalize_option in self.useroptions:
            captryst = TrystCapitalize()                                    # Construct
            captryst.silence()                                              # Silence console output
            captryst.main(self.userargs)                                    # Pass the user's arguments 
            if captryst.outputbuffer:                                       # Get TrystCapitalize's output directly
                self.userargs = captryst.outputbuffer                       # Replace our userargs before outputting

        for arrg in self.userargs:
            self.output(arrg)
        self.finish()
#================================================================================

#----------------------------------------
if __name__ == "__main__":
    TrystChild().main()
#----------------------------------------

```

# Tests
Tests can be run from `src/tryst/` via `python -m unittest`.

# Documentation
Documentation is intended for use with `pdoc`:

`pdoc tryst.py`
`pdoc -o <destdir> tryst.py`

# Support
Tryst intends to be platform-agnostic but has only been tested in Windows 10 environments with PowerShell 5.x and WSL 2.0's Ubuntu 20.x bash.
