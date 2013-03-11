#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
This script allow you to export content from an old Phorum 3.x to pure WordPress objects (pages & comments).

It browse the MySQL database of a Phorum instance and generate an XML file. The XML produced is a WXR file (WordPress eXtended RSS), which can be imported into a plain WordPress site.

A Phorum thread is imported as an empty page with the thread's title. All its replies are imported as comments of that page.
A top-level page is then created, and all its threads are linked from that parent page.

The script requires the following python modules:
    * lxml
    * PyMySQL
    * bbcode

These can easely be installed on Debian with the following commands:
    $ aptitude install python-pip python-lxml
    $ pip install PyMySQL bbcode
"""

import time
import random
import bbcode
import pymysql
import operator
import HTMLParser
import email.utils
import unicodedata
from lxml import etree
from datetime import datetime


## Configuration

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''

PHORUM_DB = 'phorum'
PHORUM_FORUM_ID = 'main_forum'
PHORUM_USER_TABLE = 'forums_auth'

WORDPRESS_ROOT_URL = 'http://example.com'

XML_FILEPATH = './phorum-export.xml'

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

conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=PHORUM_DB)
cr = conn.cursor()

def query(table_name, columns, extra=''):
    """
    Utility method to query the database
    """
    results = []
    q = "SELECT %s FROM %s %s" % (
        ', '.join(["`%s`" % c for c in columns]),
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
h = HTMLParser.HTMLParser()
clean_text = lambda s: s.replace('[%sig%]', '').replace('\r\n', '\n').strip()
rfc822_date = lambda d: email.utils.formatdate(time.mktime(d.timetuple()))
normalize_url = lambda s: '-'.join([w for w in ''.join([c.isalnum() and c or '-' for c in unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').lower()]).split('-') if w])
strip_prefix = lambda s, prefix: s[len(prefix):] if s.startswith(prefix) else s
normalize_title = lambda s: h.unescape(strip_prefix(strip_prefix(s, 'Re: '),'Re : '))

# XML items
items = []

# Database extraction

# parentless messages are the start of a thread
subjects = dict([(s['id'], s['subject']) for s in query(PHORUM_FORUM_ID, ['id', 'subject'])])
topics = query(PHORUM_FORUM_ID, ['id', 'datestamp', 'thread', 'parent', 'author', 'subject', 'email', 'host', 'approved', 'userid'], "WHERE parent = 0")
replies = query(PHORUM_FORUM_ID, ['id', 'datestamp', 'thread', 'parent', 'author', 'subject', 'email', 'host', 'approved', 'userid'], "WHERE parent != 0")
bodies = dict([(b['id'], b) for b in query(PHORUM_FORUM_ID + "_bodies", ['id', 'body', 'thread'])])
users = dict([(u['id'], u) for u in query(PHORUM_USER_TABLE, ['id', 'name', 'username', 'email', 'webpage', 'image'])])

# Utility to get a new ID while avoiding collisions
reserved_ids = [t['id'] for t in topics] + [t['id'] for t in replies]
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
subject_follow_ups = []

for topic in topics:
    # Prepare content
    topic_replies = [r for r in replies if r['thread'] == topic['id']]
    topic_url = "%s/?p=%s" % (WORDPRESS_ROOT_URL, topic['id'])
    topic_slug = normalize_url(topic['subject'])
    topic_link = "%s%s/" % (forum_link, topic_slug)

    # Save topics as pages
    page = etree.Element("item")
    etree.SubElement(page, "title").text = topic['subject']
    etree.SubElement(page, "link").text = topic_link
    etree.SubElement(page, DC + "creator").text = 'admin'
    etree.SubElement(page, WP + "post_name").text = topic_slug
    etree.SubElement(page, "guid", attrib={"isPermaLink": "false"}).text = topic_url
    etree.SubElement(page, "pubDate").text = rfc822_date(topic['datestamp'])
    etree.SubElement(page, WP + "post_id").text = str(topic['id'])
    etree.SubElement(page, WP + "post_date").text = topic['datestamp'].isoformat(' ')
    etree.SubElement(page, WP + "post_date_gmt").text = topic['datestamp'].isoformat(' ')
    etree.SubElement(page, WP + "status").text = topic['approved'] == 'Y' and "publish" or "draft"
    etree.SubElement(page, WP + "post_type").text = "page"
    etree.SubElement(page, WP + "post_parent").text = forum_page_id
    etree.SubElement(page, WP + "comment_status").text = "open"
    etree.SubElement(page, WP + "ping_status").text = "closed"

    # Put the content of the topic to a dedicated comment
    topic_replies.insert(0, topic)

    # Save replies as comments
    for reply in topic_replies:
        user = None
        if reply['userid']:
          user = users[reply['userid']]
        user_email = reply['email']
        if not user_email and user:
          user_email = user['email']
        user_url = ''
        if user:
          user_url = user['webpage'] or user['image']

        # If parent title is not the same, include it in the message
        reply_content = ''
        parent_title = normalize_title(subjects.get(reply['parent'], ''))
        reply_title = normalize_title(reply['subject'])
        if parent_title and parent_title != reply_title and (parent_title, reply_title) not in subject_follow_ups:
          reply_content += "New subject: %s\n\n" % reply_title
          subject_follow_ups.append((parent_title, reply_title))
        reply_content += clean_text(bodies[reply['id']]['body'])

        comment = etree.Element(WP + "comment")
        etree.SubElement(comment, WP + "comment_id").text = str(reply['id'])
        etree.SubElement(comment, WP + "comment_approved").text = reply['approved'] == 'Y' and "1" or "0"
        etree.SubElement(comment, WP + "comment_author").text = etree.CDATA(reply['author'])
        etree.SubElement(comment, WP + "comment_author_email").text = user_email
        etree.SubElement(comment, WP + "comment_author_url").text = user_url
        etree.SubElement(comment, WP + "comment_author_IP").text = reply['host']
        etree.SubElement(comment, WP + "comment_type").text = ""
        etree.SubElement(comment, WP + "comment_parent").text = str(reply['parent'])
        etree.SubElement(comment, WP + "comment_date").text = reply['datestamp'].isoformat(' ')
        etree.SubElement(comment, WP + "comment_date_gmt").text = reply['datestamp'].isoformat(' ')
        etree.SubElement(comment, WP + "comment_content").text = etree.CDATA(bbcode.render_html(reply_content).replace('<br />', '\n').replace('<br/>', '\n'))
        page.append(comment)

    items.append(page)

    # Save some topic information for later
    topic_list.append({
        'link': topic_link,
        'title': topic['subject'],
        'date': topic['datestamp'],
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
