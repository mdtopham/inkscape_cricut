#!/usr/bin/env python

# These two lines are only needed if you don't put the script directly into
# the installation directory
import sys
sys.path.append('/usr/share/inkscape/extensions')

# We will use the inkex module with the predefined Effect base class.
import inkex, cubicsuperpath
# The simplestyle module provides functions for style parsing.
from simplestyle import *
from simpletransform import * 
from lxml.etree import QName

class CriCutCleanupEffect(inkex.Effect):
    """
    Cleanup SVG for use in CriCut Design Space
    """
    def __init__(self):
        """
        Constructor
        """
        inkex.Effect.__init__(self)

    def effect(self):
        """
        Effects behaviour.
        Combines similar strokes into paths so CriCut Design Space can handle them
        """
        #
        svg = self.document.getroot()
        width  = self.unittouu(svg.get('width'))
        height = self.unittouu(svg.attrib['height'])
        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'CriCut')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

        x = 0
        each = ""
        obj_styles = {}
        identity = parseTransform("")
        #
        # For each unique line style, add it to a dictionary/set
        # so we can later use the id's to build a path
        for obj in svg.xpath('//svg:line|//svg:circle|//svg:rectx', namespaces=inkex.NSS):
          style = obj.get('style','')
          matrix = composeParents(obj,identity)
          #style = style + formatTransform(matrix)
          id = obj.get('id')
          if not style in obj_styles:
            obj_styles[style] = set()
          obj_styles[style].add(id)

        ## For each dictionary
        ## Iterate it's set and output paths instead. 
        for obj_each in obj_styles: 
          M = ""
          style = ""
          for obj_set in obj_styles[obj_each]:
            p = "//*[@id='" + obj_set + "']"
            element = svg.xpath(p,namespaces=inkex.NSS) 
            style = element[0].get('style','')
            element_type = QName(element[0]).localname
            new_transform = composeParents(element[0],identity)
            newM = ""
            if (element_type == "rect"):
              x = float(element[0].attrib['x'])
              y = float(element[0].attrib['y'])
              width = float(element[0].attrib['width'])
              height = float(element[0].attrib['height'])
              newM = " M " + str(x) + "," + str(y) + " " + str(x+width) + "," + str(y) + " " + str(x+width) + "," + str(y+height) + " " + str(x) + "," + str(y+height) + " " + str(x) + "," + str(y) + " "

            if (element_type == "line"):
              x1 = element[0].attrib['x1']
              x2 = element[0].attrib['x2']
              y1 = element[0].attrib['y1']
              y2 = element[0].attrib['y2']
              newM = " M " + x1 + "," + y1 + " L " + x1 + "," + y1 + " " + x2 + "," + y2 + " "
            if (element_type == "circle"):
              cy = element[0].attrib['cy']
              cx = element[0].attrib['cx']
              r = float(element[0].attrib['r'])
              newM += " M " + cx + " " + cy 
              newM += " m " + str(r * -1) + ",0 "
              newM += " a " + str(r) + "," + str(r) + " 0 1,0 " + str(r*2) + ",0 "
              newM += "a " + str(r) + "," + str(r) + " 0 1,0 " + str((r*2)*-1) + ",0 z "
            p = cubicsuperpath.parsePath(newM)
            applyTransformToPath(new_transform,p)
            newM = cubicsuperpath.formatPath(p) 
            M += newM
          # obj_each
            
          attribs = { 'd':M, 'style':style } ## , 'transform':formatTransform(new_transform) }
                      ###inkex.addNS('label','inkscape'):name },  
          inkex.etree.SubElement(layer, inkex.addNS('path','svg'), attribs)


# Create effect instance and apply it.
effect = CriCutCleanupEffect()
effect.affect()

