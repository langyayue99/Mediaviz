from xml.etree.cElementTree import Element, ElementTree, SubElement, tostring
import matplotlib.colors as colors


def parse_colors(path):
    tree = ElementTree(file=path)
    root = tree.getroot()
    nodes = root.findall('./{http://www.gexf.net/1.2draft}graph/{http://www.gexf.net/1.2draft}nodes/')
    color_codes = {}
    for node in nodes:
        id = node.attrib['id']
        color_code = node.findall('./{http://www.gexf.net/1.1draft/viz}color')[0].attrib
        rgb_color_code = color_code['r'],color_code['g'],color_code['b']
        hex_code = colors.rgb2hex([(1.0*float(x))/255 for x in rgb_color_code])
        color_codes[id] = hex_code
    return color_codes



def parse_size(path):
    tree = ElementTree(file=path)
    root = tree.getroot()
    nodes = root.findall('./{http://www.gexf.net/1.2draft}graph/{http://www.gexf.net/1.2draft}nodes/')
    sizes = {}
    for node in nodes:
        id = node.attrib['id']
        size = node.findall('./{http://www.gexf.net/1.1draft/viz}size')[0].attrib
        sizes[id]=size['value']
    return sizes




def parse_position(path):
    tree = ElementTree(file=path)
    root = tree.getroot()
    nodes = root.findall('./{http://www.gexf.net/1.2draft}graph/{http://www.gexf.net/1.2draft}nodes/')
    positions = {}
    for node in nodes:
        id = node.attrib['id']
        position = node.findall('./{http://www.gexf.net/1.1draft/viz}position')[0].attrib
        positions[id]= (position['x'],position['y'])
    return positions