"""Utilities to import Locations from a CSV file.
The script contains a configuration table that enables storing different profiles (ex. different custom csvs). 
"""

import sys
import csv
import json
import urllib.request
import logging
import van_api

########## encode/decode

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
            logging.error('failed to decode {}'.format(repr(row)))			
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



############ geonames and coordinates


def get_coords(address_key, GOOGLE_API_KEY, urlname):
    """Get geocode for location using the google geocoding api"""		
    request = 'https://maps.googleapis.com/maps/api/geocode/json?address=' 
    request = request + address_key
    request = request + '&key='
    request = request + GOOGLE_API_KEY
    request = request.replace(' ','_')
    if '\n' in request:
        request = request.replace('\n','')
    response = urllib.request.urlopen(request)
    str_response = response.readall().decode('utf-8')
    data = json.loads(str_response)['results']
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


def get_geoname(GEONAME_USER, pcode, gcity):
    """Get geoname from geonames api"""
    geoname_url = 'http://api.geonames.org/searchJSON?q={}&postalcode={}&country=US&maxRows=10&username={}'.format(gcity, pcode, GEONAME_USER)
    geoname = urllib.request.urlopen(geoname_url)
    str_geoname = geoname.readall().decode('utf-8')
    data = json.loads(str_geoname)
    try:
        geo_id = data['geonames'][0]['geonameId']	
        if 'PP' not in data['geonames'][0]['fcode']:		# PP = Populated Places to avoid naming conflict with other administrative units
            geo_id = data['geonames'][1]['geonameId']					
            if 'PP' not in data['geonames'][1]['fcode']:
                raise NotImplementedError		
    except:
        geo_id = None
    return geo_id




########### api functions


class LocationUpdater:
    def __init__(self, api, instance_id):
        self.api = api
        self.instance_id = instance_id


    def check_existing_location(self, urlname):
        """ Get all locations and check if urlname is already there
        """
        EXISTING_LOCS = self.api.GET('/%s/locations?fields=uuid-urlname&rpp=100' % self.instance_id)
        there = False
        while 'next' in EXISTING_LOCS:
            EXISTING_LOCS = self.api.GET('/%s/locations?%s' %(self.instance_id, EXISTING_LOCS['next']))
            for item in EXISTING_LOCS['items']:
                if item[1] == urlname:  													
                    there = True
        return there


    def upsert_location(self, loc_dict, loc_uuid):					
        """chek if item exists, then update/insert accordingly
        """    
        EXISTING_LOCS = self.api.GET('/%s/locations?fields=uuid-urlname&rpp=100' % self.instance_id)
        there = False
        while 'next' in EXISTING_LOCS:
            EXISTING_LOCS = self.api.GET('/%s/locations?%s' %(self.instance_id, EXISTING_LOCS['next']))
            for item in EXISTING_LOCS['items']:
                if item[0] == loc_dict['uuid']:  												
                    there = True
        if there is True:
            self.update_location(self.api, loc_dict, loc_uuid, item)
        else:    
            self.insert_location(self.api, loc_dict, loc_uuid)


    def insert_location(self, api, loc_dict, loc_uuid):
        """put item into database       
        """
        status = 0
        result = self.api.PUT('/%s/locations/%s' % (self.instance_id, loc_uuid), loc_dict)
        check = self.api.GET('/%s/locations/%s' % (self.instance_id, loc_uuid))
        if check is not None:						
            status = 1
        return status


    def update_location(self, api, loc_dict, loc_uuid, item):
        """update item in database
           the script must pass the correct fields (only those that need updating, or all admitted fields?)  
           https://api.metropublisher.com/resources/location.html#resource-patch-location-patch
        """
        # TODO I can PATCH only fields that have changed, or PUT all fields - if PATCH, modify loc_dict, use "item" to see what's there
        # maybe for big imports is better to save that time?
        status = 0
        result = self.api.PUT('/%s/locations/%s' % (self.instance_id, loc_uuid), loc_dict)
        #result = self.api.PATCH('/%s/locations/%s' % (self.instance_id, loc_uuid), loc_dict) 
        check = self.api.GET('/%s/locations/%s' % (self.instance_id, loc_uuid)) 
        if check is not None: # TODO check a field to make sure has been updated, ex. modification date!
            status = 1
        return status





#### tags/categories

# TODO add to context in the main script? they keep track of the items created during the run
CREATED_CATS = {}			
CREATED_TAGS = {}	

class TagUpdater:
    def __init__(self, api, instance_id):
        self.api = api
        self.instance_id = instance_id

    def upsert_tags(self, tagcat_dictionary, loc_uuid):   
        """ Creates categories if not there
            input is a dictionary of type {tag1:cat1,tag2:None,tag3:cat1,cat2} # tag can be in multiple categories, or can have no category
            Adds tag to category, then tags the location
        """
        for tag in tagcat_dictionary:
            category = tagcat_dictionary.get(tag)
            if category is not None:
               cat_uuid = uuid.uuid3(namespace, category)
               create_cat(self.api, cat, cat_uuid, self.instance_id)
            else:
               cat_uuid = None
            tag_uuid = uuid.uuid3(namespace, tag) 
            created, tag_uuid = create_tag(self.api, tag, tag_uuid, cat_uuid, self.instance_id) 		
            if created == 1:
                tag = put_tag(self.api, tag_uuid, loc_uuid, self.instance_id)			


    def create_cat(self, cat, cat_uuid):
        EXISTING_CATS = self.api.GET('/%s/tags/categories?fields=uuid-title&rpp=100' %self.instance_id)				
        there = 0
        status = 0
        if not 'next' in EXISTING_CATS:
            for item in EXISTING_CATS['items']:
                if item[1] == suggest_urlname(cat):  												
                    there = 1
                    cat_uuid = item[0]	
                else:
                    status = 0
                    there = 0				    											
															
        else:
            while 'next' in EXISTING_CATS:																
                EXISTING_CATS = self.api.GET('/%s/tags/categories?%s' %(INSTANCE_ID, EXISTING_CATS['next']))		
                for item in EXISTING_CATS['items']:
                    if item[1] == suggest_urlname(cat):  												
                        there = 1
                        cat_uuid = item[0]																
                    else:
                        status = 0
                        there = 0				    											
        if cat in CREATED_CATS: # created during this run, no need to update it
            cat_uuid = CREATED_CATS.get(cat)				
            there = 1
            status = 1
        # elif ***** 		TODO  what if we want to update cat? 
        elif there == 0:																																					
            cat_creation_dict = {}
            cat_creation_dict['title'] = str(cat)
            cat_creation = self.api.PUT("/%s/tags/categories/%s" % (self.instance_id, cat_uuid), cat_creation_dict) 
            check = self.api.GET('/%s/tags/categories/%s' % (self.instance_id, cat_uuid))    							
            if check is not None:						
               status = 1
            CREATED_CATS[cat] = cat_uuid     
        return status, cat_uuid


    def create_tag(self, tag, tag_uuid, cat_uuid=None):
        """ create the tag if not in the destination db
        """
        EXISTING_TAGS = self.api.GET('/%s/tags?fields=uuid-urlname&rpp=100' %self.instance_id)				
        there = 0
        status = 0
        if not 'next' in EXISTING_TAGS:
            for item in EXISTING_TAGS['items']:
                if item[1] == suggest_urlname(tag):  												
                    there = 1
                    tag_uuid = item[0]    
                    status = 1
                else:
                    status = 0
                    there = 0				    											
        else:
            while 'next' in EXISTING_TAGS:																
                EXISTING_TAGS = self.api.GET('/%s/tags?%s' %(self.instance_id, EXISTING_TAGS['next']))
                for item in EXISTING_TAGS['items']:
                    if item[1] == suggest_urlname(tag):  												
                        there = 1
                        status = 1
                    else:
                        status = 0
                        there = 0				    											
        if tag in CREATED_TAGS: # just created during this run, no need to update
            tag_uuid = CREATED_TAGS.get(tag) 
            status = 1
            there = 1
        # elif ***** 		TODO  what if we want to update tag?
        elif there == 0:	
            tag_creation_dict = {}
            tag_creation_dict['urlname'] = suggest_urlname(tag)
            tag_creation_dict['title'] = str(tag)
            tag_creation_dict['category'] = "Subject"
            tag_creation_dict['created'] = str(datetime.datetime.now())	
            tag_creation_dict['modified'] = str(datetime.datetime.now())
            tag_creation = self.api.PUT("/%s/tags/%s" % (self.instance_id, tag_uuid), tag_creation_dict) 
            check = self.api.GET('/%s/tags/%s' % (self.instance_id, tag_uuid))      							
            if check is not None:	
               status = 1
            CREATED_TAGS[tag] = tag_uuid
            if cat_uuid is not None:
                tag_cat_dict = {}
                tag_cat_dict['tag_uuid'] = str(tag_uuid)
                tagcat_creation = self.api.POST("/%s/tags/categories/%s/tags" % (self.instance_id, cat_uuid), tag_cat_dict) 
        return status, tag_uuid


    def put_tag(self, tag_uuid, loc_uuid):   														
        """ Tag the location
        """
        tag_dict = {}
        tag_dict['created'] = str(datetime.datetime.now())	
        result = self.api.PUT('/%s/tags/%s/describes/%s' % (self.instance_id, tag_uuid, loc_uuid), tag_dict)
        check = self.api.GET('/%s/tags/%s/describes/%s' % (self.instance_id, tag_uuid, loc_uuid))      							
        if result is not None:						
            status = 1
        return status
    



