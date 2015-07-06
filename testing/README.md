# Testing scadtool.py
This document explains the different functions of `scadtool.py`

In general scadtool.py has four modes. The `info` mode for extracting
information about files or sets of files, the `map` mode to create a mapping file, the `compile`
mode to compile all references of a file into a single file and the `build`
mode to create a library file that resolves the dependencies of a given file.

## General Usage
    $ python scadtool.py -h


## Information Extraction Mode (`info`)
There is always at least an input file which will be analyzed.

### Basic Input and Information Selection

Lets extract some information (which will fail):

    $ python scadtool.py info testing/information-extraction-example.scad

uhh.. there is no output. That is because it was not specified what to output.

So we give the argument `--self` (or short `-s`) which shows
general information about the given file itself.

    $ python scadtool.py info testing/information-extraction-example.scad --self

now we see a string representation of the input file.

In the same fashion we get information about all entities (modules,
variables and functions) and references (includes and uses) specified in
this file. 

    $ python scadtool.py info testing/information-extraction-example.scad --self --modules --variables --functions --includes --uses

or short:

    $ python scadtool.py info testing/information-extraction-example.scad -smvfiu

Now these are only information available in this file. But it might be much
more interesting to list all the entities available in the given file
and the files included and used.

#### Recursive Information Gathering
Now lets get some information from all the referenced files by using the
`--recursive` (or short `-r`) flag:

    $ python scadtool.py info testing/information-extraction-example.scad --self --recursive

For `--modules` (`-m`) and the other entities (`-v -f -i -u`) there is
more to show.

    $ python scadtool.py info testing/information-extraction-example.scad -r -m

#### Multiple Input Files
We are not limited to a single file to analyze. We can provide a list of
files and directories to analyze.

    $ python scadtool.py info testing/information-extraction-example.scad lib/testlib/ -s

It is important that we don't use the -r flag here, as this would make
`lib/testlib/tools.scad` and `lib/testlib/planets.scad` appear twice.
Once as a reference from `testing/information-extraction-example.scad` and
once without a reference.

By default, only the files in the given directory are analyzed, not the
files in sub directories below. To get this behavior, the `--traverse-dirs`
(short `-t`) flag needs to be set.

You probably don't want to set the `-t` and the `-r` flag at the same time
as this might lead to problems if a file is referenced in a source file
and found by traversing.

### Output
The standard output shows a structured string representation of the data.
To get output that is usable in OpenSCAD or other Programs there are the
`--as-scad`, `--as-dump` and the `--as-json` flags.

#### `--as-scad` and `--as-dump`
Both flags make scadtool.py produce output that is usable with OpenSCAD.
Both have *almost* the same effect:
The `--as-scad` flag makes scadtool.py *reproduce* the information stored
about a file or an entity. The content of modules, functions and variable
definitions is kept as it is. The origin of each entity is stated in
a comment in the produced code.

    $ python scadtool.py info testing/information-extraction-example.scad -mr --as-scad

The `--as-dump` flag makes scadtool.py copy the relevant lines of code
from the input file to the output. Referenced files are copied/dumped into
the output.

    $ python scadtool.py info testing/information-extraction-example.scad -mr --as-dump

Notice that `--as-scad` and `--as-dump` do not produce useful output
for the `--self` flag in combination with the`--recursive` flag.
That is because they will output *all* the files that are referenced in
a single file. Some entities will be in the output multiple times.

If you want to copy all the entities into a single file, see the [`compile` mode](#mapping-mode-map)

#### `--as-json`
JSON output is not implemented yet, but maybe *you* are the one to implement it!

The idea is to produce json code that may be used in other tools to help
create big (online) libraries and/or sophisticated filtering systems.
You know: A website were you can select the modules you need for your model.

#### Specifying an `--output` (`-o`) file.
If you can't or don't want to use [pipes](http://en.wikipedia.org/wiki/Pipeline_%28Unix%29)
you may set and specify the `--output` (`-o`) flag. When set, but not
specified any further, a file named like the source file (or if multiple,
the first file) with an appropriate extension containing `.info.` will be produced.

Examples:

    $ python scadtool.py info testing/information-extraction-example.scad -mr -o

will produce a file named `information-extraction-example.scad.info.txt`.

    $ python scadtool.py info testing/information-extraction-example.scad -mr --as-dump -o

will produce a file named `information-extraction-example.scad.info.dump.scad`.

    $ python scadtool.py info testing/information-extraction-example.scad -mr --as-scad -o

will produce a file named `information-extraction-example.scad.info.scad`.

    $ python scadtool.py info testing/information-extraction-example.scad -mr --as-json -o

will produce a file named `information-extraction-example.scad.info.json`.

Anyway, you may give a filename after the `-o` flag so you get the name
that is best for you:

    $ python scadtool.py info testing/information-extraction-example.scad -mr --as-dump -o myfancyfile.scad

You may set the `--override` or the `--dont-override` flag to specify
the behavior on existing output files. By default, you are asked (`--ask`)
if you want to override an existing file.

### Filtering
Filtering is not implemented yet, but maybe *you* are the one to implement it!
Or this function will become redundant if there are any good tools based
on the `--as-json` output.


### General Usage
    $ python scadtool.py info -h

## Compilation Mode (`compile`)
This mode produces a one-file copy of the given file.
It compiles the referenced files to a single file.
Which is useful for debugging, when
OpenSCAD complains on line numbers you can't know.

    $ python scadtool.py compile testing/information-extraction-example.scad

### General Usage
    $ python scadtool.py compile -h

## Mapping Mode (`map`)
Sometimes we need to create a model without knowing the names of the entities
in the library we depend on, or the entities should be interchangeable.

fzz2scad is the best example here, as it heavily depends on unknown dependencies:
The module specifying a model of a PCB contains all the positions of all
the parts and specifies the dependencies. The names of the modules, generated
by fzz2scad are not the names of the modules in the libraries. A file that
defines the mapping between fzz2scad module names and library module names
is needed.

The simplest usage is to take a json-mapping and to generate OpenSCAD
code for all the mappings in the given json-mapping. 

    $ python scadtool.py map testing/mapping-example.json


As the mapping file might become quite large and not all mappings are
needed for eacht model, a (set of) .scad file(s) can be supplied. Only the
mappings are produced that actually are needed in the given file(s).

    $ python scadtool.py map testing/mapping-example.json -i testing/mapping-example.scad

If you compare the output of both commants you notice that the mapping
from `unused` to `useless` is missing, as it is not needed in
`testing/mapping-example.scad`.

### The json-mapping syntax

Mappings are described in [json](http://en.wikipedia.org/wiki/JSON)-Syntax.
The structure should be easy to understand. But it has some twists to
allow different levels of details:

```json
{
    "modules": {
        "smallPlanet" : "secondPlanet",
        "bigPlanet" : { "name" : "sunPlanet" },
        "alienPlanet" : { "name" : "genericScaledPlanet", "arguments" : {"dist" : "distance", "dia" : "diameter"} },
        "unused" : "useless"
    },
    "functions": {
        "rfunc" : { "name" : "r_from_dia", "arguments" : ["dia"] }
    },
    "variables" : {}
}
}
```

The recognized keys on the top level are `module`, `function` and `variables`.

On the next level there always is a mapping between the name of the entity
in use ("model-entity") on the left-hand side, and the properties of the
entity in the library ("library-entity") on the right-hand side.

The simplest mapping is from name to name: `"smallPlanet" : "secondPlanet"`

The name of the model-entity always is a string. 
The library-entity can either be a string or an object (dict in python).
If it is a string, it is the name. 
Objects must have the attribute `name`. `arguments` is an optional
attribute which can either be an object or an array (list in python).

If `arguments` is an array, the items are the names of the arguments of the mapping
entity. 
For example `{ "modules" : { "x" : { "name" : "y", "arguments" : ["A", "B", "C"] } } }`
creates an entity like this: `module x(A, B, C){y(A, B, C);}`.
The library-entity must have the same signature as the model-entity.

If `arguments` is an object it is possible to rename the arguments.
the attribute (left-hand side) is the name of an argument of the
model-entity, the value (right-hand side) is the name of an argument of
the library-entity. 
For example: `{ "modules" : { "x" : { "name" : "y", "arguments" : {"A":"H", "B":"I", "C":"J"} } } }`
becomes: `module x(A, B, C){y(H=A, I=B, J=C);}`


### General Usage
    $ python scadtool.py map -h


## Library Building (`build`)

Building a library is the main reason to use scadtool.
Basically the dependencies for the input file are calculated. Then the
resolutions for these dependencies are collected from the library and
written into a new file, which can be included into the original file.

Like in info mode, we need an input file. The difference is, that there
may only be one input file. As this is the file we want to compile a
library for.

    $ python scadtool.py build testing/build-example.scad lib/ --traverse-dirs

Including the file generated here into test/compile-example.scad, will
result in a working copy that only depends on the compiled library.

Note that still unresolved dependencies will be pseudo-resolved with dummy
entities. You can change this behavior with the `--dont-create-dummies`
flag.

### Output
In general output works like in the info mode. But of course there is only
.scad output. The extension of the automatically produced output file
is `.lib.scad`.

### General Usage
    $ python scadtool.py build -h

