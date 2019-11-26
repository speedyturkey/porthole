# Porthole

Porthole makes it easy to configure and build simple automated reports.

## Features

* Connect to and query a database.
* Convert query results into Excel workbooks
* Format Excel workbooks
* Send reports by email

## Getting Started

These instructions will allow you to install and configure your environment. You will be running your first reports after just a couple of steps:

1. Install Porthole.
2. Configure your database connection(s) and other important settings.
3. Run setup scripts (typically requires database write privileges).
4. Start creating reports.

#### Prerequisites

You must have first installed Python 3.6 or higher. It is recommended but not required to use an environment/package manager such as Anaconda. For more information, see the "Install Conda" section below. At the very least, if you are using a Mac, please do NOT use the "system" Python or any other flavor of Python 2.

You must also have access to a compatible database. This includes MySQL, PostgreSQL, Microsoft SQL Server, and SQLite. In order to take full advantage of Porthole's functionality, you will need to have CRUD privileges. See "Step 3 - Create database tables" below for more information.

Porthole is designed primarily for Linux and Mac. If you are using Windows, it is recommended that you enable and use Windows Subsystem for Linux (WSL).

### Step 1 - Install Porthole

Use pip to install Porthole from your command prompt or terminal:

`pip install porthole`

Porthole will be installed, along with its dependencies, using your default Python or whichever virtual environment you have chosen.

### Step 2 - Configuration

Create a config file by either copying and modifying `docs/sample_config.ini` or by following the steps below, which will create a blank template to work from.

From your terminal window, cd to your project directory. From the Python interpreter, execute the following:

```python
import porthole
porthole.new_config()
```

See `docs/config.md` for more information about the contents of the config file.

### Step 3 - Create database tables

Porthole uses several database tables for report definition and recipient management. To utilize Porthole's full functionality, it is necessary to create these tables before using the package. Note that you can create these tables in a dedicated reporting schema or database if you cannot or do not wish to create tables in the same schema or database as the data you are reporting on. Additionally, you can skip this section and use the lighter-weight `BasicReport` class, which does not require these dedicated tables.

Execute the following:

```python
import porthole
porthole.setup_tables()
```

This creates four tables in your database:

* automated_reports - Stores the reports you have defined. Reports must be uniquely identified by name and can be deactivated by setting the `active` attribute to 0.
* automated_report_contacts - Stores the names and email addresses of individuals who should receive reports.
* automated_report_recipients - This table facilitates the relationship between the previous two. It contains one record per report recipient. Recipients can be defined as 'to' or 'cc' recipients.
* report_logs - By default, reports will log their execution and results to this table (including error details).


### Step 4 - Create reports

Defining a new report involves adding records to the tables created in Step 3.

The following records are required:

| Table                       | Required Attributes                   | Optional Attributes   | Notes                                                                  |
|-----------------------------|---------------------------------------|-----------------------|------------------------------------------------------------------------|
| automated_reports           | report_name; active                   |                       |                                                                        |
| automated_report_contacts   | email_address                         | first_name; last_name |                                                                        |
| automated_report_recipients | report_id; contact_id; recipient_type |                       | Every report requires at least one record where recipient_type = 'to'. |

It's finally time to write an actual report! Here is a sample report script.

```python
from porthole import GenericReport

report = GenericReport(report_name='sample_report', report_title='Sample Report')
report.build_file()
report.create_worksheet_from_query(
    query={'filename': 'sample_query'},
    sheet_name='Sheet1'
)
report.subject = 'Sample Report'
report.message = 'Please see attached for the Sample Report.'
report.get_recipients()
report.execute()

```

## Running the tests

Execute the command `python run_tests.py`.


## Authors

* **Billy McMonagle** - *Maintainer* - [GitHub](https://github.com/speedyturkey)
* **Ed Nunes** - *Contributor* - [GitHub](https://github.com/nunie123)
* **Chase Hudson** - *Contributor* - [GitHub](https://github.com/Chase-H)
