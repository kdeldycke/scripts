#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This scripts allows you to export bbPress content (forums, topics & replies) to pure WordPress objects (pages & comments).

It browse the MySQL database of a bbPress instance and generate an XML file. The XML produced is a WXR file (WordPress eXtended RSS), which can be imported into a plain WordPress site.

A bbPress thread is imported as an empty page with the thread's title. All its replies are imported as comments of that page.
A top-level page is then created for each forum, and all its threads are linked from that parent page.

The script requires the following python modules:
    * lxml
    * PyMySQL

These can easely be installed on Debian with the following commands:
    $ aptitude install python-pip python-lxml
    $ pip install PyMySQL
"""

import time
import random
import pymysql
import operator
import email.utils
import unicodedata
from lxml import etree
from datetime import datetime


## Configuration

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''

BBPRESS_DB = 'mysite'
BBPRESS_TABLE_PREFIX ='wp_'

WORDPRESS_ROOT_URL = 'http://mysite.example.com'

XML_FILEPATH = './bbpress-export.xml'

# List of user IDs which can create a page
REGISTERED_USER_IDS = [1, 3, 4, 5, 6, 7, 76, 77]

## End of configuration


NS_EXCERPT = "http://wordpress.org/export/1.2/excerpt/"
NS_CONTENT = "http://purl.org/rss/1.0/modules/content/"
NS_WFW = "http://wellformedweb.org/CommentAPI/"
NS_DC = "http://purl.org/dc/elements/1.1/"
NS_WP = "http://wordpress.org/export/1.2/"

EXCERPT = "{%s}" % NS_EXCERPT
CONTENT = "{%s}" % NS_CONTENT
WFW = "{%s}" % NS_WFW
DC = "{%s}" % NS_DC
WP = "{%s}" % NS_WP

NSMAP = {
    'excerpt': NS_EXCERPT,
    'content': NS_CONTENT,
    'wfw': NS_WFW,
    'dc': NS_DC,
    'wp': NS_WP,
    }

conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=BBPRESS_DB)
cr = conn.cursor()

def query(table_name, columns, extra=''):
    """
    Utility method to query the database
    """
    results = []
    q = "SELECT %s FROM %s%s %s" % (
        ', '.join(["`%s`" % c for c in columns]),
        BBPRESS_TABLE_PREFIX,
        table_name,
        extra,
        )
    cr.execute(q)
    for row in cr.fetchall():
        cleaned_row_values = []
        for r in row:
            if isinstance(r, str):
                try:
                    r = r.decode('UTF-8')
                except UnicodeDecodeError:
                    r = r.decode('latin-1')
            cleaned_row_values.append(r)
        results.append(dict(zip(columns, cleaned_row_values)))
    return results

# Utility method to clean up multi-line HTML text.
clean_text = lambda s: s.replace('\r\n', '\n').strip().replace('\n', "<br />")
rfc822_date = lambda d: email.utils.formatdate(time.mktime(d.timetuple()))
normalize_url = lambda s: '-'.join([w for w in ''.join([c.isalnum() and c or '-' for c in unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').lower()]).split('-') if w])

# XML items
items = []

# Database extraction
topics = query('posts', ['ID', 'post_title', 'post_content', 'post_author', 'post_date', 'post_date_gmt', 'post_status'], "WHERE post_type='topic' AND post_status='publish'")
replies = query('posts', ['ID', 'post_title', 'post_content', 'post_author', 'post_date', 'post_date_gmt', 'post_parent'], "WHERE post_type='reply' AND post_status='publish'")
users = dict([(u['ID'], u) for u in query('users', ['ID', 'user_login', 'display_name', 'user_email', 'user_url'])])
# Add an anonymous user
users.update({0: {'ID': 0, 'display_name': "Anonymous", 'user_email': "", 'user_url': ""}})

# Utility to get a new ID wil avoiding collisions
reserved_ids = [t['ID'] for t in topics]
reserved_ids.extend([r['ID'] for r in replies])
reserved_ids.extend(users.keys())
def get_new_id():
    while True:
        new_id = random.randint(0, 99999999)
        if new_id not in reserved_ids:
            reserved_ids.append(new_id)
            return new_id

# Create a top-level page to be the common parent of all threads
now = datetime.now()
forum_page_id = str(get_new_id())
forum_url = "%s/?p=%s" % (WORDPRESS_ROOT_URL, forum_page_id)
forum_slug = "forum"
forum_link = "%s/%s/" % (WORDPRESS_ROOT_URL, forum_slug)
forum_page = etree.Element("item")
etree.SubElement(forum_page, "title").text = "Forum Archive"
etree.SubElement(forum_page, "link").text = forum_link
etree.SubElement(forum_page, WP + "post_name").text = forum_slug
etree.SubElement(forum_page, "guid", attrib={"isPermaLink": "false"}).text = forum_url
etree.SubElement(forum_page, "pubDate").text = rfc822_date(now)
etree.SubElement(forum_page, DC + "creator").text = 'admin'
etree.SubElement(forum_page, WP + "post_id").text = forum_page_id
etree.SubElement(forum_page, WP + "post_date").text = now.isoformat(' ')
etree.SubElement(forum_page, WP + "post_date_gmt").text = now.isoformat(' ')
etree.SubElement(forum_page, WP + "status").text = "publish"
etree.SubElement(forum_page, WP + "post_type").text = "page"
etree.SubElement(forum_page, WP + "comment_status").text = "closed"
etree.SubElement(forum_page, WP + "ping_status").text = "closed"

topic_list = []

for topic in topics:
    # Prepare content
    topic_author = users[topic['post_author']]
    topic_replies = [r for r in replies if r['post_parent'] == topic['ID']]
    topic_url = "%s/?p=%s" % (WORDPRESS_ROOT_URL, topic['ID'])
    topic_slug = normalize_url(topic['post_title'])
    topic_link = "%s%s/" % (forum_link, topic_slug)

    # Save topics as pages
    page = etree.Element("item")
    etree.SubElement(page, "title").text = topic['post_title']
    etree.SubElement(page, "link").text = topic_link
    etree.SubElement(page, WP + "post_name").text = topic_slug
    etree.SubElement(page, "guid", attrib={"isPermaLink": "false"}).text = topic_url
    etree.SubElement(page, "pubDate").text = rfc822_date(topic['post_date'])
    etree.SubElement(page, WP + "post_id").text = str(topic['ID'])
    etree.SubElement(page, WP + "post_date").text = topic['post_date'].isoformat(' ')
    etree.SubElement(page, WP + "post_date_gmt").text = topic['post_date_gmt'].isoformat(' ')
    etree.SubElement(page, WP + "status").text = topic['post_status']
    etree.SubElement(page, WP + "post_type").text = "page"
    etree.SubElement(page, WP + "post_parent").text = forum_page_id
    etree.SubElement(page, WP + "comment_status").text = "open"
    etree.SubElement(page, WP + "ping_status").text = "closed"

    # If the user is allowed to create a page, then the content of the topic is but in the page itself,
    # else we create a new comment.
    if topic_author['ID'] in REGISTERED_USER_IDS:
        etree.SubElement(page, DC + "creator").text = topic_author['user_login']
        etree.SubElement(page, CONTENT + "encoded").text = etree.CDATA(clean_text(topic['post_content']))
    else:
        etree.SubElement(page, DC + "creator").text = 'admin'
        topic_replies.insert(0, {
            'post_author': topic['post_author'],
            'ID': get_new_id(),
            'post_date': topic['post_date'],
            'post_date_gmt': topic['post_date_gmt'],
            'post_content': topic['post_content'],
            })

    # Save replies as comments
    for reply in topic_replies:
        author = users[reply['post_author']]
        comment = etree.Element(WP + "comment")
        etree.SubElement(comment, WP + "comment_id").text = str(reply['ID'])
        etree.SubElement(comment, WP + "comment_approved").text = "1"
        etree.SubElement(comment, WP + "comment_author").text = etree.CDATA(author['display_name'])
        etree.SubElement(comment, WP + "comment_author_email").text = author['user_email']
        etree.SubElement(comment, WP + "comment_author_url").text = author['user_url']
        etree.SubElement(comment, WP + "comment_author_IP").text = "127.0.0.1"
        etree.SubElement(comment, WP + "comment_type").text = ""
        etree.SubElement(comment, WP + "comment_parent").text = ""
        etree.SubElement(comment, WP + "comment_date").text = reply['post_date'].isoformat(' ')
        etree.SubElement(comment, WP + "comment_date_gmt").text = reply['post_date_gmt'].isoformat(' ')
        etree.SubElement(comment, WP + "comment_content").text = etree.CDATA(clean_text(reply['post_content']))
        page.append(comment)

    items.append(page)

    # Save some topic information for later
    topic_list.append({
        'link': topic_link,
        'title': topic['post_title'],
        'date': topic['post_date_gmt'],
        })

# As content of top-level forum page, list all topics
current_year = None
forum_content = ""
topic_list.sort(key=operator.itemgetter('date'))
topic_list.reverse()
for t in topic_list:
    if current_year != t['date'].year:
        if current_year is not None:
            forum_content += "</ul>\n\n"
        current_year = t['date'].year
        forum_content += "<h2>%s</h2>\n<ul>\n" % current_year
    forum_content += "<li><a href='%s'>%s</a></li>\n" % (t['link'], t['title'])
forum_content += "</ul>\n"
etree.SubElement(forum_page, CONTENT + "encoded").text = etree.CDATA(forum_content)
items.append(forum_page)

# Generate the final XML document
channel = etree.Element("channel")
etree.SubElement(channel, WP + "wxr_version").text = "1.2"
for item in items:
    channel.append(item)
root = etree.Element("rss", attrib={"version": "2.0"}, nsmap=NSMAP)
root.append(channel)

f = open(XML_FILEPATH, 'w')
f.write(etree.tostring(root, xml_declaration=True, pretty_print=True, encoding='UTF-8'))
f.close()

cr.close()
conn.close()
