"""
MAP PROJECT
"""
import codecs
import random
import argparse
import sys
import time
import folium
from haversine import haversine
from cachetools import cached, TTLCache
from geopy.geocoders import Nominatim

cache = TTLCache(maxsize=100, ttl=86400)

parser = argparse.ArgumentParser()

# Necessary args
parser.add_argument("year", type=str)
parser.add_argument("coordinate_one", type=str)
parser.add_argument("coordinate_two", type=str)
parser.add_argument("path", type=str)

# Optional args
parser.add_argument('--processed_locations', type=int, default=70, required=False)
parser.add_argument('--markers', type=int, default=10, required=False)
parser.add_argument('--map_style', action="store_true")
parser.add_argument('--print_film', action="store_true")

args = parser.parse_args()


def main(year, coordinate_one, coordinate_two, path, locations_count=70, marker_count=10,
    map_style=False, print_film=False):
    """
    MAIN FUNCTION
    """
    start = time.time()
    print("The program started, please, wait.")

    locations = {}
    year = "(" + year + ")"
    your_location = (coordinate_one, coordinate_two)
    print("Your location is: " + str(your_location))

    # Open file with all film locations
    with codecs.open(path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            try:
                name, location = line.strip().split("\t")
            except ValueError:
                continue
            if year in name:
                pass
            else:
                continue
            if len(locations) <= locations_count:
                try:
                    coordinate = coordinate_finder(location)
                except:
                    try:
                        location_true = location.split(", ")[-2] +", " + location.split(", ")[-1]
                        coordinate = coordinate_finder(location_true)
                    except:
                        continue
                if coordinate not in locations:
                    locations[coordinate] = [name]
                else:
                    locations[coordinate].append(name)
            else:
                break
            if print_film:
                print(name)

    # Creating the folium map, base of the project
    if map_style:
        maper = folium.Map(tiles="Stamen Terrain",
                         location=your_location,
                         zoom_start=10)
    else:
        maper = folium.Map(location=your_location,
                           zoom_start=10)
    # Search for the lowest distances among the points
    distances = {}
    for elem in locations:
        if len(distances) < marker_count:
            distance = haversine(elem, your_location)
            distances[distance] = elem
        else:
            distance = haversine(elem,your_location)
            maximum = 0
            for coords in distances:
                if coords > maximum:
                    maximum = coords
            if distance < maximum:
                distances.pop(maximum)
                distances[distance] = elem

    # Sort the minimal distances
    min_dist_coordinates = []
    keys = list(distances.keys())
    for elem in sorted(keys):
        min_dist_coordinates.append(distances[elem])

    # Creating later with film locations
    film_locations = folium.FeatureGroup(name="Films locations")
    for coord in distances:
        for name in locations[distances[coord]]:
            name = name.replace("{#", "{")
            film_locations.add_child(folium.Marker(location=[(distances[coord][0] + \
            random.uniform(-0.001, 0.001)), (distances[coord][1] + random.uniform(-0.001, 0.001))],
                                        popup=name,
                                        fill_opacity = 0.5,
                                        icon=folium.Icon(color=random.choice(['darkpurple',\
'cadetblue', 'darkred', 'green', 'lightgray', 'darkgreen', 'pink', 'purple', 'beige', \
'lightgreen', 'red', 'darkblue', 'lightblue', 'gray', 'blue', 'white', 'orange', 'black', \
'lightred']))))

    # Creating the layer with line, which goes between all shooting places,
    # from nearest to the farthest.
    # Also, shows the distance between two connected points in popup
    line_through_films = folium.FeatureGroup(name="Line")
    min_dist_coordinates = [your_location] + min_dist_coordinates
    for elem_index in range(len(min_dist_coordinates) - 1):
        folium.PolyLine([min_dist_coordinates[elem_index], min_dist_coordinates[elem_index + 1]],\
        popup=str(haversine(min_dist_coordinates[elem_index], \
        min_dist_coordinates[elem_index + 1])) +" kilometres").add_to(line_through_films)

    # Creating layer with your location
    your_location_layer = folium.FeatureGroup(name="Your location")
    your_location_layer.add_child(folium.CircleMarker(location=your_location,
                                     radius=10,
                                     popup="Your location",
                                     fill_color=random.choice(['darkpurple',\
'cadetblue', 'darkred', 'green', 'lightgray', 'darkgreen', 'pink', 'purple', 'beige', \
'lightgreen', 'red', 'darkblue', 'lightblue', 'gray', 'blue', 'white', 'orange', 'black', \
'lightred']),
                                     color=random.choice(['darkpurple',\
'cadetblue', 'darkred', 'green', 'lightgray', 'darkgreen', 'pink', 'purple', 'beige', \
'lightgreen', 'red', 'darkblue', 'lightblue', 'gray', 'blue', 'white', 'orange', 'black', \
'lightred']),
                                     fill_opacity=0.5))

    # Adding all layers to the main map
    maper.add_child(line_through_films)
    maper.add_child(film_locations)
    maper.add_child(your_location_layer)
    maper.add_child(folium.LayerControl())
    maper.save("Map_project.html")
    end = time.time()
    print("Program was working for " + str(end-start) + " seconds")
    print("The program finished its work. Enjoy your map!")
    sys.exit()

@cached(cache)
def coordinate_finder(location):
    """
    Function, that finds coordinates of addresses.
    Is cached, so you don't have to contact with server for every address, that is using again
    >>> coordinate_finder('Ashland, New Hampshire, USA')
    (43.69568, -71.630859)
    >>> coordinate_finder('University of New Mexico, Albuquerque, New Mexico, USA')
    (35.08663275, -106.62020940505188)
    """
    geolocator = Nominatim(user_agent="my_application")
    locator = geolocator.geocode(location)
    return (locator.latitude, locator.longitude)

if __name__ == "__main__":
    main(args.year, float(args.coordinate_one), float(args.coordinate_two), args.path,\
         args.processed_locations, args.markers, args.map_style, args.print_film)
