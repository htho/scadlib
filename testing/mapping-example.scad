/**
 * This is an example to show the mapping
 * functions.
 *
 * Okay this one also defines a solar system, but there might be multiple
 * modules providing models for the sun and other planets.
 *
 * Instead of writing wrapper modules, or searching and replacing the
 * module calls for bigPlanet, with sunPlanet, the map functionality
 * will create the wrapper modules.
 * 
 * @filename: mapping-example.scad
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
 * @module-dependency: alienPlanet A parametric planet with a signature
 * that differs from the signature that the implementation uses. 
 *
 * @function-dependency: rfunc Calculate radius from diameter.
 */
module solarSystem(){
  bigPlanet();
  firstPlanet();
  smallPlanet();
  dia=20;
  dist=40;
  alienPlanet(dia=dia, dist=dist); //notice that the parameters are switched and renamed. 
  rfunc(10);
}

solarSystem();

