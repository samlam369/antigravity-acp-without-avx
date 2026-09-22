"""Load the pinned packaged frontend with a native Python interpreter."""
import os
from pathlib import Path
import runpy
import sys

runtime = Path(os.environ["AGY_RUNTIME_DIR"]).expanduser().resolve()
source = runtime / "native" / "src"
if not source.is_dir():
    raise SystemExit("Native frontend is missing; run scripts/prepare_runtime.py first.")
sys.path.insert(0, str(source))

# The official entrypoint applies this same compatibility shim. It must run
# before generated internal protobuf modules import the public runtime.
import google.protobuf.runtime_version
google.protobuf.runtime_version.ValidateProtobufRuntimeVersion = (
    lambda *args, **kwargs: None
)

# This is an option of Google's hermetic launcher, not the Python application.
# Remove only the exact empty option; preserve every other client argument.
sys.argv = [arg for arg in sys.argv if arg != "--uid="]
runpy.run_module(
    "google3.cloud.developer_experience.antigravity_extensions.acp_server.main",
    run_name="__main__",
)
