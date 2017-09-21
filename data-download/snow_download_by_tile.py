'''
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

This script will facilitate downloading of snow products over WEBDAV.
'''

from datetime import datetime, timedelta
import fnmatch
from optparse import OptionParser
import os
import urllib2

# Snow server base webdav url
SNOW_DATA_URL = 'https://snow-data.jpl.nasa.gov'

# Used in webdav to tell what you are authenticating against
SNOW_REALM = 'DAV-upload'

# Types of product to download
TYPES = {'MODSCAG':{'url':'https://snow-data.jpl.nasa.gov/modscag-historic/{year}/{doy}/'},
         'MODDRFS':{'url':'https://snow-data.jpl.nasa.gov/moddrfs-historic/{year}/{doy}/'},
         'MODSCAG-NRT':{'url':'https://snow-data.jpl.nasa.gov/modscag/{year}/{doy}/'},
         'MODDRFS-NRT':{'url':'https://snow-data.jpl.nasa.gov/moddrfs/{year}/{doy}/'}
         }

def setup_cmdline_parser():
    '''Sets up the options available on the command line. Minimally the user
    should specify username, password, region (or tile_ids), and date range.
    Should also allow for type, output file, and mode (python, wget, or curl).

    >>> parser = setup_cmdline_parser()
    '''
    parser = OptionParser()
    parser.add_option('-u', '--user', action='store', type='string',
            dest='user', help='''REQUIRED - Username assigned to you by SnowDS team''')

    parser.add_option('-p', '--passwd', action='store', type='string',
            dest='passwd', help='''REQUIRED - Password assigned to you by SnowDS team,
            surrounded in single quotes''')

    parser.add_option('-T', '--tiles', action='store', type='string',
            default=None, dest='tiles', help='One or more MODIS tile_IDs to '
            'download.  Multiple tiles must be surrounded by quotes and comma separated. '
            'i.e. "h09v05,h10v05,h08v05".')

    parser.add_option('-t', '--types', action='store', type='string',
            default= None, dest='product_types', help='Product type to download '
            '(List of comma separated values). Choices include %s' % TYPES.keys())

    parser.add_option('-s', '--start', action='store', type='string', 
            default=None, dest='start', help='REQUIRED - Provide a start date in the format '
            'YYYYDDD, where DDD is a 3-digit Day Of Year')

    parser.add_option('-e', '--end', action='store', type='string', 
            default=None, dest='end', help='Provide an end date in the format '
            'YYYYDDD, where DDD is a 3-digit Day Of Year. '
            'NOTE: This date is NOT INCLUSIVE for downloading tiles.')

    parser.add_option('-f', '--file_patterns', action='store', type='string',
            default=None, help='OPTIONAL - Comma separated list of filename patterns to retrieve '
            'from the server.')

    return parser

def validate_cmdline(parser, options, args):
    '''Checks the command line options'''
    if not options.user:
        parser.error('Username required.\n\nFor a complete list of parameters and arguments use the -h flag or --help')
    if not options.passwd:
        parser.error('Password required.\n\nFor a complete list of parameters and arguments use the -h flag or --help')
    if not options.tiles:
        parser.error('Tile ID(s) required.\n\nFor a complete list of parameters and arguments use the -h flag or --help')
    if not options.start:
        parser.error('Start date is required.\n\nFor a complete list of parameters and arguments use the -h flag or --help')
    if not options.product_types:
        parser.error('Product Type(s) required.\n\nFor a complete list of parameters and arguments use the -h flag or --help')

def download_file(url):
    '''Will download and save the file using python urllib2. The file will be saved
    to the same name as it has on the server and with the same relative pathing.'''
    filepath = url[len(SNOW_DATA_URL) + 1:]
    try:
        data = urllib2.urlopen(url)
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(filepath):
            f = open(filepath, 'w')
            f.write(data.read())
            print('Downloaded: %s' % (filepath))
        else:
            print('Already existed: %s' % (os.path.basename(filepath)))
    except urllib2.HTTPError as ex:
        print('Failed Download: %s; (%s)' % (filepath, ex))
    except urllib2.URLError as ex:
        print('Invalid URL: %s; (%s)' % (url, ex))
    except IOError as ex:
        print('Cannot write: %s; (%s)' % (filepath, ex))

def setup_auth(user, passwd):
    '''Sets up the login for SnowDS WebDAV'''
    auth_handler = urllib2.HTTPDigestAuthHandler()
    auth_handler.add_password(realm=SNOW_REALM, uri=SNOW_DATA_URL, user=user, passwd=passwd)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

def daterange(start_date, end_date):
    '''Generates a set of year and doy from start_date up to but not including end_date'''
    for n in range((end_date - start_date).days):
        next_date = start_date + timedelta(n)
        year = next_date.strftime('%Y')
        doy = next_date.strftime('%j')
        yield year, doy

def parse_html_for_tile(html, base_url, tile):
    """
    Parses an html page response and a tile_id, and will return a list of
    complete URIs to be used to download the files

    Inputs::
        html <str> HTML returned from urllib2's response.read() method
        base_url <str> URL to resolve the relative URIs
        tile <str> MODIS tile_id to search through the HTML document for.

    Outputs::
        paths <list> All of the full URIs that match the given tile

    """
    paths = []
    for line in html:
        if tile in line:
            line_bits = line.split('"')
            for i, val in enumerate(line_bits):
                if val.startswith("MOD09GA"):
                    paths.append(os.path.join(base_url, line_bits[i]))

    return paths

def filter_urls(urls, patterns):
    ''' Return a list of urls that match the given pattern(s)

    Input::
        urls <list> Collection of urls to filter through
        patterns <list> Unix style filename patterns (not regex)

    Output::
        filtered_urls <list> URLs that match the given pattern(s)
    '''
    filtered_urls = []

    for pattern in patterns:
        good_urls = fnmatch.filter(urls, pattern)
        filtered_urls.extend(good_urls)

    return filtered_urls

def generate_filepaths(product_type, tiles, year, doy, filename_patterns=None):
    '''Create a set of filepaths that align with the given product type. This will pick up
    all the tiles, for the given year, and doy extensions specified.'''
    filepaths = []
    # Fetch the HTML for the Year/DOY in Question
    index_html_url = TYPES[product_type]['url'].format(year=year, doy=doy)
    try:
        req = urllib2.urlopen(index_html_url)
        html = req.readlines()
        req.close()
        for tile in tiles:
            filepath_list = parse_html_for_tile(html, index_html_url, tile)

            # If filename_patterns (check the filepath using the patterns)
            if filename_patterns:
                patterns = [p.strip() for p in filename_patterns.split(',')]
                filtered_urls = filter_urls(filepath_list, patterns)
                filepaths += filtered_urls

            else:
                filepaths += filepath_list

    except urllib2.HTTPError:
        msg = "Unable to locate URL: %s" % index_html_url
        print(msg)

    return filepaths

def fetch_doys(product_type, year):
    """ Return a list of valid DOY values for a given product type and year

    Input::
        product_type <str> Name of the product Type to search for, must be a key in TYPES
        year <int> 4 digit year to scan for DOY links

    Output::
        doys <list> Collection of valid DOYs to be searched further
    """
    base_url = TYPES[product_type]['url'].format(year=year, doy='')
    req = urllib2.urlopen(base_url)
    html = req.read()
    html_parser = AnchorTagParser()
    html_parser.feed(html)
    req.close()
    doys = html_parser.doys
    return doys



def main():
    # Handle command line
    parser = setup_cmdline_parser()
    (options, args) = parser.parse_args()
    validate_cmdline(parser, options, args)

    # Set defaults for parameters
    start_date = datetime.strptime(options.start, '%Y%j')
    end_date = datetime.strptime(options.end, '%Y%j') if options.end else datetime.today()
    product_types = options.product_types.split(',')
    tiles = options.tiles.split(',')

    # Setup login
    setup_auth(options.user, options.passwd)

    # Generate all the filepaths that will be downloaded by iterating over year, doy, and product types
    filepaths = []
    current_year = None
    for product_type in product_types:
        for year, doy in daterange(start_date, end_date):
            if current_year == year:
                pass
            else:
                current_year = year
                available_doys = fetch_doys(product_type, current_year)
            if doy in available_doys:
                filepaths += generate_filepaths(product_type, tiles, year, doy, options.file_patterns)
            else:
                bad_url = TYPES[product_type]['url'].format(year=year, doy=doy)
                print("Unable to download:: %s" % (bad_url,))

    for filepath in filepaths:
        download_file(filepath)


if __name__ == '__main__':
    main()

