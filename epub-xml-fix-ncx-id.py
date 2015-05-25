import os
from lxml import etree

# Get the current folder the script resides in.
current_folder = os.getcwd()

# Walk the whole folder tree under the current folder and stop at each node.
for root_folder, sub_folders, file_names in os.walk(current_folder):
    print "Search for OPF files in %s ..." % root_folder

    opf_file_name = None
    ncx_file_name = None

    # Search for both the OPF file and its NCX companion in the same current
    # folder.
    for file_name in file_names:
        if file_name.endswith('.opf'):
            print "OPF file found: %s" % file_name
            opf_file_name = file_name
        if file_name.endswith('.ncx'):
            print "NCX file found: %s" % file_name
            ncx_file_name = file_name

    # Only start playing with XML content if and only if I have both an OPF
    # *and* NCX file in the current folder.
    if opf_file_name and ncx_file_name:

        # Re-build the full string locating the XML file.
        opf_file_path = root_folder + '/' + opf_file_name
        ncx_file_path = root_folder + '/' + ncx_file_name
        print "Full OPF path: %s" % opf_file_path
        print "Full NCX path: %s" % ncx_file_path

        # Open the OPF file
        opened_file = open(opf_file_path, 'r')

        # Now that we have an open OPF file, we can parse its XML content.
        tree = etree.parse(opened_file)

        # Browse the XML tree, searching for the value we care about.
        package = tree.getroot()
        metadata = package.find("{http://www.idpf.org/2007/opf}metadata")
        identifier = metadata.find("{http://purl.org/dc/elements/1.1/}identifier")
        identifier_value = identifier.text

        print "ODF identifier is: %s" % identifier_value

        # Now open and parse the NCX file.
        opened_ncx_file = open(ncx_file_path, 'r')
        tree = etree.parse(opened_ncx_file)

        # Browse the XML tree, searching for the value we care about.
        ncx = tree.getroot()
        head = ncx.find("{http://www.daisy.org/z3986/2005/ncx/}head")
        uid_meta = head.find("{http://www.daisy.org/z3986/2005/ncx/}meta[@name='dtb:uid']")

        # Replace NCX file's meta content by the one we extracted from OPF.
        uid_meta.set("content", identifier_value)

        # Render the modified XML tree object into an XML string.
        xml_string = etree.tostring(tree, xml_declaration=True, encoding='utf-8')

        #xml_string.replace('/n', '/n/r')

        # Save the resulting modification into a new file.
        new_ncx_file_path = ncx_file_path + '-new'
        open(new_ncx_file_path, 'w').write(xml_string)
