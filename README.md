# Porthole

Porthole allows you to configure and build simple automated reports.

## Features

* Easily connect to and query a database.
* Convert query results into Excel workbooks
* Send reports by email

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

##### Install Conda

Anaconda (commonly shortened to "Conda") is a widely used environment and package manager for Python. Among other useful features, it makes it easy to setup and install prerequisite Python packages (that is, to setup and configure a development environment). It is recommended to install "Miniconda", which installs only the required packages.

###### OS X Installation Instructions

Full instructions can be found here: [https://conda.io](https://conda.io/docs/install/quick.html).

1. Open a terminal session (go to spotlight, type ‘terminal’ and hit enter).
2. Download the 64-bit bash installer for OS X. Make sure to select Python 3.6.
3. Either move the download to your login directory or cd into your Downloads folder.
  * If you don’t know what your login directory is, type the command `cd` followed by `pwd`.
  * If instead you want to cd into your Downloads folder, use the command `cd ~/Downloads`.
4. Enter the following command: `bash Miniconda3-latest-MacOSX-x86_64.sh`
5. Follow the on-screen instructions. Note that you will have to hold the Enter key in order to scroll through the EULA.
6. The installer will ask you where miniconda should be installed, defaulting to your home directory - type “yes” to confirm.
7. The installer will ask whether you’d like to add your selected directory to your bash profile PATH - type “yes” to confirm.

###### Windows Installation Instructions

Coming soon.


##### Create virtual environment

After Conda is installed, use it to create a virtual environment. The required packages (dependencies) are defined in the environment.yml file. Execute the following command from the terminal:

`conda env create -f environment.yml`

To activate your new environment, execute the following command:

`source activate porthole`

### Installing

##### Setup Config

Make a copy of example.ini and rename it as config.ini. The values defined in this file will be used for any connections you'll make to databases, email servers, and to your file system. The values defined in this section are required for correct functionality.

###### Default

Required values:
* base_file_path - The default location for saving files. You must define the full, absolute path. The path must include a trailing slash.
* query_path - The default location for reading .sql files. This path should be relative to your project directory. THe path must include a trailing slash.
* database - The name of the default database connection you'd like to use.

###### Database Connections

Since any database connection requires several parameters, database configs are defined as their own sections. The parameters required in a given section depend on which RDBMS is being defined. The full list of parameters is as follows:

* rdbms - The type of RDBMS. Currently supported options include mysql and sqlite.
* host - The connection string or endpoint. For sqlite, this is the database file name.
* port - Usually defaults to 3306 for mysql. Not used for sqlite but set to 0 by default.
* user - The account name for the database user.
* password - The user's password.
* schema - The default schema or database name.

##### Create database tables

Porthole uses several database tables for report definition and recipient management. It is therefore necessary to create these tables before using the package. Be sure to setup your virtual environment and config file before creating database tables.

Execute the command `python setup.py`.

## Running the tests

Execute the command `python run_tests.py`.


## Authors

* **Billy McMonagle** - *Initial work* - [GitHub](https://github.com/speedyturkey)
