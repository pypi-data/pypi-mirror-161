from .handlers import RouteHandler
from jupyter_server.extension.application import ExtensionApp
import pprint

class ETCJupyterLabNotebookStateProviderApp(ExtensionApp):

    name = "etc_jupyterlab_notebook_state_provider"

    def initialize_settings(self):
        try:
            self.log.info(f"ETCJupyterLabNotebookStateProviderApp.config {pprint.pformat(self.config)}")
        except Exception as e:
            self.log.error(str(e))

    def initialize_handlers(self):
        try:
            self.handlers.extend([(r"/etc-jupyterlab-notebook-state-provider/(.*)", RouteHandler)])
        except Exception as e:
            self.log.error(str(e))
            raise e

