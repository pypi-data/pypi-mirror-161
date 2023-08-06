# from context import BASEDIR
import os, json, time, argparse, shutil
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pdfform import config_win
from pdfform.application_form import ApplicationForm
from pdfform.form_controls_win import Skip
from pathlib import Path
from utils.utils import append_ext

# Get project's home directory,
BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# All data directory
DATADIR = os.path.abspath(os.path.join(BASEDIR, "data"))


def check_env():
    if not os.path.isfile(config_win.ACROBAT_READER_PATH):
        print("Acrobat reader not found. Please install it first.")
        exit()


def prepare_document(form_type: str, name: str, wait_time: int):
    """Create a new empty pdf file to fill"""

    # copy empty template file to output folder
    src = Path(DATADIR + f"/pdf/{form_type}.pdf")
    dst = Path(".").cwd() / f"{name}"
    shutil.copy2(src, dst)

    # open file with acrobat reader
    app = Application(backend="uia").start(
        str(config_win.ACROBAT_READER_PATH) + " " + str(dst)
    )
    # TODO: find better way to detect ready
    time.sleep(
        wait_time and int(wait_time) or 10
    )  # wait 10 seconds for file open finished.


def finish_document():
    """Validate, save and close document"""

    send_keys("^S")  # Ctrl + S to save
    send_keys("^W")  # Ctrl + W to close


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="PDF Filler -- automatically fill application forms.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("form_name", help="Input form name, for example: 1294")
    parser.add_argument("-j", "--json_name", help="Input json file name")
    parser.add_argument("-w", "--wait", help="wait time(seconds) for open pdf")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file name. ",
        metavar="output_file_name",
        default="test",
    )

    parser.add_argument(
        "-v", "--verbose", help="verbose output filling steps", action="store_true"
    )
    args = parser.parse_args()
    args.output = append_ext(args.json_name, ".pdf")
    args.json_name = append_ext(args.json_name, ".json")

    return args


def main():
    """main function"""

    args = get_args()
    form_name = args.form_name
    in_file = str(Path(args.json_name))
    verbose = args.verbose
    out_file = str(Path(".").cwd() / args.output)

    check_env()
    prepare_document(form_name, out_file, args.wait)

    # open actions data
    with open(in_file) as f:
        actions = json.load(f)

    form = ApplicationForm(verbose=verbose)

    for action in actions:
        form.add_step(action)

    form.fill_form(0, verbose=verbose)
    finish_document()


if __name__ == "__main__":
    main()
