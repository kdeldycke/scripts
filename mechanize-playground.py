#!/usr/bin/python

import re
import random
import sys
import logging
import mechanize


def getRandomUserAgent():
  """
    Get a random user agent. The list is the most used User agent on my sites.
    TODO: use statistics to get UA.
  """
  agent_list = [
      "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)"
    , "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.8.0.1) Gecko/20060111 Firefox/1.5.0.1"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Wanadoo 6.7)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; HbTools 4.7.0)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Wanadoo 6.7)"
    , "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr-FR; rv:1.7.5) Gecko/20041108 Firefox/1.0"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Win 9x 4.90)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows 98; Wanadoo 5.6; Hotbar 4.5.1.0)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Wanadoo 6.2)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows 98)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; AOL 9.0; Windows NT 5.1; .NET CLR 1.1.4322)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"
    , "Mozilla/4.0 (compatible; MSIE 6.0; AOL 9.0; Windows NT 5.1; SV1)"
    ]
  return agent_list[random.randint(0, len(agent_list)-1)]



# Get random user agent
user_agent = getRandomUserAgent()
print "Selected User-Agent: '%s'" % user_agent

# XXX Is this necessary to patch User-Agent here ?
# import urllib2
# opener = urllib2.build_opener()
# opener.addheaders = [("User-agent", user_agent)]
# urllib2.install_opener(opener)

# XXX Is this necessary to patch User-Agent here ?
# cookies = mechanize.CookieJar()
# opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
# opener.addheaders = [("User-agent", user_agent)]
# # Install custom OpenerDirector globally
# mechanize.install_opener(opener)

# To make sure all debug output will be printed
logger = logging.getLogger("mechanize")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


br = mechanize.Browser()

# Use privoxy (linked to tor) as proxy
br.set_proxies({ "http" : "127.0.0.1:8118"
               , "https": "127.0.0.1:8118"
               })

# Set User-agent for this session
br.addheaders = [("User-agent", user_agent)]

# Don't get robot.txt: this request is done by urllib2 with hard-coded 'Python-urllib' User-Agent.
br.set_handle_robots(False)

# Initialize browser to some debug messages
br.set_debug_redirects(True)
br.set_debug_responses(True)
br.set_debug_http(True)


# Start browsing the net
br.open("http://wordpress.coolcavemen.com/")

#br = mechanize.urlopen("http://wordpress.coolcavemen.com/")


print br.geturl()
print br.title()
print br.viewing_html()
# print br.info()  # headers
#print br.read()  # body

#-> http://www.ietf.org/rfc/rfc2068.txt

#    For compatibility with HTTP/1.0 applications, HTTP/1.1 requests
#    containing a message-body MUST include a valid Content-Length header
#    field unless the server is known to be HTTP/1.1 compliant. If a
#    request contains a message-body and a Content-Length is not given,
#    the server SHOULD respond with 400 (bad request) if it cannot
#    determine the length of the message, or with 411 (length required) if
#    it wishes to insist on receiving a valid Content-Length.

# 5.2 The Resource Identified by a Request
#
#    HTTP/1.1 origin servers SHOULD be aware that the exact resource
#    identified by an Internet request is determined by examining both the
#    Request-URI and the Host header field.
#
#    An origin server that does not allow resources to differ by the
#    requested host MAY ignore the Host header field value. (But see
#    section 19.5.1 for other requirements on Host support in HTTP/1.1.)
#
#    An origin server that does differentiate resources based on the host
#    requested (sometimes referred to as virtual hosts or vanity
#    hostnames) MUST use the following rules for determining the requested
#    resource on an HTTP/1.1 request:
#
#      1. If Request-URI is an absoluteURI, the host is part of the
#         Request-URI. Any Host header field value in the request MUST be
#         ignored.
#
#      2. If the Request-URI is not an absoluteURI, and the request
#         includes a Host header field, the host is determined by the Host
#         header field value.
#
#      3. If the host as determined by rule 1 or 2 is not a valid host on
#         the server, the response MUST be a 400 (Bad Request) error
#         message.
#
#    Recipients of an HTTP/1.0 request that lacks a Host header field MAY
#    attempt to use heuristics (e.g., examination of the URI path for
#    something unique to a particular host) in order to determine what
#    exact resource is being requested.



# 14.23 Host
#
#    The Host request-header field specifies the Internet host and port
#    number of the resource being requested, as obtained from the original
#    URL given by the user or referring resource (generally an HTTP URL,
#    as described in section 3.2.2). The Host field value MUST represent
#    the network location of the origin server or gateway given by the
#    original URL. This allows the origin server or gateway to
#    differentiate between internally-ambiguous URLs, such as the root "/"
#    URL of a server for multiple host names on a single IP address.
#
#           Host = "Host" ":" host [ ":" port ]    ; Section 3.2.2
#
#    A "host" without any trailing port information implies the default
#    port for the service requested (e.g., "80" for an HTTP URL). For
#    example, a request on the origin server for
#    <http://www.w3.org/pub/WWW/> MUST include:
#
#           GET /pub/WWW/ HTTP/1.1
#           Host: www.w3.org
#
#    A client MUST include a Host header field in all HTTP/1.1 request
#    messages on the Internet (i.e., on any message corresponding to a
#    request for a URL which includes an Internet host address for the
#    service being requested). If the Host field is not already present,
#    an HTTP/1.1 proxy MUST add a Host field to the request message prior
#    to forwarding it on the Internet. All Internet-based HTTP/1.1 servers
#    MUST respond with a 400 status code to any HTTP/1.1 request message
#    which lacks a Host header field.















# Exit early
sys.exit()




# XXX Big question: is referrer automaticcaly set ? Should I do it myself ?
#        -> take a look at .follow_link()
import mechanize, urllib2
req = urllib2.Request("http://foobar.com/")
req.add_header("Referer", "http://wwwsearch.sourceforge.net/mechanize/")
r = mechanize.urlopen(req)







import socket
socket.getaddrinfo(socket.gethostname(), None)[0][4][0]


# follow second link with element text matching regular expression
response1 = br.follow_link(text_regex=r"Register", nr=0)
assert br.viewing_html()
print br.title()
print response1.geturl()
print response1.info()  # headers
print response1.read()  # body
response1.close()  # (shown for clarity; in fact Browser does this for you)


first_form = None
for form in br.forms():
  print form
  first_form = form
  break


#form.set_value("megakev", name="cheeses")
first_form["user_login"] = "megakev"
first_form["user_email"] = "kev@coolcavemen.com"
print first_form

#response2 = first_form.submit()  # submit current form


request2 = first_form.click()  # urllib2.Request object
try:
    response2 = urllib2.urlopen(request2)
except urllib2.HTTPError, response2:
    pass

print response2.geturl()
print response2.info()  # headers
print response2.read()  # body




# br.select_form(name="order")
# # Browser passes through unknown attributes (including methods)
# # to the selected HTMLForm (from ClientForm).
# br["cheeses"] = ["mozzarella", "caerphilly"]  # (the method here is __setitem__)
# response2 = br.submit()  # submit current form
#
# # print currently selected form (don't call .submit() on this, use br.submit())
# print br.form
#
# response3 = br.back()  # back to cheese shop (same data as response1)
# # the history mechanism returns cached response objects
# # we can still use the response, even though we closed it:
# response3.seek(0)
# response3.read()
# response4 = br.reload()  # fetches from server
#
# for form in br.forms():
#     print form
# # .links() optionally accepts the keyword args of .follow_/.find_link()
# for link in br.links(url_regex="python.org"):
#     print link
#     br.follow_link(link)  # takes EITHER Link instance OR keyword args
#     br.back()