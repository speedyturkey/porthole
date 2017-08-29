from .app import config
from .getting_started import new_config, setup_tables
from .connections import ConnectionManager
from .queries import QueryGenerator, QueryReader, QueryResult
from .xlsx import WorkbookBuilder
from .mailer import Mailer
from .workflows import SimpleWorkflow
from .related_record import RelatedRecord, ChildRecord
from .reports import BasicReport, GenericReport
from .filters import ResultFilter

# from flask import Flask
# gui_app = Flask('porthole')
# gui_app.config['SECRET_KEY'] = 'flarp'

# def run_gui():
#     gui_app.run(debug=False)
