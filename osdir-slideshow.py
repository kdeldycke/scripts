#!/usr/bin/python

from os import system
from commands import getstatusoutput


if __name__ == "__main__":

  to_download = [ (147, 101)
                , (50, 27)
                , (140, 41)
                , (155, 105)
                ]

  for (product, slide_nb) in to_download:
    system("mkdir ./" + str(product))
    for slide_id in range(slide_nb):
      url = "http://osdir.com/shots/slideshows/" + str(product) + "/" + str(slide_id + 1) + ".gif"
      result = getstatusoutput("wget -P ./" + str(product) + "/ " + url)
      print " * Downloaded : " + url
    # rename here 1.gif to 01.gif (and 20.gif to 020.gif) if needed
