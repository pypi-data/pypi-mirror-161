from distutils.version import LooseVersion
import functools
import os
import traceback
import warnings

import flask
import werkzeug
import werkzeug.datastructures

from .aml_blueprint import AMLInferenceApp


app = AMLInferenceApp(__name__)
app.setup()


def patch_flask():
    # While "packaging" is the recommended package for comparing versions, we can't introduce the dependency because
    # we need our server to work even when the user doesn't have latest dependencies installed.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            action="ignore",
            category=DeprecationWarning,
            message="distutils Version classes are deprecated.",
        )
        patch_werkzeug = LooseVersion(werkzeug.__version__) >= LooseVersion("2.1")

    if patch_werkzeug:
        # Request.headers.has_key() was removed in werkzeug 2.1
        # https://github.com/pallets/werkzeug/commit/03979aaff2b8020fd6fd52e69745950d484e3fa5
        # Restore the functionality to preserve backwards compatability.
        werkzeug.datastructures.EnvironHeaders.has_key = werkzeug.datastructures.EnvironHeaders.__contains__
        werkzeug.datastructures.CombinedMultiDict.has_key = werkzeug.datastructures.CombinedMultiDict.__contains__

        # In werkzeug 2.1, get_json() is modified to throw BadRequest if the content type is not application/json.
        @functools.wraps(flask.Request.on_json_loading_failed)
        def on_json_loading_failed(self, e):
            if e is None:
                return None

            return on_json_loading_failed.__wrapped__(self, e)

        flask.Request.on_json_loading_failed = on_json_loading_failed
        app.logger.info("AML_FLASK_ONE_COMPATIBILITY is set. Patched Flask to ensure compatibility with Flask 1.")
    else:
        app.logger.info("AML_FLASK_ONE_COMPATIBILITY is set, but patching is not necessary.")


if os.environ.get("AML_FLASK_ONE_COMPATIBILITY", "true").lower() == "true":
    try:
        patch_flask()
    except Exception:
        app.logger.warning(
            "AML_FLASK_ONE_COMPATIBILITY is set. However, compatibility patch for Flask 1 has failed. "
            "This is only a problem if you use @rawhttp and relies on deprecated methods such as has_key().\n"
            + traceback.format_exc()
        )


def create():
    # Import routes to bind the routes to app. We will need to move away from the create_app design pattern as it
    # is for blueprints and not suitable if we're going to use app directly.
    from . import routes  # noqa: F401

    return app


if __name__ == "__main__":
    app = create()
    app.run(host="0.0.0.0", port=31311)
