# Py7za ("pizza")

Python wrapper for running the 7za.exe utility from https://www.7-zip.org/

The wrapper simply runs the application in a separate process and added functionality primarily aimed at running the tool in several parallel processes from the command-line.

Other than providing that utility, the wrapper tries to provide users Python API access to 7za in a way as simple, and as close to the original as possible. See some documentation for the command line options here https://sevenzip.osdn.jp/chm/cmdline/index.htm (no affiliation).

Additionally, the package contains the generic `AsyncIOPool` class, which allows you to queue up a large number of asynchronous tasks, and it will keep a certain number of them running at all times, until all tasks are done. This works for any `asyncio` `Task`, but can be handily combined with the `Py7za` class.

Finally, a command line utility `py7za-box` ("pizza box", and its aliases `box` and `unbox`) is included, which allows you to quickly replace individual files with their zipped equivalent in-place and vice versa, without writing any code. The idea is that a user may want to zip many files in a large project, without removing them from their original location, and still be able to find them by name and easily extract them individually.

For more information, check the [Py7za documentation at Read the Docs (py7za.readthedocs.io)](https://py7za.readthedocs.io).

## Install

Install the package for use from scripts:
```commandline
pip install py7za
```

Of if you want to use the command-line interface `py7za-box` as well, make sure the dependencies for it are installed like this: 
```commandline
pip install py7za[box]
py7za-box --help
box --help
unbox --help
```

On Linux, you will have to have `p7zip` installed for `py7za` to work, as there is no Linux binary included in the package. For example:
```commandline
sudo yum install -y p7zip
sudo apt-get install -y p7zip
```

### Command line py7za-box

To quickly replace every .csv file in a directory and in all its subdirectories with a zip-file containing that .csv:
```commandline
py7za-box **/*.csv
```

And the reverse:
```commandline
py7za-box **/*.csv.zip --unbox
```

More in the documentation https://py7za.readthedocs.io

## Dependencies

The only external dependency is on `conffu` for the configuration of the command-line tool. If you only want to use the Py7za class, and just use `pip install py7za`, this dependency won't be installed. To install the dependency, use `pip install py7za[box]`.

## License

This package is licensed under the MIT license. See [LICENSE.txt](https://gitlab.com/Jaap.vanderVelde/py7za/-/blob/master/LICENSE.txt).

## Changelog

See [CHANGELOG.md](https://gitlab.com/Jaap.vanderVelde/py7za/-/blob/master/CHANGELOG.md).
