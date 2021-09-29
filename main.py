'''
Module creates an HTML map that shows the nearest film locations to the user's locatiion
'''

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderUnavailable
import folium

def read_data():
    '''
    Reads locations file
    :return:
    '''
    my_lines = open('locations.txt', mode='r', encoding='utf-8').readlines()
    films = [line.strip().split('\t') for line in lines[14:]]
    return films


def get_user_location():
    '''
    Gets user's coordinates
    :return:
    '''
    loc = input('Please enter your location (format: lat, long): ')
    return loc


def get_user_country(coordinates):
    '''
    Determines the country the user is in
    :param coordinates:
    :return:
    '''
    try:
        geolocator = Nominatim(user_agent='Film_map')
        country = geolocator.reverse(coordinates, language='en')
        return str(country).split(', ')[-1]
    except GeocoderUnavailable:
        pass


def get_year():
    '''
    Gets desired year from user
    :return:
    '''
    year = input('Please enter a year you would like to have a map for: ')
    return year


def format_data(films, year):
    '''
    Formats location data
    :param films:
    :param year:
    :return:
    '''
    dataformat = []
    for fil in films:
        op_br_idx = fil[0].index('(')
        cl_br_idx = fil[0].index(')')
        new_str = [fil[0][cl_br_idx+2:], fil[0][op_br_idx+1:cl_br_idx], fil[0][:op_br_idx-1]]
        del fil[0]
        for i in new_str:
            fil.insert(0, i)
        fil[:] = (val for val in fil if val != '')
        new = [fil[0], fil[1]]
        if '(' not in fil[-1]:
            new.append(fil[-1])
        else:
            new.append(fil[-2])
        place_split = new[-1].split(', ')
        if len(place_split) > 3:
            place_split = place_split[-3:]
            new[-1] = ', '.join(place_split)
        dataformat.append(new)
    year_sorted = [film for film in dataformat if film[1] == year]
    return year_sorted


def coordinates_conversion(place):
    '''
    Converts location into coordinates
    :param place:
    :return:
    '''
    try:
        geolocator = Nominatim(user_agent='Film_map')
        coordinates = geolocator.geocode(place)
        return (coordinates.latitude, coordinates.longitude)
    except GeocoderUnavailable:
        pass


def distance(films, location):
    '''
    Calculates distance between film location and user
    :param films:
    :param location:
    :return:
    '''
    for film in films:
        try:
            try:
                coordinates = coordinates_conversion(film[-1])
                film.append(coordinates)
            except AttributeError:
                film.append('TTT')
        except GeocoderUnavailable:
            continue

    available_locs = [_ for _ in films if _[-1] != 'TTT']
    for film in available_locs:
        dist = geodesic(location, film[-1])
        film.append(dist)

    available_locs.sort(key=lambda x: x[-1], reverse=True)
    ten = films[:10]
    return ten


def create_map(user_year, user_loc):
    '''
    Creates map and places icons
    :param user_year:
    :param user_loc:
    :return:
    '''
    found_places = distance(format_data(read_data(), user_year), user_loc)
    location = [num for num in user_loc.split(', ')]
    film_map = folium.Map(location=location, zoom_start=5)
    film_map.add_child(folium.Marker(location=location, popup="You're here!",
                                     icon=folium.Icon(color="blue", icon='home')))
    points = folium.FeatureGroup(name="Closest film locations")
    country = get_user_country(user_loc)
    same_country = folium.FeatureGroup(name="Film locations in the same country")
    for place in found_places:
        try:
            if place[-3].split(', ')[-1] == country:
                same_country.add_child(folium.Marker(location=list(place[-2]),
                                           popup=place[0], icon=folium.Icon(color="darkpurple")))
            else:
                points.add_child(folium.Marker(location=list(place[-2]),
                                               popup=place[0], icon=folium.Icon(color="green")))
        except ValueError:
            continue

    film_map.add_child(points)
    film_map.add_child(same_country)
    film_map.add_child(folium.LayerControl())
    file_name = f'{found_places[0][1]}_movies_map.html'
    print(f'Finished. Please have look at the map {file_name}')
    return film_map.save(file_name)


def generate_map():
    '''
    Accepts user input and generates map
    :return:
    '''
    year = get_year()
    location = get_user_location()
    print('Map is generating...\nPlease wait...')
    create_map(year, location)
    return

generate_map()










