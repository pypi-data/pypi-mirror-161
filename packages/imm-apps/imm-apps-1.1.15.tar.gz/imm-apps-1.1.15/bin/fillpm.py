import json, os, shutil
from mailbox import MMDFMessage
import time
import subprocess

import context
from pdfform import config_mac as config
from pdfform.application_form_mac import ApplicationForm


# Get project's home directory,
BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# All data directory
DATADIR = os.path.abspath(os.path.join(BASEDIR, "data"))


def check_env():
    # if not os.path.isfile(config.ACROBAT_READER_PATH):
    #     print("Acrobat reader not found. Please install it first.")
    #     exit()
    if not os.path.isdir(config.OUTPUT_PATH):
        print("Output directory doesn't exist. Please check.")
        exit()


def prepare_document():
    """Create a new empty pdf file to fill"""

    # copy empty template file to output folder
    # src = DATADIR + f"/pdf/imm5708.pdf"
    dst = config.OUTPUT_PATH + "imm1295e.pdf"
    # shutil.copy2(src, dst)

    subprocess.call(["/usr/bin/open", dst])
    time.sleep(3)  # wait 5 seconds for file open finished.


def main():
    check_env()
    prepare_document()
    with open("/Users/jacky/desktop/1295.json") as f:
        actions = json.load(f)
    form = ApplicationForm(None)
    for action in actions:
        form.add_step(action)
    form.fill_form(start=0, verbose=True)


if __name__ == "__main__":
    main()
