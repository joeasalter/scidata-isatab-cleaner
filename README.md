# scidata-isatab-cleaner
A basic command line tool used to remove unwanted elements from Scientific Data's ISA-Tab files prior to archiving.

## Usage
```
isatab_cleaner.py [-h] [-o OUTPUT] [-z] path

positional arguments:
  path                  ISA-Tab file or directory to clean

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output directory
  -z, --zip             zip output ISA-Tab directories
```

### Args
* **path** - Path to the file or directory of files to be cleaned.
* **-o --output** - Defines the directory to output the cleaned files into. Defaults to ```isatab_cleaner_output``` in the current directory if not provided.
* **-z --zip** - If passed zips each output cleaned ISA-Tab directory.

## License
This project is licensed under the MIT License.