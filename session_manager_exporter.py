#!/usr/bin/env python3

# session_manager_exporter.py
# Export all Session Manager (firefox plugin) saved sessions into plain-text files.
# This should make it easier to import them into other browsers and plugins

import sys
import os
import re
import logging
import ast

import click


# Parse a session manager file and extract the session dict and its name
# Returns a tuple (name, data)
def parse_file(file_path):

    logging.info(f'Parsing file {file_path}')
    session_name_regex = re.compile(r'[^=]*=(.*)') # Capture session name
    true_regex = re.compile('true') # .session file writes 'True' as 'true'
    false_regex = re.compile('false') # .session file writes 'False' as 'false'
    none_regex = re.compile('null') # .session file writes 'None' as 'null'
    name = None
    data = None
    with open(file_path) as fh:

        for lineno, line in enumerate(fh):
            # Session name is in line 2
            if lineno==1:
                match_list = session_name_regex.findall(line)
                name = match_list[0]
                logging.info(f'Found session with name {name}')
            # Data is in line 5
            if lineno==4:
                # Parse the line and return the dict
                line = true_regex.sub('True', line)
                line = false_regex.sub('False', line)
                line = none_regex.sub('None', line)

                # Read the session data
                try:
                    data = ast.literal_eval(line) # Session information is written almost as a literal dict() description
                except ValueError as ex:
                    # Write in the log file in which part of the .session file the error was
                    logging.info(f'Failed parsing line:\n{line}\n')
                    _exc_type, exc_value, exc_traceback = sys.exc_info()
                    logging.error("ERROR: %r" % (exc_value))
                    last_tb = exc_traceback
                    while last_tb.tb_next:
                        last_tb = last_tb.tb_next
                    logging.error("Error location: line=%d, col=%d" % (
                        last_tb.tb_frame.f_locals["node"].lineno,
                        last_tb.tb_frame.f_locals["node"].col_offset))
        return (name, data)


# Accept a session dict iterator and write a Firefox bookmarks HTML file
# Accepts an iterator of tuples (name, session_data_dict)
def html_write(session_dict_iter):
    with open('exported_bookmarks.html','w') as fh:

        # Write file header
        fh.write("""<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">"""+
                 """<TITLE>Bookmarks</TITLE>""" + 
                 """<H1>Imported Bookmakrs</H1>""" +
                 """ """ + 
                 """<DL><p>\n"""
                )

        # Iterate over all sessions
        for folder_tuple in session_dict_iter:

            folder_name = folder_tuple[0] # Assuming only one window per session
            logging.info(f'Writing folder {folder_name}')
            folder_data = folder_tuple[1]
            window_1 = folder_data["windows"][0]
            tab_list = window_1["tabs"]
            folder_date = tab_list[0]["lastAccessed"]

            # Start folder
            folder_header_str = (f"""    <DT><H3 ADD_DATE="{folder_date}" LAST_MODIFIED="{folder_date}">{folder_name}</H3>""" + 
                                 f"""    <DL><p>\n"""
                                )
            fh.write(folder_header_str)

            # Write folder contents
            for tab_idx, tab in enumerate(tab_list):
                logging.info(f'Reading info for tab {tab_idx}')
                # If tab was never loaded tab list will be empty
                if len(tab["entries"])==0:
                    url = tab["userTypedValue"]
                    tutle = url
                else:
                    webpage = tab["entries"][0]
                    url = webpage["url"]
                    if "title" in webpage.keys(): # Sometimes a webpage has no 'title' key
                        title = webpage["title"]
                    else:
                        title = url
                tab_string = f"""       <DT><A HREF="{url}" ADD_DATE="{folder_date}" LAST_MODIFIED="{folder_date}">{title}</A>\n"""
                fh.write(tab_string)

            # Close folder
            fh.write("""    </DL>\n""")

        # Write file footer
        fh.write("""</DL>""")

        fh.close()


@click.command()
@click.argument(
        'full_path',
        type=click.Path(exists=True)
)
# Main function
def main(full_path):
    # Configure logging
    logging.basicConfig(
        filename='session_manager_exporter.log',
        filemode='w',
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )
    root_dir = os.path.expanduser(full_path)
    logging.info(f'Searching for session data in {root_dir}')

    bm_dict_iter = []
    # Find all files in the requested directory
    filelist = None
    for folder_name, subfolders, filenames in os.walk(full_path):
        filelist = filenames
        break

    # Parse the .session files
    for filename in filelist:
        logging.info(f'Checking {filename}')
        if filename.endswith('.session') and not filename.startswith('backup'):
            logging.info(f'It is a Session Manager file')
            full_filepath = os.path.join(full_path, filename)
            bm_dict_iter.append(parse_file(full_filepath))
        else:
            logging.info(f'It NOT is a Session Manager file')
            

    # Write the session information onto a Firefox bookmakrs HTML file
    html_write(bm_dict_iter)


if __name__=='__main__':
    main()
