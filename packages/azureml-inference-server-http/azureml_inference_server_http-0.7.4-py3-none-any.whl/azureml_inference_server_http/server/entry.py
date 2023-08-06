import os
import sys


debug_port = os.getenv("AZUREML_DEBUG_PORT")
if debug_port:
    print("!! Starting the inference server in DEBUGGING mode because AZUREML_DEBUG_PORT is set.")
    print("!! This environment variable should not be set in a production environment.")

    try:
        debug_port = int(debug_port)
    except ValueError:
        print(f"** Debug port must be an integer: {debug_port}")
        sys.exit(-1)

    try:
        import debugpy
    except ModuleNotFoundError:
        print("** Cannot connect to a debugger because debugpy is not installed.")
        sys.exit(-1)

    print(f"** Connecting to debugger at port {debug_port}...")
    debugpy.connect(debug_port)
    debugpy.wait_for_client()


from .create_app import create  # noqa: E402

app = create()
