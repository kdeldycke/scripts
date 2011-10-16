#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2009 Kevin Deldycke <kevin@deldycke.com>
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

"""Hard-coded mapping of predefined colors.
In The future, use a big table based on Rosco and Lee filters.
"""
COLORS = {
  # Extremes
  'Black': (  0,   0,   0),
  'White': (255, 255, 255),
  # RGB
  'Red'  : (255,   0,   0),
  'Green': (  0, 255,   0),
  'Blue' : (  0,   0, 255),
  # CMY
  'Cyan'   : (  0, 255, 255),
  'Magenta': (255,   0, 255),
  'Yellow' : (255, 255,   0),
  # Bright CMY
  'Bright Cyan'   : (127, 255, 255),
  'Bright Magenta': (255, 127, 255),
  'Bright Yellow' : (255, 255, 127),
  # Pale colors
  'Salmon'  : (255, 127, 127),
  'Lemon'   : (127, 255, 127),
  'Lavender': (127, 127, 255),
  # Rich colors
  'Azure'     : (  0, 127, 255),
  'Rose'      : (255,   0, 127),
  'Chartreuse': (127, 255    0),
  'Green Blue': (  0, 255, 127),
  'Purple'    : (127,   0, 255),
  'Orange'    : (255, 127,   0),
  }

def getColorFromID(color_id):
  DEFAULT_COLOR = 'Red'
  if color_id in COLORS:
    color_name = color_id
  # TODO: Try harder to find the color (lowercase, etc.)
  else:
    color_name = DEFAULT_COLOR
  return (color_name, COLORS.get(color_name))


"""This data structure define our virtual 2D panel.
   All these data should be extracted from QLX fixture definitions and wordkspace.
"""
VIRTUAL_PANEL = { 'name'                      : '4x8 pixels virtual panel'
                , 'short_name'                : 'Panel'
                , 'description'               : 'A set of 4 Wider Panel in 48 channels mode, positionned vertically'
                , 'fixture_model'             : 'Mac Mah - Wider Panel'
                , 'workspace_function_last_id': 300
                # Bus used by QLC to set fading time and step speed of chases
                , 'fader_bus_id'           : 0
                , 'speed_bus_id'           : 1
                , 'fixture_quantity'       : 4
                , 'fixture_id_start_offset': 6
                , 'dmx_start_offset'       : 75
                , 'dmx_horizontal_offset'  : 48
                , 'pixel_map_type'         : 'rgb_matrix_vertical_template'
                , 'relative_pixel_map'     : [ [( 1,  2,  3)]
                                             , [( 7,  8,  9)]
                                             , [(13, 14, 15)]
                                             , [(19, 20, 21)]
                                             , [(25, 26, 27)]
                                             , [(31, 32, 33)]
                                             , [(37, 38, 39)]
                                             , [(43, 44, 45)]
                                             ]
                }


def getNewFunctionID():
  new_available_id = VIRTUAL_PANEL['workspace_function_last_id'] + 1
  VIRTUAL_PANEL.update({'workspace_function_last_id': new_available_id})
  return new_available_id


def getPanelSize():
  """Get the pixel dimensions of the 2D virtual panel
  """
  return (VIRTUAL_PANEL['fixture_quantity'], len(VIRTUAL_PANEL['relative_pixel_map']))


def getAbsoluteDMXChannelPixelMapping():
  """ Compute the pixel RGB mapping returning absolute DMX channel adresses
  """
  normalized_pixel_map = []
  for row in VIRTUAL_PANEL['relative_pixel_map']:
    pixel_template = row[0]
    normalized_row = []
    for column_index in range(VIRTUAL_PANEL['fixture_quantity']):
      normalized_row.append(tuple([c + (VIRTUAL_PANEL['dmx_horizontal_offset'] * column_index) + VIRTUAL_PANEL['dmx_start_offset'] for c in pixel_template]))
    normalized_pixel_map.append(normalized_row)
  return normalized_pixel_map


def getFixtureRelativePixelMapping():
  """ Same as above, but DMX channels are expressed relative to their fixture (as QLC does).
  """
  normalized_pixel_map = []
  for row in VIRTUAL_PANEL['relative_pixel_map']:
    pixel_template = row[0]
    normalized_row = []
    for fixture_index in range(VIRTUAL_PANEL['fixture_quantity']):
      normalized_row.append(tuple([(VIRTUAL_PANEL['fixture_id_start_offset'] + fixture_index, c) for c in pixel_template]))
    normalized_pixel_map.append(normalized_row)
  return normalized_pixel_map


#def getFixtureIDList(fixtures = FIXTURES):
  #"""Return the list of fixtures we will generate macros for
  #"""
  #FIXTURES_ID_LIST = [6, 7, 8, 9]
  #return FIXTURES_ID_LIST


#def createWiderPanelColorSection():
  #xml = ""
  #scene_id = 0
  #fixture_number = 0
  #for fixture_id in FIXTURES_ID_LIST:
    #fixture_number += 1
    #for (color_name, color_value) in COLORS.items():
      #for segment in range(1, 9):
        #scene_name = "PANEL LED %s, Section %s - %s" % (fixture_number, segment, color_name)
        #scene_id += 1
        #xml += """
  #<Function Type="Scene" Name="%s" ID="%s" >
   #<Bus Role="Fade" >0</Bus>
   #<Value Fixture="%s" Channel="7" >%s</Value>
   #<Value Fixture="%s" Channel="8" >%s</Value>
   #<Value Fixture="%s" Channel="9" >%s</Value>
  #</Function>""" % (scene_name, scene_id, fixture_id, color_value[0], fixture_id, color_value[1], fixture_id, color_value[2])
  #return xml

def getColorizedPixelAsXML(pixel_def, color_def):
  """ Snippet to get the XML of a colozize a pixel given it's definition and a color.
  """
  xml = ''
  for channel_index in range(len(pixel_def)):
    fixture_id  = pixel_def[channel_index][0]
    channel_id  = pixel_def[channel_index][1]
    color_value = color_def[channel_index]
    xml += """<Value Fixture="%s" Channel="%s">%s</Value>""" % (fixture_id, channel_id, color_value)
  return xml

def createHorizontalGrouping(color_id=None):
  """Create a set of scenes to group pixels horizontally
  """
  (color_name, color_def) = getColorFromID(color_id)
  xml = ''
  # Create a scene for each colored row
  pixel_map = getFixtureRelativePixelMapping()
  for row_index in range(len(pixel_map)):
    dmx_xml = ''
    for pixel in pixel_map[row_index]:
      dmx_xml += getColorizedPixelAsXML(pixel, color_def)
    scene_xml = """
  <Function Type="Scene" Name="%(panel_name)s Row #%(row_number)s %(color_name)s" ID="%(function_id)s">
   <Bus Role="Fade">%(fader_bus)s</Bus>
   %(dmx_xml)s
  </Function>""" % { 'panel_name' : VIRTUAL_PANEL['short_name']
                   , 'row_number' : row_index + 1
                   , 'color_name' : color_name
                   , 'function_id': getNewFunctionID()
                   , 'fader_bus'  : VIRTUAL_PANEL['fader_bus_id']
                   , 'dmx_xml'    : dmx_xml
                   }
    xml += scene_xml
  return xml


def createVerticalGrouping(color_id=None):
  """Create a set of scenes to group pixels vertically
  """
  (color_name, color_def) = getColorFromID(color_id)
  xml = ''
  # Create a scene for each colored row
  pixel_map = getFixtureRelativePixelMapping()
  w, h = getPanelSize()
  for column_index in range(w):
    dmx_xml = ''
    for row in pixel_map:
      pixel = row[column_index]
      dmx_xml += getColorizedPixelAsXML(pixel, color_def)
    scene_xml = """
  <Function Type="Scene" Name="%(panel_name)s Column #%(column_number)s %(color_name)s" ID="%(function_id)s">
   <Bus Role="Fade">%(fader_bus)s</Bus>
   %(dmx_xml)s
  </Function>""" % { 'panel_name'   : VIRTUAL_PANEL['short_name']
                   , 'column_number': column_index + 1
                   , 'color_name'   : color_name
                   , 'function_id'  : getNewFunctionID()
                   , 'fader_bus'    : VIRTUAL_PANEL['fader_bus_id']
                   , 'dmx_xml'      : dmx_xml
                   }
    xml += scene_xml
  return xml


for color_id in COLORS:
  print createHorizontalGrouping(color_id)
  print createVerticalGrouping(color_id)


#print "End"

# Create horizontal and vertical groups for each color
#for color_id in COLORS:
#  vertical_grouping_xml  , vertical_groups   = createHorizontalGrouping(color_id)
#  horizontal_grouping_xml, horizontal_groups = createVerticalGrouping(color_id)
#  big_grouping_xml       , big_groups        = createFullGrouping(color_id)

#print vertical_grouping_xml
#print horizontal_grouping_xml
#print big_grouping_xml
