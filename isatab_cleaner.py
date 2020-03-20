import os
import argparse
import tempfile
from zipfile import ZipFile
from io import BytesIO
from datetime import date


def clean_cr(line):
    """
    Removes carriage return characters from passed string or list of strings
    """
    if isinstance(line, list):
        return [e.split('\r')[0] for e in line]
    else:
        return line.split('\r')[0]

def read_investigation(path):
    """
    Returns the investigation CSV file from the passed ISA-Tab zip archive
    as a bstring
    """
    with ZipFile(path, 'r') as zip:
        with zip.open('i_Investigation.txt') as file:
            return file.read()

def clean_investigation(investigation):
    """
    Removes the defined items from the ISA-Tab investigation file and adds
    a 'last modified' notice to the comment in the first line
    """
    decoded = investigation.decode('utf-8').split('\n')

    # Parse lines into a dict so we can delete by element name
    elements_dict = {clean_cr(element[0]): clean_cr(element[1:]) for element in [line.split('\t') for line in decoded]}

    # Delete items
    if 'Comment[Subject Keywords]' in elements_dict:
        del elements_dict['Comment[Subject Keywords]']
    if 'Comment[Supplementary Information File Name]' in elements_dict:
        del elements_dict['Comment[Supplementary Information File Name]']
    if 'Comment[Supplementary Information File Type]' in elements_dict:
        del elements_dict['Comment[Supplementary Information File Type]']
    if 'Comment[Supplementary Information File URL]' in elements_dict:
        del elements_dict['Comment[Supplementary Information File URL]']
    
    # Rebuild the tab-delimited lines
    elements_list = []
    for k, v in elements_dict.items():
        line = []
        line.append(k)
        for el in v:
            line.append(el)
        elements_list.append('\t'.join(line))
    
    # Update the header comment
    elements_list[0] = elements_list[0] + ' - Last modified: {}'.format(
        str(date.today()))

    return '\n'.join(elements_list).encode('utf-8')

def save_updated_zip(out_dir, existing_path, filename, cleaned_inv, zip):
    """
    Create a new file in the specified path that contains the updated
    investigation file and all other files from the original ISA-Tab zip
    archive

    out_dir -- directory to place the output in
    existing_path -- path where the existing zip file is located
    filename -- filename of the existing zip file
    cleaned_inv -- updated investigation file to replace
    zip -- flag determining whether the output is zipped
    """

    # Create the ouput directory if it doesn't exist
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # If the zip flag is passed, zip the newly created ISA-Tab file
    if zip:
        # Create a temporary file to stage creation of the new output
        tmp_fd, tmp_filename = tempfile.mkstemp(dir=out_dir)
        os.close(tmp_fd)
        with ZipFile(os.path.join(existing_path, filename), 'r') as old_zip:
            with ZipFile(os.path.join(out_dir,tmp_filename), 'w') as tmp_zip:
                # Copy non-investigation files into the temp file
                for item in old_zip.infolist():
                    if item.filename != 'i_Investigation.txt':
                        tmp_zip.writestr(item, old_zip.read(item.filename))
                # Write the updated investigation file to the temp file        
                tmp_zip.writestr('i_Investigation.txt', cleaned_inv)
        
        # If the file already exists at that path delete it so we can overwrite it
        if os.path.exists(os.path.join(out_dir, filename)):
            os.remove(os.path.join(out_dir, filename))
        os.rename(os.path.join(out_dir, tmp_filename), os.path.join(out_dir, filename))

    # If not, just create a new directory with the filename and save it there
    else:
        new_path = os.path.join(out_dir, filename[:-4])
        if not os.path.exists(new_path):
            os.mkdir(new_path)

        with ZipFile(os.path.join(existing_path, filename), 'r') as existing_zip:
            for item in existing_zip.infolist():
                if item.filename != 'i_Investigation.txt':
                    with open(os.path.join(new_path, item.filename), 'wb') as f:
                        f.write(existing_zip.read(item.filename))
            with open(os.path.join(new_path, 'i_Investigation.txt'), 'wb') as f:
                f.write(cleaned_inv)

if __name__ == '__main__':
    # Set up the CLI argument parser
    parser = argparse.ArgumentParser(description=
        'Remove junk fields from Scientific Data ISA-Tab files and output updated files')
    parser.add_argument('path', help='ISA-Tab file or directory to clean')
    parser.add_argument('-o', '--output', help='output directory', 
        default='isatab_cleaner_output')
    parser.add_argument('-z', '--zip', action='store_true', 
        help='zip output ISA-Tab directories')
    args = parser.parse_args()

    if os.path.isdir(args.path):
        for filename in os.listdir(args.path):
            zippath = os.path.join(args.path, filename)
            investigation = read_investigation(zippath)
            cleaned = clean_investigation(investigation)
            save_updated_zip(args.output, args.path, filename, cleaned, args.zip)
    elif os.path.isfile(args.path):
        dirname, basename = os.path.split(args.path)
        investigation = read_investigation(args.path)
        cleaned = clean_investigation(investigation)
        save_updated_zip(args.output, dirname, basename, cleaned)
    else:
        print('An ISA-Tab file name or directory must be provided.')