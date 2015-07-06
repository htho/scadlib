/**
 * This is an example to show the compile functionality of scadlib.
 *
 * The include and use statements in this file already resolve the
 * dependencies for this file. Compiling a library for this file will
 * create a single file that resolves all the dependencies for this file.
 *
 * The compiled library must then be included by hand also the old references
 * need to be removed.   
 * 
 * @filename build-example.scad
 * @author: Hauke Thorenz <htho@thorenz.net>
 * @tag-list example, simple
 * @module-dependency: solarSystem It is defined in this file, but
 * it also is called in this file. So we need to add it as a dependency.
 */


/**
 * The solar System.
 * @module-dependency: sunPlanet
 * @module-dependency: firstPlanet
 * @module-dependency: secondPlanet
 * @module-dependency: unresolvedPlanet There is no module that resolves
 * this dependency, so a dummy module will be created.
 */
    
module solarSystem(){
  sunPlanet();
  firstPlanet();
  secondPlanet();
  unresolvedPlanet();
}

solarSystem();

