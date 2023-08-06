import datetime
import faulthandler
import os
import time
import traceback
import uuid

from azureml.contrib.services.aml_response import AMLResponse
from flask import g, request, Response
from werkzeug.exceptions import HTTPException

from .create_app import app
from .input_parsers import (
    BadInput,
    JsonStringInput,
    RawRequestInput,
    UnsupportedHTTPMethod,
    UnsupportedInput,
)
from .swagger import SwaggerException
from .user_script import TimedResult, UserScriptException, UserScriptTimeout

# Get (hopefully useful, but at least obvious) output from segfaults, etc.
faulthandler.enable()

HEADER_LIMIT = 100


def wrap_response(response):
    response_headers = {}
    response_body = response
    response_status_code = 200

    if isinstance(response, dict):
        if "aml_response_headers" in response:
            app.logger.info("aml_response_headers are available from run() output")
            response_body = None
            response_headers = response["aml_response_headers"]

        if "aml_response_body" in response:
            app.logger.info("aml_response_body is available from run() output")
            response_body = response["aml_response_body"]

    return AMLResponse(response_body, response_status_code, response_headers, json_str=True)


@app.route("/swagger.json", methods=["GET"])
def get_swagger_specification():
    g.api_name = "/swagger.json"
    version = request.args.get("version")

    # Setting default version where no query parameters passed
    if version is None:
        version = "2"

    try:
        swagger_json = app.swagger.get_swagger(version)
        return AMLResponse(swagger_json, 200, json_str=True)
    except SwaggerException as e:
        return AMLResponse(
            e.message,
            404,
            json_str=True,
        )


# Health probe endpoint
@app.route("/", methods=["GET"])
def health_probe():
    return "Healthy"


# Errors from Server Side
@app.errorhandler(HTTPException)
def handle_http_exception(ex: HTTPException):
    if 400 <= ex.code < 500:
        app.logger.debug("Client request exception caught")
    elif 500 <= ex.code < 600:
        app.logger.debug("Server side exception caught")
    else:
        app.logger.debug("Caught an HTTP exception")

    app.stop_hooks()
    return AMLResponse(ex.get_description(), ex.code, json_str=False)


# Unhandled Error
# catch all unhandled exceptions here and return the stack encountered in the response body
@app.errorhandler(Exception)
def all_unhandled_exception(error):
    app.stop_hooks()
    app.logger.debug("Unhandled exception generated")
    error_message = "Encountered Exception: {0}".format(traceback.format_exc())
    app.logger.error(error_message)
    internal_error = "An unexpected internal error occurred. {0}".format(error_message)
    return AMLResponse(internal_error, 500, json_str=False)


@app.before_request
def _before_request() -> None:
    g.api_name = None
    g.start_datetime = datetime.datetime.utcnow()
    g.starting_perf_counter = time.perf_counter()


@app.before_request
def _init_headers() -> None:
    legacy_request_id = request.headers.get("x-ms-request-id")
    request_id = request.headers.get("x-request-id", legacy_request_id)
    if not request_id:
        request_id = str(uuid.uuid4())
    if not legacy_request_id:
        legacy_request_id = request_id
    client_request_id = request.headers.get("x-client-request-id", "")

    # length of the headers is limited to 100
    if len(request_id) > HEADER_LIMIT or len(client_request_id) > HEADER_LIMIT:
        g.request_id = ""
        g.client_request_id = ""
        g.legacy_request_id = ""
        return AMLResponse(
            {"message": "header length of x-request-id or x-client-request-id exceeds 100 characters"},
            431,
            json_str=True,
        )

    g.legacy_request_id = legacy_request_id
    g.request_id = request_id
    g.client_request_id = client_request_id

    # If x-request-id and x-ms-request-id header values are differenet then it is a bad request
    if g.legacy_request_id and g.legacy_request_id != g.request_id:
        return AMLResponse(
            {
                "message": (
                    "x-request-id and x-ms-request-id header value should be same "
                    "(if you are sending both in the request)"
                )
            },
            400,
            json_str=True,
        )


@app.after_request
def populate_response_headers(response: Response) -> Response:
    server_ver = os.environ.get("HTTP_X_MS_SERVER_VERSION", "")
    if server_ver:
        response.headers.add("x-ms-server-version", server_ver)

    response.headers["x-ms-request-id"] = g.legacy_request_id
    response.headers["x-request-id"] = g.request_id

    if g.client_request_id:
        response.headers["x-client-request-id"] = g.client_request_id

    # Office services have their own tracing field 'TraceId', we need to support it.
    if "TraceId" in request.headers:
        response.headers.add("TraceId", request.headers["TraceId"])

    return response


# log all response status code after request is done
@app.after_request
def _after_request(response: Response) -> Response:
    if g.api_name:
        app.logger.info(response.status_code)

    # Log to app insights
    duration_ms = (g.starting_perf_counter - time.perf_counter()) * 1e3  # second to millisecond
    if request.path != "/":
        app.appinsights_client.log_request(
            request=request,
            response=response,
            start_datetime=g.start_datetime,
            duration_ms=duration_ms,
            request_id=g.request_id,
            client_request_id=g.client_request_id,
        )

    return response


def log_successful_request(timed_result: TimedResult):
    # This is ugly but we have to do this to maintain backwards compatibility. In the future we should simply log
    # `time_result.input` as-is.
    if isinstance(app.user_script.input_parser, (JsonStringInput, RawRequestInput)):
        # This logs the raw request (probably in its repr() form) if @rawhttp is used. We should consider not logging
        # this at all in the future.
        model_input = next(iter(timed_result.input.values()))
    else:
        model_input = timed_result.input

    app.appinsights_client.send_model_data_log(g.request_id, g.client_request_id, model_input, timed_result.output)


@app.route("/score", methods=["GET", "POST", "OPTIONS"], provide_automatic_options=False)
def handle_score():
    g.api_name = "/score"

    try:
        app.start_hooks(g.request_id)
        try:
            timed_result = app.user_script.invoke_run(request, timeout_ms=app.scoring_timeout_in_ms)
        finally:
            app.stop_hooks()
        log_successful_request(timed_result)
    except BadInput as ex:
        return AMLResponse({"message": ex.args[0]}, 400, json_str=True)
    except UnsupportedInput as ex:
        return AMLResponse({"message": ex.args[0]}, 415, json_str=True)
    except UnsupportedHTTPMethod:
        # return 200 response for OPTIONS call, if CORS is enabled the required headers are implicitly
        # added by flask-cors package
        if request.method == "OPTIONS":
            return AMLResponse("", 200)
        return AMLResponse("Method not allowed", 405, json_str=True)
    except UserScriptTimeout as ex:
        app.send_exception_to_app_insights(g.request_id, g.client_request_id)
        app.logger.debug("Run function timeout caught")
        app.logger.error("Encountered Exception: {0}".format(traceback.format_exc()))
        return AMLResponse(
            f"Scoring timeout after {ex.timeout_ms} ms",
            500,
            json_str=False,
            run_function_failed=True,
        )
    except UserScriptException as ex:
        app.send_exception_to_app_insights(g.request_id, g.client_request_id)
        app.logger.debug("Run function exception caught")
        app.logger.error("Encountered Exception: {0}".format(traceback.format_exc()))
        return AMLResponse(str(ex.user_ex), 500, json_str=False, run_function_failed=True)

    response = timed_result.output
    if isinstance(response, Response):  # this covers both AMLResponse and flask.Response
        app.logger.info("run() output is HTTP Response")
    else:
        response = wrap_response(response)

    # we're formatting time_taken_ms explicitly to get '0.012' and not '1.2e-2'
    response.headers.add("x-ms-run-fn-exec-ms", f"{timed_result.elapsed_ms:.3f}")
    return response
