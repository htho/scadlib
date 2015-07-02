# Testing scadlib.py
In general scadlib.py has two modes. The `info` mode for extracting
information, and the `compile` mode to create a library file.

## Usage
    $ python scadlib.py -h
    usage: scadlib.py [-h] [-v] [-q] [-V] {info,compile} ...
    
    Helps to create and maintain fzz2scad libraries.
    
    positional arguments:
      {info,compile}
        info          Show information about the given file.
        compile       Create a library file for the given File.
    
    optional arguments:
      -h, --help      show this help message and exit
      -v, --verbose   -v -vv- -vvv increase output verbosity
      -q, --quiet     suppress any output except for final results.
      -V, --version   show program's version number and exit


## Information Extraction (`info` Mode)
There is always at least an input File. Which will be analyzed.

### Basic Input and Information Selection

Lets extract some information (which will fail):

    $ python scadlib.py info test/information-extraction-example.scad

uhh.. there is no output. That is because it was not specified what to output.

So we give the argument `--self` (or short `-s`) which shows
general information about the given file itself.

    $ python scadlib.py info test/information-extraction-example.scad --self

now we see a string representation of the input file.

In the same fashion we get information about all entities (modules,
variables and functions) and references (includes and uses) specified in
this file. 

    $ python scadlib.py info test/information-extraction-example.scad --self --modules --variables --functions --includes --uses

or short:

    $ python scadlib.py info test/information-extraction-example.scad -smvfiu

Now these are only information available in this file. But it might be much
more interesting to list all the entities available in the given file
and the files included and used.

#### Recursive Information Gathering
Now lets get some information from all the referenced files by using the
`--recursive` (or short `-r`) flag:

    $ python scadlib.py info test/information-extraction-example.scad --self --recursive

You may notice that there is no difference in the output except for
`Recursive: True`. That is all right. We will see later.

For `--modules` (`-m`) and the other entities (`-v -f -i -u`) there is
more to show.

    $ python scadlib.py info test/information-extraction-example.scad -r -m

#### Multiple Input Files
We are not limited to a single file to analyze. We can provide a list of
files and directories to analyze.

    $ python scadlib.py info test/information-extraction-example.scad lib/testlib/ -s

It is important that we don't use the -r flag here, as this would make
`lib/testlib/tools.scad` and `lib/testlib/planets.scad` appear twice.
Once as a reference from `test/information-extraction-example.scad` and
once without a reference.

By default, only the files in the given directory are analyzed, not the
files in sub directories below. To get this behavior, the `--traverse-dirs`
(short ´-t´) flag needs to be set.

### Output
The standard output shows a structured string representation of the data.
To get output that is usable in OpenSCAD or other Programs there are the
`--as-scad`, `--as-dump` and the `--as-json` flags.

#### `--as-scad` and `--as-dump`
Both flags make scadlib.py produce output that is usable in with OpenSCAD.
Both have *almost* the same effect:
The `--as-scad` flag makes scadlib.py *reproduce* the information stored
about a file or an entity. The content of modules, functions and variable
definitions is kept as it is. The origin of each entity is stated in
a comment in the produced code.

    $ python scadlib.py info test/information-extraction-example.scad -sr --as-scad

The `--as-dump` flag makes scadlib.py copy the relevant lines of code
from the input file to the output. Referenced files are copied/dumped into
the output.

    $ python scadlib.py info test/information-extraction-example.scad -sr --as-dump

The `--as-dump` flag is a nice method to get a portable version of a file
without any dependencies. It also may help debugging scad code. As the
line numbers are correct when OpenSCAD throws any errors. But you may also
use the compile mode.

#### `--as-json`
JSON output is not implemented yet, but maybe *you* are the one to implement it!

The idea is to produce json code that may be used in other tools to help
create big (online) libraries and/or sophisticated filtering systems.

#### The `--self` flag and info output.
Now you may understand why the `--self` flag always and only shows information about the given input files.

The first reason: With multiple input files which depend on each other, those representations would be shown multiple times.  
The second reason is that for other output formats, this would lead to the
production of multiple output files. One file for each referenced file,
which is definitely not what you want.  
Of course we could work around this, but the third reason is, that a
workaround would lead to inconsistent behavior. We might have reasonable
behavior for the first-time-user, which will be confusing in the long
run.

#### Specifying an `--output` (`-o`) file.
If you can't or don't want to use [pipes](http://en.wikipedia.org/wiki/Pipeline_%28Unix%29)
you may set and specify the `--output` (`-o`) flag. When set, but not
specified any further, a file named like the source file (or if multiple,
the first file) with an appropriate extension containing `.info.` will be produced.

Examples:

    $ python scadlib.py info test/information-extraction-example.scad -sr -o

will produce a file named `information-extraction-example.scad.info.txt`.

    $ python scadlib.py info test/information-extraction-example.scad -sr --as-dump -o

will produce a file named `information-extraction-example.scad.info.dump.scad`.

    $ python scadlib.py info test/information-extraction-example.scad -sr --as-scad -o

will produce a file named `information-extraction-example.scad.info.scad`.

    $ python scadlib.py info test/information-extraction-example.scad -sr --as-json -o

will produce a file named `information-extraction-example.scad.info.json`.

Anyway, you may give a filename after the `-o` flag so you get the name
that is best for you:

    $ python scadlib.py info test/information-extraction-example.scad -sr --as-dump -o myfancyfile.scad

You may set the `--override` or the `--dont-override` flag to specify
the behavior on existing output files. By default, you are asked
if you want to override an existing file.

### Filtering
Filtering is not implemented yet, but maybe *you* are the one to implement it!
Or this function will become redundant if there are any good tools based
on the `--as-json` output.


## Usage
    $ python scadlib.py info -h
    usage: scadlib.py info [-h] [-t] [-r] [-o [OUTPUT]]
                           [--override | --dont-override | --ask]
                           [--as-scad | --as-json | --as-dump] [-s] [-m] [-v] [-f]
                           [-i] [-u] [--with-meta WITH_META]
                           [--with-meta-key-value WITH_META_KEY_VALUE WITH_META_KEY_VALUE]
                           [--regex]
                           INPUT_FILE_OR_DIR [INPUT_FILE_OR_DIR ...]
    
    optional arguments:
      -h, --help            show this help message and exit
    
    input:
      How to handle the input files.
    
      INPUT_FILE_OR_DIR     The files/directories that should be searched.
      -t, --traverse-dirs   If a directory is given traverse through the sub
                            directories.
      -r, --recursive       look for information recursively (look in included and
                            used files).
    
    output:
      What should the output look line?
    
      -o [OUTPUT], --output [OUTPUT]
                            write output to an .scad File instead to console. (if
                            not defined further 'foo.scad' becomes
                            'foo.info.scad'.)
      --override            Override existing output files without asking.
      --dont-override       Do not override any existing output files - Print to
                            console instead.
      --ask                 Ask if an existing file should be overwritten.
                            (default)
      --as-scad             give output that can be used in .scad files.
      --as-json             give output that is json encoded. Useful for writing a
                            better filter engine. (NOT IMPLEMENTED YET).
      --as-dump             dump the relevant sections from the content. If
                            recursive, included or used sections will be copied.
    
    selection:
      Which information should be extracted?
    
      -s, --self            show information about the file itself.
      -m, --modules         list the modules in the given file.
      -v, --variables       list the variables in the given file.
      -f, --functions       list the functions in the given file.
      -i, --includes        list the files that are included in this file.
      -u, --uses            list the files that are used by this file.
    
    filter:
      Filter the entities. (NOT IMPLEMENTED YET!)
    
      --with-meta WITH_META
                            Only show results with the given metadata field. (NOT
                            IMPLEMENTED YET!)
      --with-meta-key-value WITH_META_KEY_VALUE WITH_META_KEY_VALUE
                            Only show results where the given metadata field has
                            the given value. (NOT IMPLEMENTED YET!)
      --regex               Use regular expressions to specify fields and values.
                            (NOT IMPLEMENTED YET!)
    
    
## Library Compilation

Compiling a library is the main reason to use scadlib. Note that all flags
that exist in the `info` mode and in the `compile` mode and that have the same name, have the same functionality. (The only exception is that
`--modules` (info) and `--mapping` (compile) have the same shortcut: `-m`)

Like in info mode, we need an input file. The difference is, that there
may only be one input file. As this is the file we want to compile a
library for.

    $ python scadlib.py compile test/compile-example.scad

Including the file generated here into test/compile-example.scad and
removing all other references, will result in a working copy that only
depends on the compiled library.

### Searching for resolutions
We may also remove all includes before compiling and let scadlib find
the needed files, by specifying the the path to the `--lib` (`-l`):

    $ python scadlib.py compile test/compile-example-no-references.scad -l lib/testlib/

Anyway in a large library we may want to look for files in all directories
and sub directories. So we specify the `--traverse` (`-t`) flag.

    $ python scadlib.py compile test/compile-example.scad -l lib/ -t

Note that unresolved dependencies will be pseudo-resolved with dummy
entities. You can change this behavior with the `--dont-create-dummies`
flag.

### Mapping/Aliasing

Sometimes we need to create a model without knowing the names of the modules
in the library we depend on.

fzz2scad is the best example here, as it heavily depends on unknown dependencies:
The module specifying a model of a PCB contains all the positions of all
the parts and specifies the dependencies. The names of the modules, generated
by fzz2scad are not the names of the modules in the libraries. A file that
defines the mapping between fzz2scad module names and library module names
is needed:

    $ python scadlib.py compile test/compile-mapping-example.scad -l lib/testlib/ -m test/compile-mapping-example.json

This will produce a library that resolves the dependencies by creating
wrapper entities.

The [json](http://en.wikipedia.org/wiki/JSON) syntax should be
self-explanatory (at least to people who know json):

```json
{
    "modules": {
        "bigPlanet" : { "name" : "sunPlanet", "arguments" : "" },
        "smallPlanet" : "secondPlanet"
    },
    "functions": {
        "rfunc" : { "name" : "r_from_dia", "arguments" : "dia" }
    }
}
```

It is a dictionary of dictionaries. On the top level, the recognized keys
are "module", "function" and "variable". On the second level there is
the name of the entity as key. The vaule may either be the name of the
resolving entity or a dictionary with the keys "name" and "arguments"
where the "name" is the name of the resolution and "arguments" the string that
will be put between the brackets.

### Output
In general output works like in the info mode. But of course there is only
.scad output. The extension of the automatically produced output file
is `.lib.scad`.

There are two flags that affect the content of the library:

`--all-in-one` (`-a`) will put all the entities together with the original.

If there is an entity that cant be resolved, a dummy entity will be created.
If you don't want these dummies to be created you can set the
`--dont-create-dummies` flag.

### Usage
    $ python scadlib.py compile -h
    usage: scadlib.py compile [-h] [-l LIB [LIB ...]] [-m MAPPING] [-t] [-r]
                              [-o [OUTPUT]] [--override | --dont-override | --ask]
                              [-a] [--dont-create-dummies]
                              INPUT_FILE
    
    Create a library file for the given File.
    
    optional arguments:
      -h, --help            show this help message and exit
    
    input:
      How to handle the input files.
    
      INPUT_FILE            The file to create the library for.
      -l LIB [LIB ...], --lib LIB [LIB ...]
                            The files/directories that should be searched for the
                            needed entities to create this library.
      -m MAPPING, --mapping MAPPING
                            A json file or a json string that specifies name
                            mappings for modules, variables and functions. Simple
                            Example:'{ "modules": { "moduleName" :
                            "implementingModuleName" } }' Example with arguments:
                            '{ "functions": { "functionName" : { "name" :
                            "implementingFunctionName", "arguments" :
                            "argumentString" } } }'
      -t, --traverse-dirs   If a directory is given traverse through the sub
                            directories to find .scad files.
      -r, --recursive       look for entities recursively (look in included and
                            used files).
    
    output:
      -o [OUTPUT], --output [OUTPUT]
                            write output to an .scad File instead to console. (if
                            not defined further 'foo.scad' becomes
                            'foo.lib.scad'.)
      --override            Override existing output files without asking.
      --dont-override       Do not override any existing output files - Print to
                            console instead.
      --ask                 Ask if an existing file should be overwritten.
                            (default)
      -a, --all-in-one      Copy the content of the input file, remove references
                            and copy the needed entites. The whole model in one
                            file, no dependencies.
      --dont-create-dummies
                            Don't create dummies for unresolved dependencies.
    

