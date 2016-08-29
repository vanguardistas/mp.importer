"""Utilities to import Locations from a CSV file.
The script contains a configuration table that enables storing different profiles (ex. different custom csvs). 
"""

import sys
import csv
import json
import urllib
import logging
import van_api

########################### auxiliary functions

def decode_row(row, encoding):
    if encoding == 'utf-8':
        decode_utf(row)
    elif encoding == 'latin-1':
        decode_latin(row)
    else:
        decode_fuzzy(row)

def decode_latin(row):
    new_row = []
    for c in row:
        try:
            c = c.decode('latin-1')
        except UnicodeDecodeError:
            logging.error('failed to decode {}'.format(repr(row)))			# latin-1 does not give errors!
            raise
        new_row.append(c)
    return new_row

def decode_utf(row):
    new_row = []
    for c in row:
        try:
            c = c.decode('utf-8')
        except UnicodeDecodeError:
            logging.error('failed to decode {}'.format(repr(row)))			
            raise
        if not c.strip():
            c = None
        new_row.append(c)
    return new_row

def decode_fuzzy(row):
    new_row = []
    for c in row:
        try:
            c = c.decode('utf-8')
        except UnicodeDecodeError:
            c = c.decode('latin1')
            raise
        if not c.strip():
            c = None
        new_row.append(c)
    return new_row
 

def encode_utf(row):
    new_row = []
    for c in row:
        if c:
            try:
                c = c.encode('utf-8')
            except UnicodeDecodeError:
                logging.error('failed to encode {}'.format(repr(row)))			
                raise
            if not c.strip():
                c = None
        new_row.append(c)
    return new_row



#### geo-stuff

def get_coords(address_key, urlname):
    """Get geocode for location using the google geocoding api"""		
    request = 'https://maps.googleapis.com/maps/api/geocode/json?address=' 
    request = request + address_key
    request = request + '&key='
    request = request + GOOGLE_API_KEY
    request = request.replace(' ','_')
    if '\n' in request:
        request = request.replace('\n','')
    response = urllib2.urlopen(request)
    data = json.load(response)['results']					
    try:
        lat = data[0]['geometry']['location']['lat']
    except:
        lat = None
    try:
        lon = data[0]['geometry']['location']['lng']			
    except:
        lon = None
    if lat and lon:
        coords = []				
        coords.append(lat)
        coords.append(lon)
    else:
        coords = None
    return coords        


def get_geoname(title, pcode, urlname, gcity):
    """Get geoname from geonames api"""
    geoname_url = 'http://api.geonames.org/searchJSON?q={}&postalcode={}&country=US&maxRows=10&username={}'.format(gcity, pcode, GEONAME_USER)
    geoname_2 = urllib.urlopen(geoname_url)
    data_2 = json.load(geoname_2)
    try:
        geo_id = data_2['geonames'][0]['geonameId']	
        if 'PP' not in data_2['geonames'][0]['fcode']:
            geo_id = data_2['geonames'][1]['geonameId']					
            if 'PP' not in data_2['geonames'][1]['fcode']:
                raise NotImplementedError		
    except:
        geo_id = None
    return geo_id







########################### api functions

### locations

def put_location(api,loc_dict,loc_uuid,INSTANCE_ID):
    """chek if item exists, then update/insert accordingly
    """
    _EXISTING_LOCS = api.GET('/%s/locations?fields=uuid-urlname&rpp=100' % INSTANCE_ID)
    there = 0
    while 'next' in _EXISTING_LOCS:
        _EXISTING_LOCS = api.GET('/%s/locations?%s' %(INSTANCE_ID, _EXISTING_LOCS['next']))
        for item in _EXISTING_LOCS['items']:
            if item[1] == loc_dict['urlname']:  # match by urlname (they'll insert a csv with unique urlname)													
                there = 1
    if there:
        update_location(api, loc_dict, loc_uuid, item)
    else:
        insert_location(api, loc_dict, loc_uuid)


def insert_location(api, loc_dict, loc_uuid, INSTANCE_ID):
    """put item into database
    """
    status = 0
    if there == 0:
        result = api.PUT('/%s/locations/%s' % (INSTANCE_ID, loc_uuid), loc_dict)
        check = api.GET('/%s/locations/%s' % (INSTANCE_ID, loc_uuid))
        if check is not None:						
            status = 1
    else:
        status = update_location(api, loc_dict, loc_uuid, item)   
    return status



def update_location(api, loc_dict, loc_uuid, existing_loc, INSTANCE_ID):
    """update item in database
    """
    status = 0
    loc_dict_toupdate = loc_dict - existing_loc  
    print 'loc_dict_toupdate', loc_dict_toupdate
    result = api.PATCH('/%s/locations/%s' % (INSTANCE_ID, loc_uuid), loc_dict_toupdate)
    check = api.GET('/%s/locations/%s' % (INSTANCE_ID, loc_uuid)) 
    if check is not None: # TODO should check a field!
        status = 1
    return status


### locations tags and categories - TODO fix

def add_tags(api, categories, loc_uuid):
    """ Creates categories if not there
        Adds tag to category, then tags the location
    """
    # create a dict of tags and categories to be passed here! tagcat_dict
    for category in categories['categories']:
        cat_uuid = uuid.uuid3(namespace, 'cat_region')
        created, cat_uuid = create_cat(api, category, cat_uuid) 	 
        tag = tagcat_dict.get(category) # TODO get from dict
        tag_uuid = uuid.uuid3(namespace, tag) 
        created, tag_uuid = create_tag(api, tag, tag_uuid, cat_uuid) 		
        if created == 1:
            tag = put_tag(api, tag_uuid, loc_uuid)
    #
    # create tags without category? they should have '' in the cat field
    tag = 'Top Wedding Vendor 2016'
    namespace = uuid.NAMESPACE_URL
    tag_uuid = uuid.uuid3(namespace, tag) 
    created, tag_uuid = create_tag(api, tag, tag_uuid, None)
    if created == 1:
        tag = put_tag(api, tag_uuid, loc_uuid)			


_CREATED_CATS_NOW = {}

def create_cat(api, cat, cat_uuid):
    _EXISTING_CATS = api.GET('/%s/tags/categories?fields=uuid-title&rpp=100' %INSTANCE_ID)				
    there = 0
    status = 0
    if not 'next' in _EXISTING_CATS:
        for item in _EXISTING_CATS['items']:
            if item[1] == suggest_urlname(cat):  												
                there = 1
                cat_uuid = item[0]																
    else:
        while 'next' in _EXISTING_CATS:																
            _EXISTING_CATS = api.GET('/%s/tags/categories?%s' %(INSTANCE_ID, _EXISTING_CATS['next']))		
            for item in _EXISTING_CATS['items']:
                if item[1] == suggest_urlname(cat):  												
                    there = 1
                    cat_uuid = item[0]																
    if cat in _CREATED_CATS_NOW:
        cat_uuid = _CREATED_CATS_NOW.get(cat)				# TODO update cat?
    elif there == 0:																																					
        cat_creation_dict = {}
        cat_creation_dict['title'] = str(cat)
        cat_creation = api.PUT("/%s/tags/categories/%s" % (INSTANCE_ID, cat_uuid), cat_creation_dict) 
        check = api.GET('/%s/tags/categories/%s' % (INSTANCE_ID, cat_uuid))    							
        if check is not None:						
           status = 1
        _CREATED_CATS_NOW[cat] = cat_uuid     
    return status, cat_uuid


_CREATED_TAGS_NOW = {}

def create_tag(api, tag, tag_uuid, cat_uuid=None):
    """ create the tag if not in the destination db
    """
    _EXISTING_TAGS = api.GET('/%s/tags?fields=uuid-urlname&rpp=100' %INSTANCE_ID)				
    there = 0
    status = 0
    if not 'next' in _EXISTING_TAGS:
        for item in _EXISTING_TAGS['items']:
            if item[1] == suggest_urlname(tag):  												
                there = 1
                tag_uuid = item[0]
                status = 1															
    else:
        while 'next' in _EXISTING_TAGS:																
            _EXISTING_TAGS = api.GET('/%s/tags?%s' %(INSTANCE_ID, _EXISTING_TAGS['next']))
            for item in _EXISTING_TAGS['items']:
                if item[1] == suggest_urlname(tag):  												
                    there = 1
                    tag_uuid = item[0]																
                    status = 1
    if tag in _CREATED_TAGS_NOW:
        tag_uuid = _CREATED_TAGS_NOW.get(tag) # TODO update tag?
    elif there == 0:	
        tag_creation_dict = {}
        tag_creation_dict['urlname'] = suggest_urlname(tag)
        tag_creation_dict['title'] = str(tag)
        tag_creation_dict['category'] = "Subject"
        tag_creation_dict['created'] = str(datetime.datetime.now())	
        tag_creation_dict['modified'] = str(datetime.datetime.now())
        tag_creation = api.PUT("/%s/tags/%s" % (INSTANCE_ID, tag_uuid), tag_creation_dict) 
        check = api.GET('/%s/tags/%s' % (INSTANCE_ID, tag_uuid))      							
        if check is not None:	
           status = 1
        _CREATED_TAGS_NOW[tag] = tag_uuid
        if cat_uuid is not None:
            tag_cat_dict = {}
            tag_cat_dict['tag_uuid'] = str(tag_uuid)
            tagcat_creation = api.POST("/%s/tags/categories/%s/tags" % (INSTANCE_ID, cat_uuid), tag_cat_dict) 
    return status, tag_uuid



def put_tag(api, tag_uuid, loc_uuid):   														
    """ Tag the location
    """
    tag_dict = {}
    tag_dict['created'] = str(datetime.datetime.now())	
    result = api.PUT('/%s/tags/%s/describes/%s' % (INSTANCE_ID, tag_uuid, loc_uuid), tag_dict)
    check = api.GET('/%s/tags/%s/describes/%s' % (INSTANCE_ID, tag_uuid, loc_uuid))      							
    if result is not None:						
        status = 1
    return status
    



