import itertools
import logging
import os
import sys
import traceback

from flask import Flask

from .aml_logger import AMLLogger
from .appinsights_client import AppInsightsClient
from .print_hook import PrintHook
from .swagger import Swagger
from .user_script import UserScript, UserScriptError
from .utils import walk_path
from ..constants import ENV_AZUREML_MODEL_DIR

# check if flask_cors is available
try:
    import flask_cors
except ModuleNotFoundError:
    flask_cors = None

AML_APP_ROOT = os.environ.get("AML_APP_ROOT", "/var/azureml-app")
AML_SERVER_ROOT = os.environ.get("AML_SERVER_ROOT", os.path.dirname(os.path.realpath(__file__)))
AML_ENTRY_SCRIPT = os.environ.get("AZUREML_ENTRY_SCRIPT")
AML_SOURCE_DIR = os.environ.get("AZUREML_SOURCE_DIRECTORY")
FILE_TREE_LOG_LINE_LIMIT = 200

# Amount of time we wait before exiting the application when errors occur for exception log sending
WAIT_EXCEPTION_UPLOAD_IN_SECONDS = 30
SCORING_TIMEOUT_ENV_VARIABLE = "SCORING_TIMEOUT_MS"

sys.path.append(AML_APP_ROOT)

if AML_SOURCE_DIR:
    source_dir = os.path.join(AML_APP_ROOT, AML_SOURCE_DIR)
    sys.path.append(source_dir)


class AMLInferenceApp(Flask):
    appinsights_client: AppInsightsClient
    logger: AMLLogger

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user_script = UserScript(AML_ENTRY_SCRIPT)
        self.scoring_timeout_in_ms = 3600 * 1000

        self._stdout_hook = None
        self._stderr_hook = None

    def _init_logger(self):
        try:
            print("Initializing logger")
            self.logger = AMLLogger()

            logging.getLogger("gunicorn.access").addFilter(lambda record: "GET / HTTP/1." not in record.getMessage())
        except Exception:
            print("logger initialization failed: {0}".format(traceback.format_exc()))
            sys.exit(3)

    # AML App Insights Wrapper
    def _init_appinsights(self):
        try:
            self.logger.info("Starting up app insights client")
            self.appinsights_client = AppInsightsClient()
            self._stdout_hook = PrintHook(PrintHook.stdout_fd)
            self._stderr_hook = PrintHook(PrintHook.stderr_fd)
        except Exception:
            self.logger.error(
                "Encountered exception while initializing App Insights/Logger {0}".format(traceback.format_exc())
            )
            sys.exit(3)

    def send_exception_to_app_insights(self, request_id="NoRequestId", client_request_id=""):
        if self.appinsights_client is not None:
            self.appinsights_client.send_exception_log(sys.exc_info(), request_id, client_request_id)

    # The default prefix of zeros acts as default request id
    def start_hooks(self, prefix="00000000-0000-0000-0000-000000000000"):
        try:
            if self._stdout_hook is not None:
                self._stdout_hook.start_hook(prefix)
            if self._stderr_hook is not None:
                self._stderr_hook.start_hook(prefix)
        except Exception:
            pass

    def stop_hooks(self):
        try:
            if self._stdout_hook is not None:
                self._stdout_hook.stop_hook()
            if self._stderr_hook is not None:
                self._stderr_hook.stop_hook()
        except Exception:
            pass

    def setup(self):
        # initiliaze logger and app insights
        self._init_logger()
        self._init_appinsights()

        # Enable CORS if the environemnt variable is set
        if os.getenv("AML_CORS_ORIGINS"):
            if flask_cors:
                origins = os.getenv("AML_CORS_ORIGINS")
                originsList = [origin.strip() for origin in origins.split(",")]
                flask_cors.CORS(self, methods=["GET", "POST"], origins=originsList)
                self.logger.info(f"Enabling CORS for the following origins: {', '.join(originsList)}")
            # if flask_cors package is not available and environ variable is set then log appropriate message
            else:
                self.logger.info(
                    "CORS cannot be enabled because the flask-cors package is not installed. The issue can be"
                    " resolved by adding flask-cors to your pip dependencies."
                )

        # start the hooks to listen to init print events
        try:
            self.logger.info("Starting up app insight hooks")
            self.start_hooks()
        except Exception:
            self.logger.error("Starting up app insight hooks failed")
            if self.appinsights_client is not None:
                self.appinsights_client.send_exception_log(sys.exc_info())
                self.appinsights_client.wait_for_upload()
            sys.exit(3)

        try:
            self.user_script.load_script(AML_APP_ROOT)
        except UserScriptError:
            # If main is not found, this indicates score script is not in expected location
            if "No module named 'main'" in traceback.format_exc():
                self.logger.error("No score script found. Expected score script main.py.")
                self.logger.error(f"Expected script to be found in PYTHONPATH: {sys.path}")
                if os.path.isdir(AML_APP_ROOT):
                    self.logger.error(f"Current contents of AML_APP_ROOT: {os.listdir(AML_APP_ROOT)}")
                else:
                    self.logger.error(f"The directory {AML_APP_ROOT} not an accessible directory in the container.")

            self.logger.error(traceback.format_exc())
            sys.exit(3)

        try:
            self.user_script.invoke_init()
        except UserScriptError:
            self.logger.error("User's init function failed")
            self.logger.error("Encountered Exception {0}".format(traceback.format_exc()))
            self.appinsights_client.send_exception_log(sys.exc_info())

            aml_model_dir = os.environ.get(ENV_AZUREML_MODEL_DIR)
            if aml_model_dir and os.path.exists(aml_model_dir):
                self.logger.info("Model Directory Contents:")

                tree = walk_path(aml_model_dir)
                for line in itertools.islice(tree, FILE_TREE_LOG_LINE_LIMIT):
                    self.logger.info(line)

                if next(tree, None):
                    self.logger.info(f"Output Truncated. First {FILE_TREE_LOG_LINE_LIMIT} lines shown.")

            self.appinsights_client.wait_for_upload()

            sys.exit(3)

        self.stop_hooks()

        # init debug middlewares deprecated
        if "AML_DBG_MODEL_INFO" in os.environ or "AML_DBG_RESOURCE_INFO" in os.environ:
            self.logger.warning(
                "The debuggability features have been removed. If you have a use case for them please reach out to us."
            )

        # generate the swagger
        self.swagger = Swagger(AML_APP_ROOT, AML_SERVER_ROOT, self.user_script)

        if SCORING_TIMEOUT_ENV_VARIABLE in os.environ.keys() and self.is_int(os.environ[SCORING_TIMEOUT_ENV_VARIABLE]):
            self.scoring_timeout_in_ms = int(os.environ[SCORING_TIMEOUT_ENV_VARIABLE])
            self.logger.info("Scoring timeout is found from os.environ: {} ms".format(self.scoring_timeout_in_ms))
        else:
            self.logger.info(
                "Scoring timeout setting is not found. Use default timeout: {} ms".format(self.scoring_timeout_in_ms)
            )

    @staticmethod
    def is_int(value):
        try:
            int(value)
            return True
        except ValueError:
            return False
