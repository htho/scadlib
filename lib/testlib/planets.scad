/** This file defines all the entities needed to create a solar system.
 *
 * @filename planets.scad
 */


/**
 * The scale of this solarSystem.
 */
globalScale = 10;

/**
 * A generic planet.
 *
 * @param distance The distance from the center.
 * @param diameter The diameter of the planet.
 * @show a Planet.
 * @function-dependency r_from_dia Calculate radius from diameter.
 */
module genericPlanet(distance, diameter){
  translate([distance,0,0]) sphere(r=r_from_dia(diameter));
}

/**
 * A generic scaled planet.
 * This planet already is scaled according to global Scale.
 *
 * @param distance The distance from the center.
 * @param diameter The diameter of the planet.
 * @show a Planet.
 * @module-dependency genericPlanet A generic planet.
 */
module genericScaledPlanet(distance, diameter){
  genericPlanet(distance*globalScale, diameter*globalScale);
}

/**
 * Calculates the radius from the given diameter.
 *
 * @param dia a diameter.
 * @return the radius.
 *
 */
function r_from_dia(dia) = dia / 2;

/**
 *  The Sun.
 * @module-dependency: genericPlanet
 * @variable-dependency: globalScale
 */
module sunPlanet(){
  diameter = 200*globalScale;
  genericPlanet(0,diameter);
  }

/**
 *  The first Planet.
 * @module-dependency: genericPlanet
 * @variable-dependency: globalScale
 */
module firstPlanet(){
  diameter = 20*globalScale;
  distanceFromSun = 500*globalScale;
  genericPlanet(distanceFromSun,(diameter));
  }

/**
 *  The second Planet.
 * @module-dependency: genericPlanet
 * @variable-dependency: globalScale
 */
module secondPlanet(){
  diameter = 80*globalScale;
  distanceFromSun = 800*globalScale;
  genericPlanet(distanceFromSun,(diameter));
  }
