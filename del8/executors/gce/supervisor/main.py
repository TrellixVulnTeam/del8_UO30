"""Main executable program for a GCE supervisor."""
import base64
import json
import os
import requests

from absl import app
from absl import flags
from absl import logging

from del8.core import serialization

FLAGS = flags.FLAGS

flags.DEFINE_string("gce_instance_name", None, "")
flags.DEFINE_string("zone", None, "")
flags.DEFINE_string("execution_items_base64", None, "")
flags.DEFINE_string("executor_params_base64", None, "")

flags.mark_flag_as_required("gce_instance_name")
flags.mark_flag_as_required("zone")
flags.mark_flag_as_required("execution_items_base64")
flags.mark_flag_as_required("executor_params_base64")


def kill_vm():
    logging.info("Killing GCE VM")
    # TODO: Rewrite to use subprocess.
    os.system(
        "gcloud compute instances delete --quiet "
        f"--zone='{FLAGS.zone}' '{FLAGS.gce_instance_name}'"
    )


# NOTE: There is probably a cleaner way to do this than a
# bunch of nested contexts and loops. Also maybe try seeing
# if some light server framework could be used.
def main(_):
    try:
        exe_items = base64.b64decode(
            FLAGS.execution_items_base64.encode("utf-8")
        ).decode("utf-8")
        exe_params = base64.b64decode(
            FLAGS.executor_params_base64.encode("utf-8")
        ).decode("utf-8")

        exe_items = serialization.deserialize(exe_items)
        exe_params = serialization.deserialize(exe_params)

        supervisor = exe_params.create_supervisor()

        supervisor.run(exe_items)
    finally:
        kill_vm()


if __name__ == "__main__":
    app.run(main)
