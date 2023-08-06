import xml.etree.cElementTree as etree

def getelements(filename_or_file, tag):
    context = iter(etree.iterparse(filename_or_file, events=('start', 'end')))
    _, root = next(context) # get root element
    for event, elem in context:
        if event == 'end' and elem.tag == tag:
            yield elem
            root.clear() # preserve memory