'''
    scadlib.py: A tool to create and manage libraries for OpenSCAD.

    Copyright (C) 2015  Hauke Thorenz <htho@thorenz.net>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
# import statements: We use pythons included batteries!
import re
import os
import json

VERSION = 0.1

open_scad_keywords = "module function cube cylinder square circle sphere polyhedron square circle polygon import_dxf import_stl difference union intersection render include use projection translate rotate scale mirror hull multimatrix color minkowski $fn $fs $fa linear_extrude rotate_extrude if else for abs acos asin atan atan2 ceil cos exp floor ln log lookup sqrt tan sin sign round rands pow min max str".split()

# ####################### I/O HELPER FUNCTIONS ########################


def printConsole(s, minimumVerbosityLevel):
    """Write the given string to the console. To be printed
    args.verbose needs to be >= minimumVerbosityLevel."""

    global args
    if not args.quiet and args.verbose >= minimumVerbosityLevel:
        print(s)


def determineOutFile(defaultFilenameToDeriveFrom=None, defaultExtensionInfix=None, defaultExtensionOverride=None):
    global args
    if args.output is None:
        return None
    else:
        if args.output == "":
            if defaultFilenameToDeriveFrom is None:
                outFile = "out"
                if defaultExtensionInfix is not None:
                    outFile = outFile + "." + defaultExtensionInfix
                if defaultExtensionOverride is not None:
                    outFile = outFile + "." + defaultExtensionOverride
            else:
                outFile = os.path.basename(defaultFilenameToDeriveFrom).rsplit(".", 1)
                if defaultExtensionInfix is not None:
                    outFile[0] = outFile[0] + "." + defaultExtensionInfix
                if defaultExtensionOverride is not None:
                    outFile[1] = defaultExtensionOverride
                outFile = outFile[0] + outFile[1]
        else:
            outFile = args.output
        return outFile


def outputHelper(fileContent, outFile):
    global args
    override = True
    if outFile is not None and os.path.exists(outFile):
        if args.override:
            override = True
            pass
        elif args.dont_override:
            override = False
        else:
            ans = None
            while ans is None:
                tmp_ans = input("'{}' already exists. Do you want to override it? (y/n)".format(outFile))
                if tmp_ans.strip().lower() == "y":
                    ans = True
                elif tmp_ans.strip().lower() == "n":
                    ans = False
                else:
                    print("Please type 'y' for Yes and 'n' for No.\n")
            if ans is True:
                override = True
            else:
                override = False

    if outFile is None or override is False:
        printConsole(fileContent, 0)
    else:
        with open(outFile, 'w') as f:
            f.write(fileContent)


# ####################### re HELPERS/PATTERN ########################


re_pattern_multilinecomment_info = re.compile(r"(?P<info>/\*\*.*?\*/)", re.MULTILINE + re.DOTALL)

re_pattern_comment = re.compile(r"^.*?(?P<ignore>//.*)$", re.MULTILINE)  # Matches a single line comment
re_pattern_multilinecomment = re.compile(r"(?P<ignore>/\*.*?\*/)", re.MULTILINE + re.DOTALL)  # Matches a multiline comment

re_pattern_include = re.compile(r"include\s*\<(?P<includePath>.*?)\>", re.MULTILINE)
re_pattern_use = re.compile(r"use\s*\<(?P<usePath>.*?)\>", re.MULTILINE)

re_pattern_module_definition = re.compile(r"module\s+(?P<name>\w+)\s*\((?P<arguments>.*?)\).*?(?P<startBracket>\{)", re.MULTILINE + re.DOTALL)
re_pattern_variable_definition = re.compile(r"(?P<name>\w+)\s*\=\s*(?P<value>.*?);", re.MULTILINE)
re_pattern_function_definition = re.compile(r"function\s+(?P<name>\w+)\s*\((?P<arguments>.*?)\).*?\=\s*(?P<statememts>.*);", re.MULTILINE + re.DOTALL)


def re_get_occupied_positions_set(inString, patternList, relevantMatchGroup=0):
    """Get a list of all the positions in the given string, that are
    occupied by the matches from the given pattenList
    range(match.span(relevantMatchGroup))."""
    ret = list()

    for pattern in patternList:
        matchIter = re.finditer(pattern, inString)
        for match in matchIter:
            span = match.span(relevantMatchGroup)
            ret.extend(range(span[0], span[1]))

    return set(ret)

# ####################### TXT HELPERS ########################


def txt_get_bracket_close_pos(inString, startPos, bracketOpenChar, bracketCloseChar, excludedPositions=list()):
    """Find the position of the bracket that closes the section opened
    by the bracket at the given position."""
    if(inString[startPos] != bracketOpenChar):
        raise ValueError("Expecting pos ({}) to be the the position of the opening bracket, instead found '{}' there.".format(startPos, inString[startPos]))
    pos = startPos
    openBrackets = 0
    while pos < len(inString):
        while pos in excludedPositions:
            pos = pos + 1
        c = inString[pos]
        if c == bracketOpenChar:
            openBrackets = openBrackets + 1
        elif c == bracketCloseChar:
            openBrackets = openBrackets - 1

        if openBrackets == 0:
            return pos

        pos = pos + 1

    raise ValueError("The given string does not have balanced brackets.")


def txt_text_to_comment(string="", isInfoComment=True):
    """Make the given string a beautiful comment."""

    if isInfoComment:
        ret = "/**"
    else:
        ret = "/*"

    if len(string.splitlines()) > 1:
        ret = ret + "\n" + txt_prefix_each_line(string, " * ") + "\n"
    else:
        ret = ret + " " + string

    return ret + " */"


def txt_comment_to_text(comment, isInfoComment=True):
    """
    Make the given comment string a normal text.

    Take a comment string and remove the asterisks, openers etc.
    The string may have asterisks opening each line or none. If there
    is one line that does not begin with an asterisk, all other asterisks
    are interpreted as part of the text.

    Working Example:
        In:
        '/**
         * Foo
         * Bar
         */'
         OR
         '/**
         Foo
         Bar
         */'
        Out:
        'Foo
        Bar'

    Failing Example:
        In:
        '/**
         * Foo
           Bar
         */'
         OR
        Out:
        '* Foo
        Bar'

    :TODO: This could be *much* more error tolerant!
    """
    if isInfoComment:
        opener = "/**"
    else:
        opener = "/*"

    if not comment.startswith(opener):
        raise ValueError("The comment string must start with '/**', but instead starts with: '{}'".format(comment[0:10]))
    if not comment.endswith("*/"):
        raise ValueError("The comment string must end with '*/', but instead ends with: '{}'".format(comment[:-10]))

    comment = comment.lstrip(opener)
    comment = comment.rstrip("*/")

    ret = list()

    lines = comment.splitlines()

    ret.append(lines[0])  # don't touch the first line we stripped it already

    lines = lines[1:-1]

    hasAsteriskColumn = True
    for line in lines:
        if not (line.startswith(" * ") or line == (" *")):
            hasAsteriskColumn = False

    if hasAsteriskColumn:
        for line in lines:
            ret.append(line[3:])
        return "\n".join(ret)
    else:
        return "\n".join(lines)


def txt_pretty_print(v, indent=0, kvsep=" : "):
    ret = ""
    if isinstance(v, dict):
        for key, value in v.items():
            ret = ret + "\n" + ("    " * (indent + 0)) + repr(key) + kvsep + txt_pretty_print(value, indent=indent + 1)
    elif isinstance(v, (list, set)):
        l = []
        for item in v:
            l.append(txt_pretty_print(item, indent=indent + 1))
        l = ",\n".join(l)
        l = txt_prefix_each_line(l, ("    " * (indent + 0)))
        ret = ret + l
    else:
        ret = ret + repr(v)
    return ret


def txt_prefix_each_line(string, prefix, ignorefirst=False, ignorelast=False):
    """prefix each line in the given string with the given prefix.
    Useful for block indention."""
    ret = list()
    splitted = string.splitlines()
    if len(splitted) == 0:
        return ""

    if ignorefirst:
        ret.append(splitted[0])
        splitted = splitted[1:]
        if len(splitted) == 0:
            return "\n".join(ret)

    last = None
    if ignorelast:
        last = splitted[-1]
        splitted = splitted[:-1]
        if len(splitted) == 0:
            return "\n".join(ret.append(last))

    for line in splitted:
        ret.append(prefix + line)

    if ignorelast:
        ret.append(last)

    return "\n".join(ret)


# ####################### CLASSES ########################
class ScadDoc():
    """
    :TODO: Implement the new tags and behaviour:
"@adopt ENTITYNAME"
    copy the tags from the given module, except for the -dependency, param and return tags.
"@adopt-all ENTITYNAME"
    like adopt but with -dependency, param and return tags.
"@adopt-behavior {replace, append, prepend} (default: replace)"
    What should happen if a tag is defined in the adopting entity?
    Sets the default behavior, see below.
"@TAGNAME-{replace VALUE, append VALUE, prepend VALUE, remove}"
"@TAGNAME-list/dict-{replace [ITEM_TO_REPLACE] VALUE[, VALUE, ...], append VALUE[, VALUE, ...], prepend VALUE[, VALUE, ...], remove ITEM_TO_REMOVE[,ITEM_TO_REMOVE, ...]}"
    Override the default behavior for the given Tag.
    Example:
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
    """
    commonDictionaryTags = frozenset([])
    fileDictionaryTags = frozenset(["variable-dependency", "module-dependency", "function-dependency"] + list(commonDictionaryTags))
    moduleDictionaryTags = frozenset(["param", "variable-dependency", "module-dependency", "function-dependency"] + list(commonDictionaryTags))
    functionDictionaryTags = frozenset(["param", "variable-dependency", "function-dependency"] + list(commonDictionaryTags))
    variableDictionaryTags = frozenset(["variable-dependency", "function-dependency"] + list(commonDictionaryTags))

    commonListTags = frozenset(["tag-list", "category-list"])
    fileListTags = frozenset([] + list(commonListTags))
    moduleListTags = frozenset([] + list(commonListTags))
    functionListTags = frozenset([] + list(commonListTags))
    variableListTags = frozenset([] + list(commonListTags))

    commonOfficialTags = ["description", "uri", "tag-list", "category-list", "author", "version", "note", "see", "license-short", "license", "license-link"]
    fileOfficialTags = ["filename"] + commonOfficialTags + ["variable-dependency", "function-dependency", "module-dependency"]
    moduleOfficialTags = commonOfficialTags + ["variable-dependency", "function-dependency", "module-dependency", "param"]
    functionOfficialTags = commonOfficialTags + ["variable-dependency", "function-dependency", "param", "return"]
    variableOfficialTags = commonOfficialTags + ["variable-dependency", "function-dependency"]

    def __init__(self, text, scadType=None, inScadFile=None):
        self.__rawMetaDataTupelList = ScadDoc.__metadataListFromText(text)
        self._metaData = dict()

        self.inScadFile = inScadFile

        self.officialTags = None
        self.listTags = None
        self.dictionaryTags = None
        if scadType is None:
            self.makeUniversalDoc()
        else:
            self.makeTypeSpecific(scadType)

    def getList(self, tag):
        if tag in self._metaData.keys():
            if self.isDict(tag):
                return list(self._metaData[tag].keys())
            else:
                return list(self._metaData[tag])
        else:
            return []

    def getFirst(self, tag):
        if self.has(tag):
            return self.getList(tag)[0]
        else:
            return None

    def getDesc(self, tag, key):
        if self.isDict(tag):
            return self._metaData[tag][key]
        else:
            return None

    def has(self, tag):
        return tag in self._metaData.keys()

    def isUnique(self, tag):
        return self.count(tag) == 1

    def isOfficial(self, tag):
        return tag in self.officialTags

    def count(self, tag):
        return len(self.getList(tag))

    def isDict(self, tag):
        return tag in self.dictionaryTags or tag.endswith("-dict")

    def getDict(self, tag):
        if self.isDict(tag):
            if tag in self._metaData.keys():
                return self._metaData[tag]
            return dict()
        return None

    def isList(self, tag):
        return tag in self.listTags or tag.endswith("-list")

    def add(self, key, value):
        self.__rawMetaDataTupelList.append((key, value))
        self.__reBuildDicts()

    def set(self, key, value):
        toRemove = list()
        for k, v in self.__rawMetaDataTupelList:
            if k == key:
                toRemove.append((k, v))
        for rem in toRemove:
            self.__rawMetaDataTupelList.remove(rem)
        self.add(key, value)

    @staticmethod
    def __metadataListFromText(string):
        """Creates a list of key value tuples."""
        if string == "":
            return list()
        READ_VALUE = 1
        READ_KEY = 2

        ret = list()
        key = "description"
        current = []
        state = READ_VALUE
        hadNewline = True
        used = "\n"
        for c in string:
            if state == READ_VALUE:
                if c != '@' or not used.rstrip(" \t").endswith("\n"):
                    current.append(c)
                else:
                    val = ("".join(current)).lstrip().rstrip()
                    ret.append((key, val))
                    current = []
                    key = None
                    state = READ_KEY
            if state == READ_KEY:
                if c != ':' and c != ' ':
                    current.append(c)
                else:
                    key = ("".join(current)).lstrip().rstrip()[1:]
                    current = []
                    state = READ_VALUE

            used = used + c

        val = ("".join(current)).lstrip().rstrip()
        ret.append((key, val))
        return ret

    def __reBuildDicts(self):
        self._metaData = dict()

        for line in self.__rawMetaDataTupelList:
            tag = line[0].strip()
            value = line[1].strip()
            if value != "":
                if self.has(tag):
                    self._metaData[tag].append(value)
                else:
                    self._metaData[tag] = [value]
        for tag, valueList in self._metaData.items():
            if self.isDict(tag):
                insDict = dict()
                for value in valueList:
                    # TODO: Allow quoting.
                    value = str(value).split(sep=None, maxsplit=1)
                    value[0] = value[0].strip()
                    if len(value) > 1:
                        value[1] = value[1].strip()
                    else:
                        value.append("")

                    insDict[value[0]] = value[1]
                self._metaData[tag] = insDict
            if self.isList(tag):
                insList = list()
                for value in valueList:
                    value = value.split(",")
                    insList.extend(value)
                self._metaData[tag] = insList

    def makeTypeSpecific(self, scadType):
        if not issubclass(scadType, ScadType):
            raise TypeError("Type must inherit from ScadType(ScadFile, ScadModule, ScadFunction or ScadVariable) but is '{}'.".format(scadType))

        if scadType is ScadFile:
            self.makeFileDoc()
        elif scadType is ScadModule:
            self.makeModuleDoc()
        elif scadType is ScadFunction:
            self.makeFunctionDoc()
        elif scadType is ScadVariable:
            self.makeVariableDoc()

    def makeFileDoc(self):
        self.type = ScadFile
        self.officialTags = ScadDoc.fileOfficialTags
        self.listTags = ScadDoc.fileListTags
        self.dictionaryTags = ScadDoc.fileDictionaryTags
        self.__reBuildDicts()

    def makeModuleDoc(self):
        self.type = ScadModule
        self.officialTags = ScadDoc.moduleOfficialTags
        self.listTags = ScadDoc.moduleListTags
        self.dictionaryTags = ScadDoc.moduleDictionaryTags
        self.__reBuildDicts()

    def makeFunctionDoc(self):
        self.type = ScadFunction
        self.officialTags = ScadDoc.functionOfficialTags
        self.listTags = ScadDoc.functionListTags
        self.dictionaryTags = ScadDoc.functionDictionaryTags
        self.__reBuildDicts()

    def makeVariableDoc(self):
        self.type = ScadVariable
        self.officialTags = ScadDoc.variableOfficialTags
        self.listTags = ScadDoc.variableListTags
        self.dictionaryTags = ScadDoc.variableDictionaryTags
        self.__reBuildDicts()

    def makeUniversalDoc(self):
        self.type = None
        self.officialTags = ScadDoc.commonOfficialTags
        self.listTags = ScadDoc.commonListTags
        self.dictionaryTags = ScadDoc.commonDictionaryTags
        self.__reBuildDicts()

    def getDependencies(self):
        ret = list()
        if self.has("module-dependency"):
            for name, description in self.getDict("module-dependency").items():
                ret.append(ScadEntityDependency(name, description, ScadModule))
        if self.has("function-dependency"):
            for name, description in self.getDict("function-dependency").items():
                ret.append(ScadEntityDependency(name, description, ScadFunction))
        if self.has("variable-dependency"):
            for name, description in self.getDict("variable-dependency").items():
                ret.append(ScadEntityDependency(name, description, ScadVariable))
        return ret

    def __str__(self):
        text = self._asScadText()
        if len(text.splitlines()) > 1:
            return "ScadDoc({type})[\n{s}\n]".format(type=self.type.__name__, s=txt_prefix_each_line(self._asScadText(), "    "))
        else:
            return "ScadDoc({type})[{s}]".format(type=self.type.__name__, s=self._asScadText())

    def __repr__(self):
        return "ScadDoc({type})[{description}]".format(type=self.type.__name__, description=str(self.getFirst("description"))[:20])

# # TODO: Maybe they will be needed sooner or later?
#
#     def __eq__(self, other):
#     """TODO: Does this work?"""
#         return self.__rawMetaDataTupelList == other.__rawMetaDataTupelList
#
#     def __hash__(self):
#     """TODO: Does this work?"""
#         hash = 0
#         for t in self.__rawMetaDataTupelList:
#             for i in t:
#                 hash = hash ^ hash(i)
#         return hash

    def asScad(self):
        return txt_text_to_comment(self._asScadText())

    def _asScadText(self):
        availableTags = list(self._metaData.keys())
        availableOfficialTags = list()
        availableUnknownTags = list()

        for tag in availableTags:
            if tag in self.officialTags:
                availableOfficialTags.append(tag)
            else:
                availableUnknownTags.append(tag)

        tagList = availableOfficialTags + availableUnknownTags

        ret = list()
        if "description" in tagList:
            ret.append("\n".join(self.getList("description")))
            tagList.remove("description")

        for tag in tagList:
            valueList = self.getList(tag)
            if tag in self.listTags or tag.endswith("-list"):
                ret.append("@{tag}: \t{value}".format(tag=tag, value=",".join(valueList)))
            else:
                for value in valueList:  # remember this is a list!
                    if tag in self.dictionaryTags or tag.endswith("-dict"):
                        ret.append("@{tag}: {key} \t{value}".format(tag=tag, key=value, value=self.getDesc(tag=tag, key=value)))
                    else:
                        ret.append("@{tag}: \t{value}".format(tag=tag, value=value))
        return "\n".join(ret)


class ScadEntityDependency():
    def __init__(self, name, description, scadEntityType):
        self.name = name
        self.description = description
        if issubclass(ScadEntity, scadEntityType):
            raise TypeError("scadEntityType must inherit from ScadEntity. But type is '{}'".format(type))
        self.scadEntityType = scadEntityType
        self.resolution = None

    def findResolution(self, fileList=list()):
        self.resolution = None
        for scadFile in fileList:
            printConsole("Looking for a resolution for '{}' in '{}'".format(repr(self), repr(scadFile)), 2)
            self.resolution = scadFile.getDependencyResolution(self)
            if self.resolution is not None:
                return scadFile
        return None

    def getResolution(self):
        return self.resolution

    def hasResolution(self):
        return self.resolution is not None

    def getDummyResolution(self):
        meta = ScadDoc("@description !!!!! DUMMY ENTITY !!!!!\n" + self.description, scadType=self.scadEntityType)
        ret = self.scadEntityType(name=self.name, metaData=meta)
        ret.isDummy = True
        return ret

    def __str__(self):
        return """ScadEntityDependency[
    Type: {scadEntityType}
    Name: {self.name}
    Description: {self.name}
    Resolution: {self.resolution}
]""".format(self=self, scadEntityType=self.scadEntityType.__name__)

    def __repr__(self):
        return "ScadEntityDependency[{scadEntityType}['{self.name}']]".format(self=self, scadEntityType=self.scadEntityType.__name__)


class ScadType():
    """An abstract class for everything that has dependencies:
        ScadFile, ScadModule, ScadFunction, ScadVariable
    :TODO: Use abc to make this actually abstract"""
    def __init__(self, metaData):
        self.metaData = metaData
        self.entityDependencies = metaData.getDependencies()

#    def __getTypeDependencies(self, entityType):
#        return list(filter(lambda entityDependency: entityDependency.scadEntityType is entityType, self.entityDependencies))
# #        ret = list()
# #        for entityDependency in self.entityDependencies:
# #            if entityDependency.scadEntityType is entityType:
# #                ret.append(entityDependency)
# #        return ret

    def getModuleDependencies(self):
        return list(filter(lambda entityDependency: entityDependency.scadEntityType is ScadModule, self.entityDependencies))
#        return self.__getTypeDependencies(ScadModule)

    def getFunctionDependencies(self):
        return list(filter(lambda entityDependency: entityDependency.scadEntityType is ScadFunction, self.entityDependencies))
#        return self.__getTypeDependencies(ScadFunction)

    def getVariableDependencies(self):
        return list(filter(lambda entityDependency: entityDependency.scadEntityType is ScadVariable, self.entityDependencies))
#        return self.__getTypeDependencies(ScadVariable)

    def getDependencies(self):
        return self.entityDependencies

    def getDependencyTreeAndUnresolvedDependencies(self, fileList=list()):
        dependencyTree = dict()
        unresolvedDependencies = list()
        for dependency in self.getDependencies():
            fileWithResolution = dependency.findResolution(fileList)
            if dependency.hasResolution():
                resolution = dependency.getResolution()
                dependencyTree[resolution], unres = resolution.getDependencyTreeAndUnresolvedDependencies([fileWithResolution] + fileList)
                unresolvedDependencies.extend(unres)
            else:
                #  raise RuntimeError("No resolution for '{}' found.".format(repr(dependency)))
                unresolvedDependencies.append(dependency)
        if len(dependencyTree) == 0:
            dependencyTree = None
        return (dependencyTree, unresolvedDependencies)

    @staticmethod
    def reduceRedundanciesInDependencyTree(dependencyTree):
        entities = list()
        for entitiy, subTree in dependencyTree.items():
            entities.append(entitiy)
            if subTree is not None:
                entities.extend(ScadType.reduceRedundanciesInDependencyTree(subTree))
        return list(set(entities))

    def asJson(self):
        return "JSON EXPORT NOT IMPLEMENTED YET"


class ScadEntity(ScadType):
    """An abstract class for entities:
        ScadModule, ScadFunction, ScadVariable
    :TODO: Use abc to make this actually abstract"""

    def __init__(self, name, metaData, inScadFile=None):
        ScadType.__init__(self, metaData)
        self.name = name
        self.inScadFile = inScadFile
        self.isDummy = False

    def isResolution(self, dependency):
        if not isinstance(dependency, ScadEntityDependency):
            raise TypeError("dependency needs to be of type 'ScadEntityDependency' but is '{}'".format(type(dependency)))
        if isinstance(self, dependency.scadEntityType):
            if dependency.name == self.name:
                return True
        return False

    def asDump(self):
        """Return the text that defines this entity."""
        if self.inScadFile is None:
            raise RuntimeError("Can only dump an entity that is defined in an actual file. (self.inScadFile is None)")
        return self.inScadFile.scadFile.content[self.inScadFile.startPosition:self.inScadFile.endPosition]

    def __str__(self):
        meta = txt_prefix_each_line(str(self.metaData), "        ")
        dependencies = txt_prefix_each_line(txt_pretty_print(self.getDependencies()), "        ")
        return """{type}[
    Name: '{self.name}'{{typeSpecific}}
    Defined in: {self.inScadFile}
    Meta:
{meta}
    Dependencies: [
{dependencies}
    ]
]""".format(self=self, dependencies=dependencies, meta=meta, type=type(self).__name__)

    def __repr__(self):
        return """{type}['{self.name}']""".format(self=self, type=type(self).__name__)

    def __eq__(self, othr):
        """http://stackoverflow.com/a/19073010/1635906"""
        return (isinstance(othr, type(self)) and (self.name) == (othr.name))

    def __hash__(self):
        """http://stackoverflow.com/a/19073010/1635906"""
        return (hash(self.name))


class ScadFileDummy(ScadType):
    """fakes an ScadFile to provide ScadFile Functions for non recursive ScadFiles"""
    def __init__(self, targetPath):
        if targetPath == "":
            raise ValueError("The purpose of ScadFileDummy is to store a path, so it must not be None or empty.")
        self._printablePath = os.path.relpath(targetPath, ScadFileFromFile.referencePath)

    def __repr__(self):
        return """ScadFileDummy['{self._printablePath}']""".format(self=self)

    def __str__(self):
        return """ScadFileDummy[
    Target: "{self._printablePath}"
]""".format(self=self)


class ScadFile(ScadFileDummy):
    """represents a .scad file."""

    def __init__(self, metaData=ScadDoc(""), definedEntities=list(), referencedFiles=list(), statements="", recursive=False):
        self.metaData = metaData
        self.definedEntities = definedEntities
        self.referencedFiles = referencedFiles
        self.statements = statements
        self.recursive = recursive

    def getDependencyResolution(self, scadEntityDependency):
        """Look for a resolution for the given dependency in this file
        and in the files that are referenced in this file."""
        for entity in self.getAvailableEntities():
            printConsole("Checking if '{ent}' is resolved by '{res}'".format(ent=repr(scadEntityDependency), res=repr(entity)), 2)
            if entity.isResolution(scadEntityDependency):
                return entity
        return None

# Direct/Indirect member access

# statements
    def getStatements(self):
        return self.statements

    def setStatements(self, statements):
        self.statements = statements


# entities
    def addDefinedEntity(self, entity):
        if not isinstance(entity, ScadEntity):
            raise TypeError("The given entity must be of type ScadEntity(ScadModule, ScadFunction, ScadVariable) but is '{}'".format(type(entity)))
        self.definedEntities.append(entity)

    def getDefinedEntities(self):
        """get all the entities (ScadEntity) that are defined in THIS file."""
        return self.definedEntities

    def getDefinedModules(self):
        """get all the modules (ScadModule) that are defined in THIS file."""
        return list(filter(lambda entity: isinstance(entity, ScadModule), self.definedEntities))

    def getDefinedFunctions(self):
        """get all the functions (ScadFunction) that are defined in THIS file."""
        return list(filter(lambda entity: isinstance(entity, ScadFunction), self.definedEntities))

    def getDefinedVariables(self):
        """get all the variables (ScadVariable) that are defined in THIS file."""
        return list(filter(lambda entity: isinstance(entity, ScadVariable), self.definedEntities))

# references
    def addReferencedFile(self, fileReference):
        if not isinstance(fileReference, ScadFileReference):
            raise TypeError("The given fileReference must be of type ScadFileReference(ScadIncludeFileReference, ScadUseFileReference) but is '{}'".format(type(fileReference)))
        self.referencedFiles.append(fileReference)

    def getReferencedFiles(self):
        """get all the files that are referenced (ScadFileReference) in THIS file."""
        return self.referencedFiles

    def getIncludedFiles(self):
        """get all the files that are included (ScadIncludeFileReference) in THIS file."""
        return list(filter(lambda reference: isinstance(reference, ScadIncludeFileReference), self.getReferencedFiles()))

    def getUsedFiles(self):
        """get all the files that are used (ScadUseFileReference) in THIS file."""
        return list(filter(lambda reference: isinstance(reference, ScadUseFileReference), self.getReferencedFiles()))

# Recursion functions that only collect data from the references.
    def _getEntitiesFromReferences(self):
        """If recursive, get all the entities (ScadEntity) that are
        defined in files that are referenced in this file."""
        if not self.recursive:
            raise RuntimeError("Not recursive. In order to find more than defined Entities, this instance needs to be recursive!")
        ret = list()
        for scadFileReference in self.getReferencedFiles():
            ret.extend(scadFileReference.toScadFile.getAvailableEntities())
        return ret

    def _getReferencedFilesFromReferences(self):
        if not self.recursive:
            raise RuntimeError("Not recursive. In order to find more than references defined in this file, this instance needs to be recursive!")
        ret = list()
        for scadFileReference in self.getReferencedFiles():
            ret.extend(scadFileReference.toScadFile.getAvailableReferences())
        return ret

# Recursion functions that combine data from references with data from this instance.
# entities
    def getAvailableEntities(self):
        if self.recursive:
            return self.getDefinedEntities() + self._getEntitiesFromReferences()
        else:
            return self.getDefinedEntities()

    def getAvailableModules(self):
        return list(filter(lambda entity: isinstance(entity, ScadModule), self.getAvailableEntities()))

    def getAvailableFunctions(self):
        return list(filter(lambda entity: isinstance(entity, ScadFunction), self.getAvailableEntities()))

    def getAvailableVariables(self):
        return list(filter(lambda entity: isinstance(entity, ScadVariable), self.getAvailableEntities()))

# references
    def getAvailableReferences(self):
        if self.recursive:
            return self.getReferencedFiles() + self._getReferencedFilesFromReferences()
        else:
            return self.getReferencedFiles()

    def getAvailableIncludedFiles(self):
        return list(filter(lambda reference: isinstance(reference, ScadIncludeFileReference), self.getAvailableReferences()))

    def getAvailableUsedFiles(self):
        return list(filter(lambda reference: isinstance(reference, ScadUseFileReference), self.getAvailableReferences()))

# Output Functions
    def asScad(self, recursive=False, excludeList=list(), dummiesFirst=False):
        """Return the content of this File built from the data in this file.
        Not the content (which is the difference from asDump()).
        """
        if recursive:
            entities = self.getAvailableEntities()
        else:
            entities = self.getDefinedEntities()

        entities = list(filter(lambda entity: entity not in excludeList, entities))

        if dummiesFirst:
            entities = sorted(entities, key=(lambda entity: entity.isDummy), reverse=True)

        references = self.getReferencedFiles()
        referencesAsScad = list()
        for reference in references:
            referencesAsScad.append(reference.asScad())
        referencesAsScad = "\n".join(referencesAsScad)

        entitiesAsScad = list()
        for entity in entities:
            entitiesAsScad.append(entity.asScad())
        entitiesAsScad = "\n\n".join(entitiesAsScad)

        if recursive:
            # References don't need to be included, as their contnent
            # is part of the entities.
            return "{meta}\n\n{entities}""".format(meta=self.metaData.asScad(), entities=entitiesAsScad)
        else:
            # Also include the references.
            return "{meta}\n\n{references}\n\n{entities}".format(meta=self.metaData.asScad(), references=referencesAsScad, entities=entitiesAsScad)

    def __str__(self):
        meta = txt_prefix_each_line(str(self.metaData), "        ")
        references = txt_prefix_each_line(txt_pretty_print(self.getReferencedFiles()), "        ")
        entities = txt_prefix_each_line(txt_pretty_print(self.getDefinedEntities()), "        ")
        dependencies = txt_prefix_each_line(txt_pretty_print(self.getDependencies()), "        ")
        return """ScadFile[
    Recursive: {self.recursive}
    Meta:
{meta}
    References: [
{references}
    ]
    Defined Entities: [
{entities}
    ]
    Defined Dependencies: [
{dependencies}
    ]
]""".format(self=self, meta=meta, references=references, entities=entities, dependencies=dependencies)

    def __repr__(self):
        return "ScadFile[]"


class ScadFileFromFile(ScadFile):
    referencePath = os.path.curdir

    @staticmethod
    def buildFromFile(path, recursive, referencedFromScadFile=None):
        """helper function to instanciate an ScadFile instance from a file.
        recursive: (True) instanciate all the referenced files (False) Store filenames.
        referencedFromScadFile: To be used when recursively created from another file."""
        with open(path, 'r') as f:
            return ScadFileFromFile(content=f.read(), path=path, referencedFromScadFile=referencedFromScadFile, recursive=recursive)

    @staticmethod
    def buildListFromDirectory(dirName, recursive, traverseSub):
        """helper function to instanciate an ScadFile instance from a file.
        recursive: (True) instanciate all the referenced files (False) Store filenames.
        (don't set recursive unless you exactly know that you need this.)"""
        from os import listdir
        ret = list()
        files = list()

        for entry in listdir(dirName):
            entry = (dirName + os.path.sep + entry)
            if os.path.isdir(entry):
                if traverseSub:
                    ret.extend(ScadFileFromFile.buildListFromDirectory(entry, recursive=recursive, traverseSub=traverseSub))
            elif entry.endswith(".scad"):
                ret.append(ScadFileFromFile.buildFromFile(entry, recursive=recursive, referencedFromScadFile=None))
        return ret

    def __init__(self, path, content="", recursive=False, referencedFromScadFile=None, metaData=None):
        """path must not be emty because we need to write something to the metadata."""
        self.content = content  # The Text.

        self.path = os.path.abspath(path)  # Absolute path of this file.
        self._printablePath = os.path.relpath(self.path, ScadFileFromFile.referencePath)  # A nice to look at relative path.

        self.referencedFromScadFile = referencedFromScadFile  # The reference (if any) to another file. (A ScadFileReference insatance)

        self.recursive = recursive  # Are we looking for information in the files referenced in this file?

        self.__positionLineRangesList = ScadFileFromFile.__txt_getPositionLineRangesList(self.content)  # in which line is the given position?

        # Where are the comments in this file?
        self._commentPositions = frozenset(re_get_occupied_positions_set(self.content, [re_pattern_comment, re_pattern_multilinecomment], "ignore"))

        self.metaData = metaData

        # Extract all the metadata from all comments.
        unusedMetaData = list()
        for infoComment, inScadFile in self.__extractInfoComments_inScadFile():  # The raw texts from the info comments
            metaData = ScadDoc(infoComment, inScadFile=inScadFile)
            unusedMetaData.append(metaData)

        # Find meta data for this file.
        for metaData in unusedMetaData:  # find the meta data for this file
            if metaData.has("filename"):
                if metaData.getFirst("filename") == os.path.basename(self.path):
                    metaData.makeFileDoc()
                    ScadType.__init__(self, metaData)
                    unusedMetaData.remove(metaData)

        self.metaDataIsAutoGenerated = False

        if self.metaData is None:  # We did not find any metadata.
            ScadType.__init__(self, ScadDoc("@filename " + os.path.basename(self.path)))
            self.metaDataIsAutoGenerated = True
            self.metaData.makeFileDoc()

        self._entityContentPositions = list()  # The positions that are occupied by entity content.

        # find references
        self.referencedFiles = list()

        # find included files
        matchesList = ScadFileFromFile.__getFilteredMatches(self.content, re_pattern_include, relevantGroup=0, forbiddenPositions=self._commentPositions)
        for match in matchesList:
            self._entityContentPositions.extend(range(match.start(), match.end() + 1))
            targetPath = match.group("includePath")
            reference = ScadIncludeFileReference(InScadFile(scadFile=self, referencePosition=match.start(), startPosition=match.start(), endPosition=match.end()))
            targetPath = os.path.dirname(self.path) + os.path.sep + targetPath

            if self.recursive:
                referenceScadFile = ScadFileFromFile.buildFromFile(path=targetPath, recursive=self.recursive, referencedFromScadFile=reference)
            else:
                referenceScadFile = ScadFileDummy(targetPath=targetPath)

            reference.setTarget(referenceScadFile)
            self.referencedFiles.append(reference)

        # find used files
        matchesList = ScadFileFromFile.__getFilteredMatches(self.content, re_pattern_use, relevantGroup=0, forbiddenPositions=self._commentPositions)
        for match in matchesList:
            self._entityContentPositions.extend(range(match.start(), match.end() + 1))
            targetPath = match.group("usePath")
            reference = ScadUseFileReference(InScadFile(scadFile=self, referencePosition=match.start(), startPosition=match.start(), endPosition=match.end()))
            targetPath = os.path.dirname(self.path) + os.path.sep + targetPath

            if self.recursive:
                referenceScadFile = ScadFileFromFile.buildFromFile(path=targetPath, recursive=self.recursive, referencedFromScadFile=reference)
            else:
                referenceScadFile = ScadFileDummy(targetPath=targetPath)

            reference.setTarget(referenceScadFile)
            self.referencedFiles.append(reference)

        self.definedEntities = list()

        # find defined MODULES
        matchesList = ScadFileFromFile.__getFilteredMatches(self.content, re_pattern_module_definition, relevantGroup=0, forbiddenPositions=self._commentPositions)
        for match in matchesList:
            name = match.group("name")
            arguments = match.group("arguments")
            startBracketPos = match.start("startBracket")
            startPos = match.start()
            endPos = txt_get_bracket_close_pos(self.content, startBracketPos, '{', '}', self._commentPositions)
            commentStart = startPos
            self._entityContentPositions.extend(range(match.start(), endPos + 1))

            entityContent = self.content[startBracketPos + 1:endPos]

            meta = ScadDoc("")
            for metaData in unusedMetaData:  # find the meta data for the current module
                if metaData.inScadFile.endPosition < startPos:
                    if self.content[metaData.inScadFile.endPosition:startPos].strip() == "":
                        meta = metaData
                        commentStart = metaData.inScadFile.startPosition
                        unusedMetaData.remove(metaData)

            meta.makeModuleDoc()
            scadModule = ScadModule(name, arguments, entityContent, meta, InScadFile(self, referencePosition=match.start(), startPosition=commentStart, endPosition=endPos + 1))
            self.definedEntities.append(scadModule)

        # find defined FUNCTIONS
        matchesList = ScadFileFromFile.__getFilteredMatches(self.content, re_pattern_function_definition, relevantGroup=0, forbiddenPositions=(self._commentPositions.union(set(self._entityContentPositions))))
        for match in matchesList:

            name = match.group("name")
            arguments = match.group("arguments")
            startPos = match.start()
            statememts = match.group("statememts")
            commentStart = match.start()

            self._entityContentPositions.extend(range(match.start(), match.end()))

            meta = ScadDoc("")
            for metaData in unusedMetaData:  # find the meta data for the current function
                if metaData.inScadFile.endPosition < startPos:
                    if self.content[metaData.inScadFile.endPosition:startPos].strip() == "":
                        meta = metaData
                        commentStart = metaData.inScadFile.startPosition
                        unusedMetaData.remove(metaData)

            meta.makeFunctionDoc()
            scadFunction = ScadFunction(name, arguments, statememts, meta, InScadFile(self, referencePosition=match.start(), startPosition=commentStart, endPosition=match.end()))
            self.definedEntities.append(scadFunction)

        # find defined VARIABLES
        matchesList = ScadFileFromFile.__getFilteredMatches(self.content, re_pattern_variable_definition, relevantGroup=0, forbiddenPositions=(self._commentPositions.union(set(self._entityContentPositions))))
        for match in matchesList:
            name = match.group("name")
            value = match.group("value")
            namePos = match.start("name")
            commentStart = match.start()

            self._entityContentPositions.extend(range(match.start(), match.end()))

            meta = ScadDoc("")
            for metaData in unusedMetaData:  # find the meta data for the current variable
                if metaData.inScadFile.endPosition <= namePos:
                    if self.content[metaData.inScadFile.endPosition:namePos - 1].strip() == "":
                        meta = metaData
                        commentStart = metaData.inScadFile.startPosition
                        unusedMetaData.remove(metaData)

            meta.makeVariableDoc()
            scadVariable = ScadVariable(name, value, meta, InScadFile(self, referencePosition=match.start(), startPosition=commentStart, endPosition=match.end()))

            self.definedEntities.append(scadVariable)

            usedPositions = (self._commentPositions.union(set(self._entityContentPositions)))
            pos = 0
            self.statements = []
            for c in self.content:
                if pos not in usedPositions:
                    self.statements.append(c)
                pos = pos + 1
            self.statements = "".join(self.statements)
            self.statements = "\n".join(filter(lambda line: line.strip() != "", self.statements.splitlines()))

    def __extractInfoComments_inScadFile(self):
        """return all the comments that store parsable information.
        returns a tupel of the raw text, the start position and the
        end position in content."""
        ret = list()
        matchIter = re.finditer(re_pattern_multilinecomment_info, self.content)
        for match in matchIter:
            span = match.span("info")
            raw = self.content[span[0]:span[1]]
            cleaned = txt_comment_to_text(raw)
            ret.append((cleaned, InScadFile(self, referencePosition=span[0], startPosition=span[0], endPosition=span[1])))
        return ret

    def _getLineAndPositionInLine(self, position):
        """get a dictionary with information about line and position in
        line for the given position in the content string.
        :note: line_num and line_pos start with 1."""
        line_num = 1
        for posRange in self.__positionLineRangesList:
            if position in posRange:
                return {"position": position, "line_num": line_num, "line_pos": position - posRange[0] + 1}
            line_num = line_num + 1
        return None

    @staticmethod
    def __txt_getPositionLineRangesList(string):
        """returns the data for _getLineAndPositionInLine()

        Get a list with an item for each line in the given string.
        Each item is a range that covers the positions the line given
        line.

        Example:
            >>> __txt_getPositionLineRangesList('foo\nbar')
            [range(0, 4), range(4, 7)]
        """
        lines = str(string).splitlines(True)
        ret = list()
        pos = 0
        for line in lines:
            newPos = pos + len(line)
            ret.append(range(pos, newPos))
            pos = newPos
        return ret

    @staticmethod
    def __getFilteredMatches(content, pattern, relevantGroup=0, forbiddenPositions=set()):
        """find all the matches for pattern in the given string.
        only return those that do not have positions in common with the
        set of forbiddenPositions.

        'Hey there is an entitiy definition!' - 'oh but it's commented!'"""
        ret = list()
        matchList = list(re.finditer(pattern, content))
        matchList = filter(lambda match: set(range(*match.span(relevantGroup))).isdisjoint(forbiddenPositions), matchList)  # filter matches in ignored sections
        return matchList

    def asDump(self, recursive=False):
        """Returns the content of this file.
        If recursive copies the content of included files and the
        modules from used files."""

        if not recursive:
            return self.content

        ret = self.content.splitlines()
        todo = list()
        for referenced in self.referencedFiles:
            dump = referenced.toScadFile.asDump()
            line_num = referenced.inScadFile.line_num
            todo.append((line_num, dump))

        # Sort reverse so we add lines from the bottom to the top.
        # This way line numbers dont change.
        todo = sorted(todo, key=(lambda tpl: tpl[0]), reverse=True)

        for line_num, dump in todo:
            line_num = line_num - 1  # because line numbers in editors start wit 1 but indices with 0
            insert = "// ------ INCLUDED/USED ------" + "\n"
            insert = insert + "//" + ret[line_num] + "\n"
            insert = insert + "// ---------------------------" + "\n"
            insert = insert + txt_prefix_each_line(dump, "    ") + "\n"
            insert = insert + "// ---------------------------" + "\n"
            ret[line_num] = insert

        return "\n".join(ret)

    def asCompilationDump(self, entities):
        """Create a dump that contains the given entities.
        Replace the references with the entities from the list, that
        are defined by this reference.
        Entities that are not part of a reference will be put right behind
        the file comment."""
        ret = self.content.splitlines()

        # In which of the references (if any) were the entities defined?
        linenum_insertString = list()
        for referencedFile in self.referencedFiles:
            line_num = referencedFile.inScadFile.line_num
            dump = ""
            toRemove = list()
            for entity in entities:
                if entity.inScadFile is not None and entity in referencedFile.inScadFile.scadFile.getAvailableEntities():
                    toRemove.append(entity)
                    dump = dump + entity.asScad() + "\n\n"

            for r in toRemove:
                entities.remove(r)

            line_num = line_num - 1  # because line numbers in editors start wit 1 but indices with 0
            insert = "// ---------- RESOLVED DEPENDENCIES FROM ----------" + "\n"
            insert = insert + "//" + ret[line_num] + "\n"
            insert = insert + "// ------------------------------------------------" + "\n"
            insert = insert + "// (Note that each entity is only copied here once." + "\n"
            insert = insert + "// If it is needed earlier, it is not in this block.)" + "\n"
            insert = insert + "// ------------------------------------------------" + "\n"
            insert = insert + txt_prefix_each_line(dump, "    ") + "\n"
            insert = insert + "// ------------------------------------------------" + "\n"

            linenum_insertString.append((line_num, insert))

        # The entities that were not found in any references:
        dump = ""
        for entity in entities:
            dump = dump + entity.asScad() + "\n\n"

        # put these entities right after the file comment
        line_num = self._getLineAndPositionInLine(self.metaData.inScadFile.endPosition)["line_num"] - 1

        insert = ret[line_num] + "\n\n"
        insert = insert + "// ------ AUTOMATICALLY RESOLVED DEPENDENCIES ------" + "\n\n"
        insert = insert + txt_prefix_each_line(dump, "    ") + "\n"
        insert = insert + "// -------------------------------------------------" + "\n"

        linenum_insertString.append((line_num, insert))

        # replace the the original file comment wit the current.
        newFileComment = self.metaData.asScad()
        oldFileCommentStart = self._getLineAndPositionInLine(self.metaData.inScadFile.startPosition)["line_num"] - 1
        linenum_insertString.append((line_num, newFileComment))
        oldFileCommentEnd = self._getLineAndPositionInLine(self.metaData.inScadFile.endPosition)["line_num"]
        for pos in range(oldFileCommentStart, oldFileCommentEnd):
            linenum_insertString.append((pos, None))

        # Sort reverse so we add lines from the bottom to the top.
        # This way line numbers dont change.
        linenum_insertString = sorted(linenum_insertString, key=(lambda tpl: tpl[0]), reverse=True)

        for line_num, insert in linenum_insertString:
            ret[line_num] = insert

        while None in ret:
            ret.remove(None)
        return "\n".join(ret)

    def __str__(self):
        meta = txt_prefix_each_line(str(self.metaData), "        ")
        references = txt_prefix_each_line(txt_pretty_print(self.getReferencedFiles()), "        ")
        entities = txt_prefix_each_line(txt_pretty_print(self.getDefinedEntities()), "        ")
        dependencies = txt_prefix_each_line(txt_pretty_print(self.getDependencies()), "        ")
        return """ScadFileFromFile[
    Path: "{self._printablePath}"
    Recursive: {self.recursive}
    Referenced from: {self.referencedFromScadFile}
    Meta:
{meta}
    References: [
{references}
    ]
    Defined Entities: [
{entities}
    ]
    Defined Dependencies: [
{dependencies}
    ]
]""".format(self=self, meta=meta, references=references, entities=entities, dependencies=dependencies)

    def __repr__(self):
        return """ScadFileFromFile['{self._printablePath}']""".format(self=self)


class ScadModule(ScadEntity):
    """Represents a module in scad files."""
    def __init__(self, name, arguments="", content="", metaData=ScadDoc(""), inScadFile=None):
        ScadEntity.__init__(self, name, metaData, inScadFile)
        self.arguments = arguments
        self.content = content

    def asScad(self, origin=True):
        """Create a string representation to be used in .scad files."""
        data = dict()
        data['meta'] = self.metaData.asScad()
        data['content'] = txt_prefix_each_line(self.content, "    ", False, False)
        data['origin'] = ""
        if origin:
            data['origin'] = "/* Origin: " + str(self.inScadFile) + " */"

        return """{data[meta]}
module {self.name}({self.arguments}){{{data[origin]}
{data[content]}
}}""".format(self=self, data=data)

    def __str__(self):
        return ScadEntity.__str__(self).format(typeSpecific="\n    Arguments: '" + self.arguments + "'")

    def __eq__(self, othr):
        """http://stackoverflow.com/a/19073010/1635906"""
        return (isinstance(othr, type(self)) and (self.name, self.arguments) == (othr.name, othr.arguments))

    def __hash__(self):
        """http://stackoverflow.com/a/19073010/1635906"""
        return (hash(self.name) ^ hash(self.arguments) ^
                hash((self.name, self.arguments)))


class ScadVariable(ScadEntity):
    """Represents a variable in scad files."""
    def __init__(self, name, value="", metaData=ScadDoc(""), inScadFile=None):
        ScadEntity.__init__(self, name, metaData, inScadFile)
        self.value = value

    def asScad(self, origin=True):
        """Create a string representation to be used in .scad files."""
        data = dict()
        data['meta'] = self.metaData.asScad()
        data['origin'] = ""
        if origin:
            data['origin'] = "/* Origin: " + str(self.inScadFile) + " */"
        return """{data[meta]}
{self.name} = ({self.value}); {data[origin]}""".format(self=self, data=data)

    def __str__(self):
        return ScadEntity.__str__(self).format(typeSpecific="\n    Value: '" + str(self.value) + "'")


class ScadFunction(ScadEntity):
    """Represents a function in scad files."""
    def __init__(self, name, arguments="", content="", metaData=ScadDoc(""), inScadFile=None):
        ScadEntity.__init__(self, name, metaData, inScadFile)
        self.arguments = arguments
        self.content = content

    def asScad(self, origin=True):
        """Create a string representation to be used in .scad files."""
        data = dict()
        data['meta'] = self.metaData.asScad()
        data['origin'] = ""
        if origin:
            data['origin'] = "/* Origin: " + str(self.inScadFile) + " */"
        return """{data[meta]}
function {self.name}({self.arguments}) = {self.content}; {data[origin]}""".format(self=self, data=data)

    def __str__(self):
        return ScadEntity.__str__(self).format(typeSpecific="\n    Arguments: '" + self.arguments + "'")

    def __eq__(self, othr):
        """http://stackoverflow.com/a/19073010/1635906"""
        return (isinstance(othr, type(self)) and (self.name, self.arguments) == (othr.name, othr.arguments))

    def __hash__(self):
        """http://stackoverflow.com/a/19073010/1635906"""
        return (hash(self.name) ^ hash(self.arguments) ^
                hash((self.name, self.arguments)))


class InScadFile():
    """Helps to keep track where a variable/module/function/include/use was defined."""
    def __init__(self, scadFile, referencePosition, startPosition, endPosition):
        self.scadFile = scadFile
        self.referencePosition = referencePosition

        self.startPosition = startPosition
        self.endPosition = endPosition

        d = scadFile._getLineAndPositionInLine(referencePosition)
        self.line_num = d["line_num"]
        self.line_pos = d["line_pos"]
        self.position = d["position"]

    def __str__(self):
        return "'{scadFile._printablePath}'({self.line_num}:{self.line_pos})".format(self=self, scadFile=self.scadFile)


class ScadFileReference():
    """Represents a reference (include/use) to another Scad File.
    Helps to keep track from where a file was included/used.
    :TODO: Use abc to actually make this abstract!"""
    def __init__(self, inScadFile, toScadFile=None):
        if not isinstance(inScadFile, InScadFile):
            raise TypeError("inScadFile must be of Type InScadFile but is '{}'.".format(type(inScadFile)))
        self.inScadFile = inScadFile
        self.setTarget(toScadFile)

    def setTarget(self, toScadFile):
        if not isinstance(toScadFile, ScadFileDummy) and toScadFile is not None:
            raise TypeError("toScadFile must be inherit From ScadFileDummy but is '{}'.".format(type(toScadFile)))

        self.toScadFile = toScadFile

    def getTarget(self):
        if self.toScadFile is None:
            raise RuntimeError("This reference ('{}') does not have a target (yet)!".format(str(self)))
        return self.toScadFile

    def asScad(self):
        if self.toScadFile is None:
            raise RuntimeError("Not target set! self.toScadFile must not be None.")
        # Implementation in ScadIncludeFileReference.asScad and ScadUseFileReference.asScad

    def asDump(self):
        return self.inScadFile.scadFile.content[self.inScadFile.startPosition:self.inScadFile.endPosition]

    def asJson(self):
        return "JSON EXPORT NOT IMPLEMENTED YET"

    def __str__(self):
        return "{}[in={}, to='{}']".format(type(self).__name__, str(self.inScadFile), self.toScadFile._printablePath)

    def __repr__(self):
        return "{}[to='{}']".format(type(self).__name__, self.toScadFile._printablePath)


class ScadIncludeFileReference(ScadFileReference):

    def __init__(self, inScadFile, toScadFile=None):
        ScadFileReference.__init__(self, inScadFile, toScadFile)

    def asScad(self):
        ScadFileReference.asScad(self)
        return "include <{}>".format(self.toScadFile._printablePath)


class ScadUseFileReference(ScadFileReference):

    def __init__(self, inScadFile, toScadFile=None):
        ScadFileReference.__init__(self, inScadFile, toScadFile)

    def asScad(self):
        ScadFileReference.asScad(self)
        return "use <{}>".format(self.toScadFile._printablePath)

# ####################### SCRIPT PART ########################
if __name__ == "__main__":
    import argparse

    def cmd_info_handler(args):
        scadFileList = list()
        for inFile in args.INPUT_FILE_OR_DIR:
            if (os.path.isdir(inFile)):
                scadFileList.extend(ScadFileFromFile.buildListFromDirectory(inFile, recursive=args.recursive, traverseSub=args.traverse_dirs))
            else:
                scadFileList.append(ScadFileFromFile.buildFromFile(inFile, args.recursive))

        toOutput = list()

        if args.self:
            toOutput.extend(scadFileList)
#  This is not as clever as it seems: We don't want all files
#  dumped recursively.
#            if args.recursive:
#                for scadFile in scadFileList:
#                    for ref in scadFile.getAvailableReferences():
#                        toOutput.append(ref.toScadFile)

        if args.modules:
            for f in scadFileList:
                toOutput.extend(f.getAvailableModules())

        if args.variables:
            for f in scadFileList:
                toOutput.extend(f.getAvailableVariables())

        if args.functions:
            for f in scadFileList:
                toOutput.extend(f.getAvailableFunctions())

        if args.includes:
            for f in scadFileList:
                toOutput.extend(f.getIncludedFiles())

        if args.uses:
            for f in scadFileList:
                toOutput.extend(f.getUsedFiles())

        if args.regex:
            # TODO: Use regular expressions to filter the output.
            pass

        if args.with_meta:
            # TODO: filter the output.
            pass

        if args.with_meta_key_value:
            # TODO: filter the output.
            pass

        outString = ""

        for out in toOutput:
            if args.as_scad:
                if isinstance(out, ScadFile):
                    outString = outString + out.asScad(args.recursive) + "\n" + "\n"
                else:
                    outString = outString + out.asScad() + "\n" + "\n"
            elif args.as_json:
                if isinstance(out, ScadFile):
                    outString = outString + out.asJson() + "\n" + "\n"
                else:
                    outString = outString + out.asJson() + "\n" + "\n"
            elif args.as_dump:

                if isinstance(out, ScadFile):
                    outString = outString + out.asDump(args.recursive) + "\n" + "\n"
                else:
                    outString = outString + out.asDump() + "\n" + "\n"
            else:
                outString = outString + str(out) + "\n" + "\n"

        if args.as_scad:
            outFile = determineOutFile(args.INPUT_FILE_OR_DIR[0], "scad.info.", "scad")
        elif args.as_json:
            outFile = determineOutFile(args.INPUT_FILE_OR_DIR[0], "scad.info.", "json")
        elif args.as_dump:
            outFile = determineOutFile(args.INPUT_FILE_OR_DIR[0], "scad.info.dump.", "scad")
        else:
            outFile = determineOutFile(args.INPUT_FILE_OR_DIR[0], "scad.info.", "txt")

        outputHelper(outString, outFile)

    def cmd_compile_handler(args):
        libraryFileList = list()
        if args.lib is not None:
            for libFile in args.lib:
                if (os.path.isdir(libFile)):
                    libraryFileList.extend(ScadFileFromFile.buildListFromDirectory(libFile, recursive=args.recursive, traverseSub=args.traverse_dirs))
                else:
                    libraryFileList.append(ScadFileFromFile.buildFromFile(libFile, args.recursive))

        inputFile = ScadFileFromFile.buildFromFile(args.INPUT_FILE, True)

        if inputFile.metaDataIsAutoGenerated:
            raise ValueError("'{}' did not have a @filename tag with the correct name. IS THE FILENAME TAG CORRECT? We can't build a library without knowing the dependencies.".format(args.INPUT_FILE))

        printConsole(str(inputFile) + "\n", 2)

        if args.mapping:
            if os.path.isfile(args.mapping):
                with open(args.mapping, 'r') as f:
                    jsonMapping = json.load(f)
            else:
                jsonMapping = json.loads(args.mapping)

            printConsole("\nJSON-Mapping:" + txt_prefix_each_line(txt_pretty_print(jsonMapping), "    ") + "\n", 1)

            mappingFile = ScadFile()

            for entityType, mapping in jsonMapping.items():
                for localName, info in mapping.items():
                    if not isinstance(info, dict):
                        info = {"name": info}
                    entity = None
                    if entityType == "modules":
                        if "name" not in info.keys():
                            raise ValueError("For modules, a name must be specified.")
                        if "arguments" not in info.keys():
                            # raise ValueError("For modules, arguments must be specified.")
                            info["arguments"] = ""
                        metaData = ScadDoc("@description: A wrapper from '{source}' to '{target}'.\n@module-dependency {target}".format(source=localName, target=info["name"]), ScadModule)
                        entity = ScadModule(localName, arguments=info["arguments"], content="{}({});".format(info["name"], info["arguments"]), metaData=metaData)
                    elif entityType == "functions":
                        if "name" not in info.keys():
                            raise ValueError("For functions, a name must be specified.")
                        if "arguments" not in info.keys():
                            # raise ValueError("For functions, arguments must be specified.")
                            info["arguments"] = ""
                        metaData = ScadDoc("@description: A wrapper from '{source}' to '{target}'.\n@function-dependency {target}".format(source=localName, target=info["name"]), ScadFunction)
                        entity = ScadFunction(localName, arguments=info["arguments"], content="{}({});".format(info["name"], info["arguments"]), metaData=metaData)
                    elif entityType == "variables":
                        if "name" not in info.keys():
                            raise ValueError("For variables, a name must be specified.")
                        metaData = ScadDoc("@description: A wrapper from '{source}' to '{target}'.\n@variable-dependency {target}".format(source=localName, target=info["name"]), ScadVariable)
                        entity = ScadVariable(localName, info["name"], metaData=metaData)
                    else:
                        raise ValueError("The key for the mapping type must be: 'module', 'function' or 'variable' but is '{}'".format(entityType))
                    mappingFile.addDefinedEntity(entity)

            printConsole("\nMapping-Entities:\n" + txt_prefix_each_line(txt_pretty_print(mappingFile.getDefinedEntities()), "    ") + "\n", 1)
            libraryFileList = [mappingFile] + libraryFileList

        printConsole("Looking for resolutions in these files:\n" + txt_prefix_each_line(txt_pretty_print(libraryFileList), "    ") + "\n", 2)

        dependencyTree, unresolvedDependencies = inputFile.getDependencyTreeAndUnresolvedDependencies([inputFile] + libraryFileList)

        if dependencyTree is None:
            printConsole("""\nWARNING: The dependency tree is empty!
    This means NONE of the defined dependencies could be resolved.

    You may try --traverse in order to search subdirectories.
    Check the name of the defined dependencies.
    Did you forget to include needed files that are not part of the library?

    Dummies will be created...""", 1)
            dependencyTree = dict()

        printConsole("\nDependency Tree:" + txt_pretty_print(dependencyTree, kvsep=" depends on: "), 2)

        neededEntities = ScadEntity.reduceRedundanciesInDependencyTree(dependencyTree)

        if len(unresolvedDependencies) > 0:
            dummyResolutions = list()
            printConsole("\nUnresolved Dependencies:\n" + txt_prefix_each_line(txt_pretty_print(unresolvedDependencies), "    "), 1)
            if not args.dont_create_dummies:
                printConsole("\nCreating dummies for the unresolved dependencies..." + txt_pretty_print(neededEntities), 2)
                for dependency in unresolvedDependencies:
                    dummyResolutions.append(dependency.getDummyResolution())
            printConsole(txt_prefix_each_line(txt_pretty_print(dummyResolutions), "    "), 3)
            neededEntities = neededEntities + dummyResolutions
            neededEntities = list(set(neededEntities))  # should be unnecessary as there should be no duplicates.

        # remove entities that are defined in the input file
        neededEntities = list(filter(lambda entity: entity not in inputFile.getDefinedEntities(), neededEntities))
        printConsole("\nEntities in library:\n" + txt_prefix_each_line(txt_pretty_print(neededEntities), "    "), 2)

        if args.all_in_one:
            outFileName = determineOutFile(args.INPUT_FILE, "allinone.", "scad")
            if outFileName is not None:
                inputFile.metaData.set("filename", outFileName)
            else:
                inputFile.metaData.set("filename", "")
            outString = inputFile.metaData.asScad() + inputFile.asCompilationDump(neededEntities)

        else:
            outFileName = determineOutFile(args.INPUT_FILE, "lib.", "scad")
            outScadFile = ScadFile(definedEntities=neededEntities)
            if outFileName is not None:
                outScadFile.metaData.add("filename", outFileName)
            outString = outScadFile.asScad(dummiesFirst=True)

        outputHelper(outString, outFileName)

    # Argument parsing
    parser = argparse.ArgumentParser(description="Helps to create and maintain fzz2scad libraries.")

    parser.add_argument("-v", "--verbose", action="count", default=0, help="-v -vv- -vvv increase output verbosity")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress any output except for final results.")
    parser.add_argument('-V', '--version', action='version', version="%(prog)s " + str(VERSION))

    subparsers = parser.add_subparsers(dest="cmd")
    parser_info = subparsers.add_parser("info", description="Show information about the given file.")
    parser_info_group_input = parser_info.add_argument_group(title="input", description="How to handle the input files.")
    parser_info_group_input.add_argument("INPUT_FILE_OR_DIR", nargs="+", help="The files/directories that should be searched.")
    parser_info_group_input.add_argument("-t", "--traverse-dirs", action="store_true", help="If a directory is given traverse through the sub directories.")
    parser_info_group_input.add_argument("-r", "--recursive", action="store_true", help="look for information recursively (look in included and used files).")

    parser_info_group_output = parser_info.add_argument_group(title="output", description="What should the output look line?")
    parser_info_group_output.add_argument("-o", "--output", nargs="?", default=None, const="", help="write output to an .scad File instead to console. (if not defined further 'foo.scad' becomes 'foo.info.scad'.)")

    parser_info_group_output_override = parser_info_group_output.add_mutually_exclusive_group()
    parser_info_group_output_override.add_argument("--override", action="store_true", help="Override existing output files without asking.")
    parser_info_group_output_override.add_argument("--dont-override", action="store_true", help="Do not override any existing output files - Print to console instead.")
    parser_info_group_output_override.add_argument("--ask", default="true", action="store_true", help="Ask if an existing file should be overwritten. (default)")

    parser_info_group_output_type = parser_info_group_output.add_mutually_exclusive_group()
    parser_info_group_output_type.add_argument("--as-scad", action="store_true", help="give output that can be used in .scad files.")
    parser_info_group_output_type.add_argument("--as-json", action="store_true", help="give output that is json encoded. Useful for writing a better filter engine. (NOT IMPLEMENTED YET).")
    parser_info_group_output_type.add_argument("--as-dump", action="store_true", help="dump the relevant sections from the content. If recursive, included or used sections will be copied.")

    parser_info_group_selection = parser_info.add_argument_group(title="selection", description="Which information should be extracted?")
    parser_info_group_selection.add_argument("-s", "--self", action="store_true", help="show information about the file itself.")
    parser_info_group_selection.add_argument("-m", "--modules", action="store_true", help="list the modules in the given file.")
    parser_info_group_selection.add_argument("-v", "--variables", action="store_true", help="list the variables in the given file.")
    parser_info_group_selection.add_argument("-f", "--functions", action="store_true", help="list the functions in the given file.")
    parser_info_group_selection.add_argument("-i", "--includes", action="store_true", help="list the files that are included in this file.")
    parser_info_group_selection.add_argument("-u", "--uses", action="store_true", help="list the files that are used by this file.")

    parser_info_group_filter = parser_info.add_argument_group(title="filter", description="Filter the entities. (NOT IMPLEMENTED YET!)")
    parser_info_group_filter.add_argument("--with-meta", help="Only show results with the given metadata field. (NOT IMPLEMENTED YET!)")
    parser_info_group_filter.add_argument("--with-meta-key-value", nargs=2, help="Only show results where the given metadata field has the given value. (NOT IMPLEMENTED YET!)")
    parser_info_group_filter.add_argument("--regex", action="store_true", help="Use regular expressions to specify fields and values. (NOT IMPLEMENTED YET!)")

    parser_compile = subparsers.add_parser("compile", description="Create a library file for the given File.")
    parser_compile_group_input = parser_compile.add_argument_group(title="input", description="How to handle the input files.")

    parser_compile_group_input.add_argument("INPUT_FILE", help="The file to create the library for.")
    parser_compile_group_input.add_argument("-l", "--lib", nargs="+", help="The files/directories that should be searched for the needed entities to create this library.")
    parser_compile_group_input.add_argument("-m", "--mapping", help="A json file or a json string that specifies name mappings for modules, variables and functions. Simple Example:" + """'{ "modules": { "moduleName" : "implementingModuleName" } }'""" + " Example with arguments: " + """'{ "functions": { "functionName" : { "name" : "implementingFunctionName", "arguments" : "argumentString" } } }'""")

    parser_compile_group_input.add_argument("-t", "--traverse-dirs", action="store_true", help="If a directory is given traverse through the sub directories to find .scad files.")
    parser_compile_group_input.add_argument("-r", "--recursive", action="store_true", help="look for entities recursively (look in included and used files).")

    parser_compile_group_output = parser_compile.add_argument_group(title="output", description=None)
    parser_compile_group_output.add_argument("-o", "--output", nargs="?", default=None, const="", help="write output to an .scad File instead to console. (if not defined further 'foo.scad' becomes 'foo.lib.scad'.)")
    parser_compile_group_output_override = parser_compile_group_output.add_mutually_exclusive_group()
    parser_compile_group_output_override.add_argument("--override", action="store_true", help="Override existing output files without asking.")
    parser_compile_group_output_override.add_argument("--dont-override", action="store_true", help="Do not override any existing output files - Print to console instead.")
    parser_compile_group_output_override.add_argument("--ask", default="true", action="store_true", help="Ask if an existing file should be overwritten. (default)")
    parser_compile_group_output.add_argument("-a", "--all-in-one", action="store_true", help="Copy the content of the input file, remove references and copy the needed entites. The whole model in one file, no dependencies.")
    parser_compile_group_output.add_argument("--dont-create-dummies", action="store_true", help="Don't create dummies for unresolved dependencies.")

    args = parser.parse_args()

    if args.cmd == "info":
        cmd_info_handler(args)
    elif args.cmd == "compile":
        cmd_compile_handler(args)
else:
        print(parser.error("a subcommand is required."))
