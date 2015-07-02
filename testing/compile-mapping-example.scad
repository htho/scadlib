/**
 * This is an example to show the compile and mapping
 * functions.
 *
 * Okay this one also defines a solar system, but there might be multiple
 * modules providing models for the sun and other planets.
 *
 * Instead of writing wrapper modules, or searching and replacing the
 * module calls for bigPlanet, with sunPlanet, the compile functionality
 * will create the wrapper modules.
 * 
 * @filename: compile-mapping-example.scad
 * @module-dependency: solarSystem A solar system.
 */


/**
 * The solar System.
 * Note that the modules bigPlanet and smallPlanet do not exist in the
 * library.
 * @module-dependency: bigPlanet The Sun (will be mapped to sunPlanet)
 * @module-dependency: firstPlanet The first Planet
 * @module-dependency: smallPlanet The second Planet (will be mapped to
 * secondPlanet).
 *
 * @function-dependency: rfunc Calculate radius from diameter.
 */
module solarSystem(){
  bigPlanet();
  firstPlanet();
  smallPlanet();
  rfunc(10);
}

solarSystem();

