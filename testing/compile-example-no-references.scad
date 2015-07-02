/**
 * This is an example to show the compile functionality of scadlib.
 *
 * Compiling a library for this file will create a single file that
 * resolves all the dependencies for this file.
 *
 * You need to specify a library where to look for resolutions, by setting
 * the --lib flag.
 *
 * The compiled library must then be included by hand also the old references
 * need to be removed.   
 * 
 * @filename compile-example-no-references.scad
 * @author: Hauke Thorenz <htho@thorenz.net>
 * @tag-list example, simple
 * @module-dependency: solarSystem It is defined in this file, but
 * it also is called in this file. So we need to add it as a dependency.
 */

//there are no references here!

/** We define the needed globalScale Variable */
globalScale = 1.5;

/**
 * The solar System.
 * @module-dependency: sunPlanet
 * @module-dependency: firstPlanet
 * @module-dependency: secondPlanet
 */
    
module solarSystem(){
  sunPlanet();
  firstPlanet();
  secondPlanet();
}

solarSystem();

