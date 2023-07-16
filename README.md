
ElementSimulator 0.2.5
======================

[ElementSimulator](https://github.com/d-zo/ElementSimulator)
is a simple test program to simulate geotechnical laboratory tests (triaxial and oedometric compression)
as well as response envelopes and stress paths.
It was created at the Institute of Geotechnical Engineering
at the Hamburg University of Technology.


Installation
------------

ElementSimulator requires a Python 3.7+ environment and
the zipapp file can be run with Python.
A Fortran compiler is needed to compile the geotechnical laboratory tests
(GNU and Intel Fortran compilers were used).
If the commercial software [Abaqus](https://www.3ds.com/products-services/simulia/products/abaqus/)
is available and linked with a Fortran compiler,
it can be used for single element simulations as well.
ElementSimulator uses [matplotlib](https://matplotlib.org/) for plotting.


Running the program
-------------------

In Linux the following commands can be used in a shell
(the first command has to be adjusted to point to the right directory).

```
cd /path/to/ElementSimulator
python3 ElementSimulator.pyz
```

In Windows a batch file can be created to provide access to ElementSimulator.
Therefore, the path to the Python interpreter and the path to ElementSimulator have to be
defined in the following code.

```
@echo off
pushd C:\path\to\ElementSimulator
C:\path\to\Python\python.exe C:\path\to\ElementSimulator\ElementSimulator.pyz
pause
```

ElementSimulator can be run interactively if called without any options (as shown above)
or with all of the following options as a batch run:

```
python3 ElementSimulator.pyz -test=[arg] -prog=[arg] -zusatz=[arg]
```

The arguments and their options are

 - `test` to choose the geotechnical test to perform.
    - `oedo`: Oedometeric test.
    - `triax`: Triaxial test.
    - `scher`: Simple shear test (only with Abaqus).
    - `impuls`: Single response (only with Fortran).
    - `pfade`: Stress paths starting from a single stress state (only with Fortran).
    - `ellipsen`: Response envelopes around given stress states (only with Fortran).

 - `prog` which program to use for conducting the element tests.
    - `fortran`: Use the given Fortran compiler to compile provided test programs with user routines.
                 Expected user routine interface is UMAT, VUMAT, or XMAT.
                 `test=scher` is currently not suported as direct Fortran program.
    - `abaqus`: Use Abaqus/Standard or Abaqus/Explicit and the provided Python scripts
                to create, run, and postprocess the supported tests.
                Only `oedo`, `triax`, and `scher` are currently supported.
                Does select an explicit analysis with Abaqus/Explicit for given VUMAT routines
                and implicit analysis with Abaqus/Standard for UMAT routines.

 - `zusatz` to select how to handle the created files.
    - `normal`: Create the work directory, run the tests there, create plots, copy the results in `output/` directory
                and remove work directory if everything was successfull. This can be considered the default way.
    - `keinplot`: Same as `normal`, but don't create any plots. This is mainly for compatibility if `matplotlib`
                  is not available for plotting or another workflow for creating plots is used.
    - `ordnerbehalten`: Same as `normal` but does not delete the working directory if everything was successfull.
    - `nurvorbereiten`: Only prepares everything in the working directory but stops before actually running the experiments.

As hinted, ElementSimulator does not support all possible combinations of arguments.
More precisely following combinations will not work:

 - Abaqus simulations with impulse test (`-prog=abaqus -test=impuls`)
 - Abaqus simulations with stress paths (`-prog=abaqus -test=pfade`)
 - Abaquss simulations with response envelopes (`-prog=abaqus -test=ellipsen`)
 - Fortran simulations with simple shear test (`-prog=fortran -test=scher`)

If an invalid combination is chosen,
ElementSimulator will exit with a corresponding note after reading the options.
Since it was created alongside the xMat user routine (see <https://github.com/d-zo/xMat>),
this user routine can also be used to test ElementSimulator.

A simple function documentation (in german) created with pydoc can be found
[here](https://d-zo.github.io/ElementSimulator/ElementSimulator.html "ElementSimulator documentation").


Structure
---------

Using ElementSimulator requires certain files and folders.
Typically the zipapp `ElementSimulator.pyz` is used inside a prepared directory with the following structure

 - `UMAT/`: Directory for UMAT user routines
 - `VUMAT/`: Directory for UMAT user routines
 - `XMAT/`: Directory for XMAT user routines
 - `output/`: Final results and plots are copied into this folder
 - `utilities/`: Contains Python scripts, Fortran sources, and some auxiliary files
                 to create, run and postprocess the tests (see below)
 - `einstellungen.json`: JSON-file with all directly configurable settings for the tests
 - `ElementSimulator.pyz`: Main program as zipapp
 - `ElementSimulator.bat`: Batch-file to run ElementSimulator.pyz in Windows (paths inside need to be adjusted)
 - `systembefehle.json`: JSON-file to configure paths and programs to use (paths inside need to be adjusted)

That means, ElementSimulator requires the presence of the potentially empty folders `UMAT`, `VUMAT`, and `XMAT`.
Each user routine to be used should be in the directory of the respective interface (files in subfolders are ignored)

In `utilities/` the following files are provided:

 - `*mat_*.f`: Fortran templates for different element tests and different interfaces
 - `fort/`: Directory for auxiliary files for user routines during Fortran calls.
            Especially `preparation.f` can be important to adjust for different user routines and constitutive models.
            Files in this directory will be available for all routines and tests.
            Routines depending on certain files like `aba_param.inc` or `vaba_param.inc` (which are provided by Abaqus)
            need those files being copied into this directory from the installation directory.
            This folder can also be used for optional files like `matplotlibrc`.

 - `*plicit_*.py`: Python templates for creating element tests in Abaqus
 - `Auswertung_*.py`, `auswertungshilfe.py`: Python scripts to plot the results of Abaqus simulations
 - `abq*_*/` (optional, not provided): Directories for additional files running Abaqus simulations.
   The naming scheme consists of `abq`, the version number and a operating system prefix.
   Examples are `abq2018_lnx` for Abaqus 2018 for Linux and `abq6.14-2_win` for Abaqus 6.14-2 for Windows.
   If a specific Abaqus version should use a specific set of files, they can be provided here.
   Typically up to three files are used: `aba_param.inc` and `vaba_param.inc` from your Abaqus installation
   und an environment file called `abaqus_v6.env`
   Although the first two are interchangable between versions
   (except for Abaqus 2019 which uses fixed format comments with `c`.),
   the environment file `abaqus_v6.env` is different from installation to installation.
   It depends on the actual version of Abaqus as well as the linked compiler and its options.
   It is mainly used to add the `free` flag to the compilation command for `free` format routines.

Additionally the provided configuration files `einstellungen.json` and `systembefehle.json` are required to
control ElementSimulator.


**Structure of `systembefehle.json`**

Commands and paths to the Python, the Fortran compiler, and Abaqus (if available) are set in `systembefehle.json`.
It should look like the following:

```
{
   "Linux": {
      "Abaqus": "abaqus",
      "Python": "python",
      "Intel Fortran": "ifort",
      "GNU Fortran": "gfortran"
   },
   "Windows": {
      "Abaqus": "C:\path\to\Abaqus\abq2020.bat",
      "Python": "C:\path\to\python\python.exe",
      "Intel Fortran": "C:\path\to\ifort\ifort.exe",
      "GNU Fortran": "C:\path\to\gfortran\gfortran.exe"
   }
}
```


**Structure of `einstellungen.json`**

All simulation settings and testparameters are saved in `einstellungen.json`.
It has the following sections:

 - `Global`: General settings related to time increments and durations are saved here.
   Three entries are specific to Abaqus runs: `Abaqus Simulationsdauer [s]`,
   `Anzahl Ausgaben Abaqus` and `max. Laufzeit Abaqus [s]`.
   The first of these defines the duration Abaqus should simulate.
   `Anzahl Ausgaben Abaqus` defines the amount of outputs Abaqus writes and the last one
   defines the maximum amount of time an Abaqus simulation is allowd to take before it is cancelled.
 - `Fortran`: Options related to user routines and their compilation flags.
   The structure of `Compiler Argumente` expects an entry for each user routine(s) to be used.
   The key is the name of the user routine and value is a list with arguments passed to the compiler
   and a list with additional Fortran files used during compilation.
 - `Ausgabe`: Output related options.
 - `Material`: Basic information about the material parameters. These informations are processed
   and used in another Fortran source file located at `utilities/fort/preparation.f`.
   The currently supported constitutive models and user routines can be seen in `preparation.f` and
   extended as needed.
 - One section for each of the tests: `Oedometerversuch`, `Triaxialversuch`, `Einfachscherversuch`,
   `Impulsantwort`, `Spannungspfade`, and `Antwortellipsen`.
   In each section all required and some optional variables are defined and can be adjusted.


Please note that working with both configuration files requires a valid JSON structure.
It might be necessary to escape character sequences like spaces in paths.
If there is an issue reading the configuration files,
ElementSimulator should point you to it.


Requirements on user routines
-----------------------------

ElementSimulator allows to investigate the behaviour of different constitutive models in Fortran user routines.
Each user routine is assumed to have the following properties

 - The user routines need to have a `UMAT` or `VUMAT` interface (custom `XMAT` interface is also supported)
   and have to be moved or copied into the respective directory.
 - The test programs pass `double precision` values to the user routines and expect them to handle it correctly.
   Also for Abaqus simulations the auxiliary files `aba_param.inc` and `vaba_param.inc` are needed to
   provide their definitions in `double precision`.
 - User routines need to have a file name ending with `.f`.
   When using Abaqus from Windows, the suffix `.for` was expected for older versions of Abaqus.
   ElementSimulator takes care of this automatically.
 - Each user routine should be listed with optional compiler arguments in _Fortran -> Compiler Argumente_ in `einstellungen.json`.
   Since many user routines are provided in `fixed` format, this is supported by default.
   Compilation flags for user routines in `free` format (or with other requirements from the compiler)
   can be specified here.
   For Abaqus simulations this has also be defined in an environment file.
   It is recommended to use a local `abaqus_v6.env` file and add the respective compiler argument
   for `free` format routines in the `compile_fortran` command.
   (This file will only be used/copied in the working directory if it is defined as `free` format
   routine in `einstellungen.json` of ElementSimulator).
 - Currently, only one constitutive model identifier is used for all user routines.
   But it is possible to support different kind of identifiers and parameters for each user routine.
   This involves two steps:
    - First adjust _Fortran -> Compiler Argumente_ in `einstellungen.json` and add the name
      of all user routines to be used. Regardless of the amount of other arguments required,
      make sure to add different preprocessor macros (`D_...`) to the each compiler argument.
    - Edit the provided Fortran file `utilities/fort/preparation.f` based on the default
      identifier given in _Material -> Name_ of `einstellungen.json` and the preprocessor macros.
      Those are used to distinguish between different user routines:
        - Add common material parameters in subroutine `Get_Material()` and do the actual assignment
          in subroutine `Adjust_Default_Materialparameters()`.
        - Adjust the initial state variables passed into the user routines in subroutine `Prepare_State()` and
          the returned state variables in subroutine `Postprocess_State()`


Troubleshooting
---------------

If an error occured or something happened which is not supposed to happen,
ElementSimulator should give a hint about the origin of the issue in the terminal output.
Issues with user routines are usually more verbose when calling them directly from Fortran
instead of Abaqus. But if the error is only occuring when using Abaqus,
it should be checked first that a user routines runs fine with Abaqus outside of ElementSimulator
(see also [About user routines]).

 - During startup some binary can not be found or some path does not exist.
    - Check paths in `systembefehle.json` and make sure they point to the right files.
      When running from Windows also check `bat` file.

 - When running `__main__` can not be found and a module error is thrown.
    - ElementSimulator needs a working Python3 environment (tested with Python 3.7+).
      Earlier versions are not supported.

 - Required files can not be found.
    - All required files are provided and should be there by default.
      If a file is missing or not parsable, the error message should tell you which one.
      
 - JSON configuration files can not be parsed.
    - After modifying the files they have to adhere to the JSON standard or an error is thrown.
      The error message should point to the line in which parsing failed.

 - During run something is off or the results are not as expected.
    - Check that the values in the `einstellungen.json` configuration file have meaningful values.
      There are no value checks, so you have to make sure the order, sign and actual values are correct
      (and for arrays the right amount of values in the right order given).


Note on using Abaqus
--------------------

During developement, Abaqus/Standard simulations on the test systems occasionally did not exit at the end
although they were successfull runs.
To be able to have multiple runs without worrying about that issue,
ElementSimulator defines a maximum runtime for Abaqus simulations in `einstellungen.json`.
If the time is up, the simulations are terminated automatically.
Since the time limit depends on the given system and simulation parameters
it should be set accordingly.
Otherwise simulations might be terminated prematurely or the wait time for finished simulations is overly long.

It is worth noting that terminating the simulations might end up leaving some unconnected processes back in the system.
Therefore if simulations did not exit properly, check if all spawned Abaqus components (like `abaqus`, `ABQcaeK`, `standard`, ...)
and the additional `python` process which was started by `subprocess` are terminated.
Usually having an eye on the running processes (Windows: Task-Manager, Linux: `ps -e`)
should help to locate still running processes.


Contributing
------------

**Bug reports**

If you found a bug, make sure you can reproduce it with the latest version of ElementSimulator.
Please check that the expected results can actually be achieved by other means
and are not considered invalid operations due to problematic template files.
Please give detailed and reproducible instructions in your report including

 - the ElementSimulator version
 - the expected result
 - the result you received
 - the command(s) used as a _minimal working example_

Note: The bug should ideally be reproducible by the _minimal working example_ alone.
Please keep the example code as short as possible (minimal).


**Feature requests**

If you have an idea for a new feature, consider searching the
[open issues](https://github.com/d-zo/ElementSimulator/issues) and
[closed issues](https://github.com/d-zo/ElementSimulator/issues?q=is%3Aissue+is%3Aclosed) first.
Afterwards, please submit a report in the
[Issue tracker](https://github.com/d-zo/ElementSimulator/issues) explaining the feature and especially

 - why this feature would be useful (use cases)
 - what could possible drawbacks be (e.g. compatibility, dependencies, ...)



License
-------

ElementSimulator is released under the
[GPL](https://www.gnu.org/licenses/gpl-3.0.html "GNU General Public License"),
version 3 or greater (see als [LICENSE](https://github.com/d-zo/ElementSimulator/blob/master/LICENSE) file).
It is provided without any warranty.

