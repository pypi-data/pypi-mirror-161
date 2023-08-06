# import context
from pathlib import Path
import argparse, json
from model.experience.resume import ResumeModel
from utils.utils import append_ext
from tabulate import tabulate
from os.path import exists
from model.common.wordmaker import WordMaker
import os
from bin.models import get_models
from bin.config import Config

# make sure term color works both in mac and windwos
from termcolor import colored
import colorama

colorama.init()

# Get project's home directory,
BASEDIR = Path(__file__).parents[1]
# All data directory
DATADIR = BASEDIR / "data"


def add_ext(args):
    if args.excel:
        args.excel = append_ext(args.excel, ".xlsx")
    if args.make:
        args.make = append_ext(args.make, ".xlsx")
    if args.check:
        args.check = append_ext(args.check, ".xlsx")
    if args.word:
        args.word = append_ext(args.word, ".docx")
    if args.webform:
        args.webform = append_ext(args.webform, ".json")
    if args.pdfform:
        args.pdfform = append_ext(args.pdfform, ".json")

    args.template_num = args.template_num or 1
    return args


def getArgs():
    parser = argparse.ArgumentParser(
        description="used for making excel based on model or checking excel data according to the model"
    )
    parser.add_argument("model", help="input program code,such as 0008 5669 5562 5406 ")
    parser.add_argument("-m", "--make", help="input excel file name for output")
    parser.add_argument("-c", "--check", help="input excel file name to check")
    parser.add_argument(
        "-e",
        "--excel",
        help="input excel file name as data source for generating docx/josn file",
    )

    parser.add_argument(
        "-wf", "--webform", help="input webform josn file name for output"
    )
    parser.add_argument(
        "-pf", "--pdfform", help="input pdf form josn file name for output"
    )
    # for word. 2 args -d and -w
    parser.add_argument(
        "-d", "--document", help="input document flag to generate related docx"
    )
    parser.add_argument("-w", "--word", help="input word file name for output")
    parser.add_argument(
        "-tn", "--template_num", help="input template number for using templates"
    )
    parser.add_argument("-u", "--upload_dir", help="input upload directory")
    parser.add_argument(
        "-r",
        "--rcic",
        help="input rcic name",
    )
    parser.add_argument(
        "-rc",
        "--rcic_company_id_name",
        help="input rep's company short name for generating some customized docs",
    )

    parser.add_argument("-j", "--json", help="output json data", action="store_true")
    parser.add_argument("-i", "--initial", help="BCPNP initial registration or application", action="store_true")
    parser.add_argument("-p", "--previous", help="BCPNP has previous applicaton", action="store_true")

    args = parser.parse_args()
    args.rcic_company_id_name = args.rcic_company_id_name or Config.rcic_company_id_name
    args = add_ext(args)
    return args


def getHelp(valid_models):
    contents = [["Model",  "Word Template","Description"]]
    for model, value in valid_models.items():
        word_template = value.get("docx_template")
        if word_template:
            temp_name = ", ".join(word_template)
        else:
            temp_name = "NA"
        contents.append([model, os.path.basename(temp_name), value["remark"]])
    print(
        colored(
            "Every model can do two things. 1. -m make excel document 2. -c check excel content based on the model\nFor specific help, enter mmc model_name to get the model's details.",
            "green",
        )
    )
    print(tabulate(contents, tablefmt="fancy_grid"))
    return


def getModelHelp(valid_models, key):
    help = valid_models.get(key).get("help")
    if help:
        print(colored(f"{help.get('description')}", "green"))
        print(tabulate(help.get("helps"), tablefmt="fancy_grid"))
    else:
        print(colored("There is no help info provided yet.", "red"))


def makeExcel(args, the_model):
    file_exists = exists(args.make)
    if file_exists:
        print(colored(f"{args.make} is existed, overwrite?(Y/N)", "red"))
        overwrite = input()
        if overwrite and overwrite.upper()[0] == "N":
            return
    # create excel
    the_model(output_excel_file=args.make)
    print(colored(f"{args.make} has been created", "green"))


def checkModel(args, the_model):
    model_obj = the_model(excels=[args.check])
    if model_obj.dict() != {}:
        print(
            json.dumps(model_obj.dict(), indent=3, default=str)
        ) if args.json else print(
            colored(f"The model has been checked and everything seems good...", "green")
        )

def makeWord(args, model, the_model):
    word_file_exists = exists(args.word)
    excel_file_exists = exists(args.excel)
    if word_file_exists:
        print(colored(f"{args.word} is existed, overwrite?(Y/N)", "red"))
        overwrite = input()
        if overwrite and overwrite.upper()[0] == "N":
            return
    if not excel_file_exists:
        print(colored(f"{args.excel} is not existed."))
        return

    template_docx_dict = model.get("docx_template")
    if not template_docx_dict:
        print(
            colored(
                f"There is no template existing in model {model.get('class_list')[0]}",
                "red",
            )
        )
        return
    
    # if there  is no args.document, which means the model has only one  default  dict element
    def getOnlyOneTemplate():
        the_only_one_temp=list(template_docx_dict.keys())
        temp_number=len(the_only_one_temp)
        if temp_number==1:
            return template_docx_dict.get(the_only_one_temp[0])
        elif temp_number>1:
            raise ValueError("Word templates more than one in the model, but you did not give -d option")
        else:
            return  None
     
    # if with args.document, get the specific template, or  without args.document, get the only one
    template_docx = template_docx_dict.get(args.document) if args.document else getOnlyOneTemplate()
    if not exists(template_docx):
        print(
            colored(
                f"{template_docx} is not existed. Please check your template base",
                "red",
            )
        )
        return

    model = the_model(excels=[args.excel])
    context = model.context(doc_type=args.document)
    wm = WordMaker(template_docx, context, args.word)
    wm.make()


def makeWebform(args, the_model):
    if not args.upload_dir:
        print(
            colored(
                "You did not input uploading directory. Without it , the files in current folder will be uploaded.",
                "yellow",
            )
        )
    key_args = {
        "output_json": args.webform,
        "upload_dir": args.upload_dir or ".",
        "rcic": args.rcic or Config.rcic,
        "initial":args.initial or True,
        "previous":args.previous or False
    }
    app = the_model(excels=[args.excel])
    app.make_web_form(**key_args)


def makePdfform(args, the_model):
    key_args = {"output_json": args.pdfform, "rcic_id_name": args.rcic or Config.rcic}
    app = the_model(excels=[args.excel])
    app.make_pdf_form(**key_args)


def main():
    args = getArgs()
    models = get_models(
        rcic_company_id_name=args.rcic_company_id_name, temp_num=args.template_num
    )
    if args.model.upper() == "HELP":
        getHelp(models)
        return

    checkArgs(args, models)

    # get model, and its instance
    model = models.get(args.model)
    class_list = model["class_list"]
    the_class = __import__(model["path"], fromlist=class_list)
    the_model = getattr(the_class, class_list[0])

    # Make excel based on model
    if args.make:
        makeExcel(args, the_model)
        return

    # Make document based on model and source excel data
    if args.excel and args.word:
        makeWord(args, model, the_model)
        return

    # Generate json file based on model and source excel data for web form
    if args.excel and args.webform:
        makeWebform(args, the_model)
        return

    # Generate json file based on model and source excel data for pdf form
    if args.excel and args.pdfform:
        makePdfform(args, the_model)
        return

    # Check model, output error list or excel file, and generate json output if model is correct and required
    if args.check:
        checkModel(args, the_model)
        return

    # if  only model after modelcheck, then show the specific help info for the model
    if args.model:
        getModelHelp(models, args.model)
        return


def checkArgs(args, valid_models):
    if not args.model:
        print(colored("You must input model!", "red"))
        exit(1)

    if not valid_models.get(args.model):
        print(colored(f"Model ({args.model}) is not existed. Please check.", "red"))
        exit(1)

    if args.excel and not os.path.exists(args.excel):
        print(colored(f"{args.excel} is not existed", "red"))
        exit(1)

    if args.upload_dir and not os.path.exists(args.upload_dir):
        print(colored(f"The path {args.upload_dir} is not existed", "red"))
        exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(colored(str(e), "red"))
