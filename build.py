"""
Build tables needed to run basic version of package.
automated_reports
automated_report_contacts
automated_report_recipients
"""

from porthole import config
from porthole.models import metadata
from porthole.connections import ConnectionManager

def run():
    db = config['Default']['database']
    try:
        cm = ConnectionManager(db)
        cm.connect()
        metadata.create_all(cm.engine)
        print("Tables successfully created.")
    except:
        print("Failed to create tables.")

if __name__ == '__main__':
    run()
