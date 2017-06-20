import sys
import csv
import ast
import numpy as np
# geopy for finding distance between
# (lat,long) points
from geopy.distance import vincenty


def get_closest_library(lat, lon, libs):

    # Get distances to each library from input
    libs_with_distance = get_distances_from(lat, lon, libs)

    closest_lib = min(libs_with_distance,
                      key=lambda x: libs_with_distance[x]['distance'])

    return libs[closest_lib]


def get_libraries():
    libraries = {}

    f = open('library_info.csv', 'rb')
    reader = csv.reader(f)

    next(reader, None)  # skip header row

    for row in reader:
        libraries[row[0]] = {'name': row[0], 'hours': row[1],
                             'cybernavigator': row[2],
                             'has_teacher': row[3], 'address': row[4],
                             'city': row[5], 'state': row[6], 'zip': row[7],
                             'phone': row[8], 'website': row[9],
                             'location': row[10]}

    f.close()

    return libraries


def get_library_popularity(lib, libs):
    """
    The popularity of a library is based on the
    number of other libraries in it's zip code.
    The less crowded a zip code is, the more
    popular libraries in that zip code will be.

    Note that there may be cases that even if
    there are only a few libraries within the
    zip code, there may be others very close
    in neighboring zip codes.

    1 = most popular; 4 = least popular

    """
    zips = {}
    for k in libs:
        if libs[k]['zip'] not in zips.keys():
            zips[libs[k]['zip']] = 1
        else:
            zips[libs[k]['zip']] += 1

    zip_counts = [i[1] for i in zips.iteritems()]

    nearest_lib_zip_count = zips[lib['zip']]

    percentile0 = np.percentile(zip_counts, 0)
    percentile25 = np.percentile(zip_counts, 25)
    percentile50 = np.percentile(zip_counts, 50)
    percentile75 = np.percentile(zip_counts, 75)
    percentile100 = np.percentile(zip_counts, 100)

    if (nearest_lib_zip_count >= percentile0 and
        nearest_lib_zip_count < percentile25):
        return 1
    elif (nearest_lib_zip_count >= percentile25 and
    	nearest_lib_zip_count < percentile50):
        return 2
    elif (nearest_lib_zip_count >= percentile50 and
    	nearest_lib_zip_count < percentile75):
        return 3
    elif (nearest_lib_zip_count >= percentile75 and
    	nearest_lib_zip_count <= percentile100):
        return 4


def get_distances_from(lat, lon, libraries):
    p1 = (lat, lon)
    for k in libraries:
        this_lib_location = ast.literal_eval(libraries[k]['location'])
        if len(this_lib_location) == 2:
            libraries[k]['distance'] = vincenty(p1, this_lib_location).miles
    return libraries

if __name__ == "__main__":

    if len(sys.argv) != 3:
        exit("usage: {} <latitude>, <longitude>".format(sys.argv[0]))

    lat = sys.argv[1].replace(',', '')
    lon = sys.argv[2]
    libs = get_libraries()

    nearest_lib = get_closest_library(lat, lon, libs)
    popularity = get_library_popularity(nearest_lib, libs)

    print "{} {}\t{}".format(nearest_lib['name'], nearest_lib['address'], popularity)
