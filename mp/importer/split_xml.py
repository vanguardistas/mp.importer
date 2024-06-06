""" Split a XML File into smaller files

The smaller files should only include the authors and attachments that are actually used in the file.
You can specify the destination folder. It will be created if it doesn't exist. You can also specify
the number of items you want to have in each batch.

It requires the lxml module to be installed. (https://lxml.de/)


usage: python split_xml.py [-h] [-c CHUNK_SIZE] [-r RESULTS_FOLDER] filename

positional arguments:
  filename              Filename of the xml file to split

options:
  -h, --help            show this help message and exit
  -c CHUNK_SIZE, --chunk_size CHUNK_SIZE
                        Number of items to put in a file. (default: 100)
  -r RESULTS_FOLDER, --results_folder RESULTS_FOLDER
                        Name of the folder to put the files in. Will be created if it doesn't exist. (default: results)


"""

import os
import re
from lxml import etree
import argparse
import datetime

parser = argparse.ArgumentParser(description='Split wordpress export xml into chunks')
parser.add_argument('filename', help='Filename of the xml file to split')
parser.add_argument('-c', '--chunk_size', help='Number of items to put in a file. (default: 100)', type=int, default=100)
parser.add_argument('-r', '--results_folder', help='Name of the folder to put the files in. Will be created if it doesn\'t exist. (default: results)', default='results')

args = parser.parse_args()
filename = args.filename
chunk_size = args.chunk_size
results_folder = args.results_folder
if not os.path.exists(results_folder):
   os.makedirs(results_folder)

parser = etree.XMLParser(strip_cdata=False)
tree = etree.parse(filename, parser=parser)

docinfo = tree.docinfo
encoding = docinfo.encoding or 'utf-8'

root = tree.getroot()
ns_dict = {k:v for k,v in root.nsmap.items() if k}

#channel info
channel_title = tree.find('channel/title', namespaces=ns_dict)
channel_link = tree.find('channel/link', namespaces=ns_dict)
channel_desc = tree.find('channel/description', namespaces=ns_dict)
channel_pub_date = tree.find('channel/pubDate', namespaces=ns_dict)
channel_language = tree.find('channel/language', namespaces=ns_dict)
channel_base_site_url = tree.find('channel/wp:base_site_url', namespaces=ns_dict)
channel_base_blog_url = tree.find('channel/wp:base_blog_url', namespaces=ns_dict)

oldest_post_date = datetime.datetime.now()

items = tree.findall('.//item')

# attachments that are used but don't exist
failed_post_ids = []

# get all authors and put them in a dict
author_dict = {}
authors_tags = tree.findall('.//wp:author', namespaces=ns_dict)
for a in authors_tags:
    author_dict[a.find('wp:author_login', namespaces=ns_dict).text] = a


# split items in attachments and posts
attachment_dict = {}
attachment_url_to_post = {}
post_list = []

for i in items:
    item_type = i.find('wp:post_type', namespaces=ns_dict).text
    if item_type == 'attachment':
        post_id = i.find('wp:post_id', namespaces=ns_dict).text
        attachment_url = i.find('wp:attachment_url', namespaces=ns_dict).text
        attachment_dict[post_id] = i
        attachment_url_to_post[attachment_url] = post_id
    elif item_type in ['article', 'post', 'news']:
        post_list.append(i)

# get a list of authors for an item
def get_item_authors(item):
    authors = []
    item_authors = item.findall('dc:creator', namespaces=ns_dict)
    for ia in item_authors:
        authors.append(author_dict.get(ia.text))
    return authors

# get a list of attachments for an item
def get_item_attachments(item):
    attachments= []
    img_list = []
    nodecontent = item.find('content:encoded', namespaces=ns_dict).text
    content = etree.HTML(u'<html><body>{}</body></html>'.format(nodecontent))
    content = content.find('body')
    content.tag = 'div'
    for node in content.findall('.//img'):
        if node.tag == 'img' and 'src' in node.attrib:
            url = node.attrib['src']
            img_list.append(url)
            # check if the url exists as wp:attachment_url
            post_id = attachment_url_to_post.get(url)
            if post_id:
                attachment = attachment_dict.get(post_id)
                if attachment is not None:
                    attachments.append(attachment_dict.get(post_id))
                    continue
                else:
                    failed_post_ids.append(post_id)
                    # print ('FAILED IMAGE IN ATTACHMENT', post_id)
            else:
                # check if an attachment is linked in the css class
                img_classes = node.attrib.get('class', '')
                post_id = re.findall('wp-image-[\d]{1,9}', img_classes)
                if post_id:
                    post_id = post_id[0].replace('wp-image-', '')
                    if post_id:
                        attachment = attachment_dict.get(post_id)
                        if attachment is not None:
                            attachments.append(attachment_dict.get(post_id))
                            continue
                        else:
                            failed_post_ids.append(post_id)
                            # print ('FAILED IMAGE IN CSS CLASS', post_id)
            has_dimensions = re.search('[\d]{3,5}x[\d]{3,5}[.]', url)       # image has a dimension in its filename, i.e. 300x250
            if has_dimensions:
                cleaned = re.sub('[-][\d]{3,5}x[\d]{3,5}[.]','.', url)
                post_id = attachment_url_to_post.get(cleaned)
                if post_id:
                    attachment = attachment_dict.get(post_id)
                    if attachment is not None:
                        attachments.append(attachment_dict.get(post_id))
                        continue
                    else:
                        failed_post_ids.append(post_id)
                        # print ('FAILED IMAGE IN ATTACHMENT WITH DIMENSIONS', post_id)

    # check if an attachment is linked as the _thumbnail_id in postmeta
    thumbnail_meta_key_nodes = item.xpath('./wp:postmeta/wp:meta_key[text()="_thumbnail_id"]', namespaces=ns_dict)
    for tn in thumbnail_meta_key_nodes:
        post_id = tn.getparent().find('wp:meta_value', namespaces=ns_dict).text
        if post_id:
            attachment = attachment_dict.get(post_id)
            if attachment is not None:
                attachments.append(attachment_dict.get(post_id))
            else:
                failed_post_ids.append(post_id)
                # print ('FAILED IMAGE IN THUMBANAIL', post_id)
    return attachments

used_attachments = []
def generate_xml_file(items, start):
    chunk_filename = '{}_{}-{}.xml'.format('.'.join(filename.split('.')[:-1]), start, start + len(items))
    print ('GENERATING {}'.format(chunk_filename))

    # Create the root element with the right namespace
    rss = etree.Element('rss', nsmap=ns_dict)
    for att in root.attrib:
        rss.attrib[att] = root.get(att)

    # Make a new document tree
    doc = etree.ElementTree(rss)

    # Add the channel
    channel = etree.SubElement(rss, 'channel')
    if channel_title != None:
        channel.append(channel_title)
    if channel_link != None:
        channel.append(channel_link)
    if channel_desc != None:
        channel.append(channel_desc)
    if channel_pub_date != None:
        channel.append(channel_pub_date)
    if channel_language != None:
        channel.append(channel_language)
    if channel_base_site_url != None:
        channel.append(channel_base_site_url)
    if channel_base_blog_url != None:
        channel.append(channel_base_blog_url)


    # add items to new rss tree and
    # get the used authors and attachments
    authors = []
    attachments = []
    global oldest_post_date
    for i in items:
        # we change all post types to post ('article', 'post', 'news')
        i.find('wp:post_type', namespaces=ns_dict).text = etree.CDATA('post')

        # set the mfn-post-hide-image metadata
        post_hide_image = i.xpath('wp:postmeta/wp:meta_key[text()="mfn-post-hide-image"]', namespaces=ns_dict)
        if len(post_hide_image) == 0:
            # meta data doesn't exist so we need to add it
            meta_tag = etree.SubElement(i, '{{{}}}postmeta'.format(ns_dict['wp']))
            meta_key = etree.SubElement(meta_tag, '{{{}}}meta_key'.format(ns_dict['wp']))
            meta_key.text = etree.CDATA('mfn-post-hide-image')
            meta_value = etree.SubElement(meta_tag, '{{{}}}meta_value'.format(ns_dict['wp']))
            meta_value.text = etree.CDATA('0')

        # collect oldest post date
        post_date = i.find('wp:post_date', namespaces=ns_dict).text
        post_date = datetime.datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
        if post_date < oldest_post_date:
            oldest_post_date = post_date
        # add item to new rss tree
        channel.append(i)
        authors.extend(get_item_authors(items[0]))
        new_attachments = get_item_attachments(i)
        attachments.extend(new_attachments)
        # only used for end statistics
        used_attachments.extend(new_attachments)

    # add authors to new rss tree
    for a in authors:
        channel.append(a)

    # add attachments to new rss tree
    for a in attachments:
        channel.append(a)

    # Save to XML file
    doc.write('{}/{}'.format(results_folder, chunk_filename), xml_declaration=True, encoding=encoding)


# split the post_list into chunks of {chunk_size} items
# and generate an xml file for every chunk
start = 0
end = len(post_list) 
for i in range(start, end, chunk_size): 
    generate_xml_file(post_list[i:i+chunk_size], i)


# print results
cpid = []
for a in used_attachments:
    if a is not None:
        cpid.append(a.find('wp:post_id', namespaces=ns_dict).text)

print ('ITEMS: ', len(items))
print ('ATTACHMENTS: ', len(attachment_dict))
print ('POSTS: ', len(post_list))
print ('AUTHORS: ', len(author_dict))

unused_post_ids = []
for k in attachment_dict.keys():
    if k not in cpid:
        unused_post_ids.append(k)
print ('LINKED POSTIDS THAT DONT EXIST: ', len(failed_post_ids))
print ('UNIQUE USED ATTACHMENTS: ', len(set(cpid)))
print ('UNUSED ATTACHMENTS: ', len(unused_post_ids))
print ('OLDEST POST DATE: ', oldest_post_date)
# print (unused_post_ids)
