/**
 * This is an example to show the different comments and the functionality
 * of scadlib.py
 *
 * Structured information is given as "tags"  That's an @ character
 * at the beginning of a line followed by the name of the tag. The
 * information belonging to that tag is given after a whitespace or a
 * colon (Colons look better). Any text until the next
 * tag or the end of the comment belongs to that tag.
 *
 * In fact this text is stored under the @description tag, but you don't
 * need to care abut that.
 * 
 * The @filename -tag is mandatory. A comment with a filename-tag that
 * matches the file name is the comment that describes the file.
 *
 * The -dependency tags are needed in order to resolve dependencies.
 *
 * ALL other fields are optional, but useful.
 * 
 * @filename information-extraction-example.scad
 * @author: Hauke Thorenz <htho@thorenz.net>
 * @tag-list example, simple
 * @module-dependency: solarSystem It is defined in this file, but
 * it also is called in this file. So we need to add it as a dependency.
 */

include <../lib/testlib/planets.scad>
use <../lib/testlib/tools.scad>

/** We define the needed globalScale Variable */
globalScale = 1.5;

/**
 * The solar System.
 * @module-dependency: sunPlanet
 * @module-dependency: firstPlanet
 * @module-dependency: secondPlanet
 */
    
module solarSystem(){
  //Only whitespace is allowed between a comment and the entity to comment.
  //The whitespace between comment and this module will be visible with
  //--as-dump, but not with --as-scad.
  sunPlanet();
  firstPlanet();
  secondPlanet();
}

solarSystem();

