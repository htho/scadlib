# scaddoc

A specification proposal for a style to document scad (OpenSCAD) files.

scaddoc is inspired by javadoc. Where applicable the [rules for documenting
Java code](http://www.oracle.com/technetwork/java/javase/documentation/index-137868.html)
should applied to scad code.

### Goals and Not (yet) Goals
The primary goal of scaddoc is to specify a human producible and machine
readable documentation style that allows *indexing* and *finding* as well
as *resolving* dependencies for modules, functions and variables in
OpenSCAD-Libraries.

Right now it is not a goal to create beautiful HTML-Documentation or even
to be doxygen compatible.

Anyway, using Markdown in the comments is encouraged. It allows a human
and machine readable markup/down, which might be interesting for future
use or tools that might build upon scaddoc/scadlib.

### Near Future
In the future there might be a web tool that allows searching
a large database of scad files. The comments will then be used to describe
the modules.

## scaddoc Style
scaddoc is inspired by javadoc. Where applicable the [rules for documenting
Java code](http://www.oracle.com/technetwork/java/javase/documentation/index-137868.html)
should applied to scad code.

### Tags (eg. `@param`, `@author`)

An author may define any tag for any entity (Except for the filename
tag, which should only appear once per file).
Tags may be defined multiple times. Tags that end with `-list` are expected
to be comma separated lists of values.

#### Standard Tags
Standard Tags like `@author` are used to store simple Information.
These tags may be defined multiple times. Information will be retreived
as a whole.

#### `-list` Tags
Tags that end with `-list` are used to specify an actual *list* of values.

#### `-dict` Tags
Tags that end with `-dict` are used to specify a dictionary of key-value
pairs. The key is the first word after the tag. The value starts after a
whitespace after the key.

All the `-dependency` and `param` tags implicitly are dictionaries.

### Specific Tags
The following Tags have a specific meaning:

#### All entities

`@description TEXT`
:    A description of what this entity does.
     This does not need to be defined explicitly. The Text before the
     first block tag is the content of this tag.

`@uri TEXT`
:    A source, where to find the module and its original context.

`@tag-list TEXT[, TEXT, ...]`
:    A comma separated list of tags, describing this entity. (for searching)

`@category-list TEXT[, TEXT, ...]`
:    A comma separated list of categories, this entity belongs to. Maybe
     there will be an official category list in the future?

`@author TEXT`
:    The author of this entity.

`@version TEXT`
:    The version of this entity.

`@note TEXT`
:    Anything special the author wants the user to know.

`@see TEXT`
:    A cross reference to another entity.

`@license-short TEXT`
:    The name of the license. Eg. GPLv3 or CC-BY-NA 4.0

`@license TEXT`
:    If necessary, the "boilerplate" of a license.

`@license-link TEXT`
:    A link to the full license text or the (official) website.

#### Files
`@filename TEXT`
:    Mandatory for files. Only a comment that contains this tag,
     followed by the name of the current file will be connected to this
     file.

`@variable-dependency NAME [DESCRIPTION]`
:    Name and meaning of a variable that is needed to show the model
     defined in this file.

`@module-dependency NAME [DESCRIPTION]`
:    Name and meaning of a module that is needed to show the model
     defined in this file.

`@function-dependency NAME [DESCRIPTION]`
:    Name and meaning of a function that is needed to show the model
     defined in this file.

##### Notice
A file only has these dependencies if these entities are needed on a file
level. If the entities are needed in a module defined in this file,
the module has this dependency, not the file.

There is no file-dependency tag. File dependencies are extracted from
include and use statements.

#### Modules
`@param NAME [DESCRIPTION]`
:    Name and meaning of this parameter.

`@variable-dependency NAME [DESCRIPTION]`
:    Name and meaning of a (global) variable that is needed to produce the
     model defined in this module (eg. the scale).

`@module-dependency NAME [DESCRIPTION]`
:    Name and meaning of a module that is needed to produce the model
     defined in this module.

`@function-dependency NAME [DESCRIPTION]`
:    Name and meaning of a function that is needed to produce the model
     defined in this module.


#### Functions
`@param NAME [DESCRIPTION]`
:    Name and meaning of this parameter.

`@return TEXT`
:    The meaning of the value returned by this function.

`@variable-dependency NAME [DESCRIPTION]`
:    Name and meaning of a (global) variable that is needed to calculate
     the returned value (eg. 2.54 to calculate millimeters from inches).

`@function-dependency NAME [DESCRIPTION]`
:    Name and meaning of a function that is needed to calculate the
     returned value.


#### Variables
`@variable-dependency NAME [DESCRIPTION]`
:    Name and meaning of a (global) variable that is needed to calculate
     value of this variable.

`@function-dependency NAME [DESCRIPTION]`
:    Name and meaning of a function that is needed to calculate the
     value of this variable.

### Adopting Information from other entities

This is not implemented yet, but you are encouraged to use it.

`@adopt ENTITYNAME`
:    copy the tags from the given module, except for the -dependency, param and return tags.

`@adopt-all ENTITYNAME`
:    like adopt but with -dependency, param and return tags.

`@adopt-behavior {replace, append, prepend}` (default: replace)
:    What should happen if a tag is defined in the adopting entity?
     Sets the default behavior, see below.

`@TAGNAME-{replace, append, prepend} VALUE`  
`@TAGNAME-{remove}`  
`@TAGNAME-list|dict-replace [ITEM_TO_REPLACE] VALUE[, VALUE, ...]`  
`@TAGNAME-list|dict-remove ITEM_TO_REMOVE[,ITEM_TO_REMOVE, ...]`  
`@TAGNAME-list|dict-{append, prepend} VALUE[, VALUE, ...]`  
:    Override the default behavior for the given Tag.

#### Adoption Example:
source entity:

    @author foo bar
    @author bla blubb
    @tag-list apples, oranges, bananas

target entity:

    @author-replace xyz abc -> @author xyz abc
    @tag-list-replace grapes, pineapple -> @tag-list grapes, pineapple
    @tag-list-replace apples   pineapples -> @tag-list pineapples, oranges, bananas
    @tag-list-replace apples   grapes, pineapple -> @tag-list grapes, pineapple, oranges, bananas

    @author-append xyz abc -> @author foo bar, @author bla blubb, @author xyz abc
    @tag-list-append grapes, pineapple -> @tag-list apples, oranges, banana, grapes, pineapple

    @author-prepend xyz abc -> @author xyz abc, @author foo bar, @author bla blubb
    @tag-list-prepend grapes, pineapple -> @tag-list grapes, pineapple, apples, oranges, banana

    @author-remove -> (no @author)
    @tag-list-remove oranges, bananas -> @tag-list apples
    
    @author xyz abc -> ??? (behavior depends on @adopt-behavior, default is replace)
    @tag-list grapes, pineapple -> ??? (behavior depends on @adopt-behavior, default is replace)
    @tag-list apples   grapes, pineapple -> ??? (behavior depends on @adopt-behavior, default is replace)

#### What are dependencies?
A entity may have dependencies. These are those entities that are needed
to produce the correct output created in this entity. An Example:

```OpenSCAD
module A(){
     cube(10);
}
module B(){
    translate([10,0,0]) A();
}
```
Module A has no dependencies. Module B depends on Module A.

```OpenSCAD
module C(){
    rotate([90,0,0]) B();
}
module D(){
    A();
    C();
}
```
Module C depends on module B, only this dependency has to be defined.

Module D depends on module A and C, both dependencies need to be defined.

So here is the example with correct comments:

```OpenSCAD
/**
 * A simple cube as a simple example.
 */
module A(){
     cube(10);
}
/**
 *  @module-dependency A a Cube.
 */
module B(){
    translate([10,0,0]) A();
}
/**
 *  @module-dependency B a translated Cube.
 */
module C(){
    rotate([90,0,0]) B();
}
/**
 *  @module-dependency A a Cube.
 *  @module-dependency C a translated and rotated Cube.
 */
module D(){
    A();
    C();
}
```

The file, that only contains this example would not have any
dependencies at all.

### Styleguide
Where possible one should stick to the [javadoc styleguide](http://www.oracle.com/technetwork/java/javase/documentation/index-137868.html#styleguide)

Differences to the javadoc styleguide and notes:

  * There is no need to use \<code\> tags for keywords and names.
  * There are no inline links yet. But you still may use them economically.
    Maybe there will be inline links in the future.
