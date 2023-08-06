# import context
from pathlib import Path
import typer, json
from utils.utils import append_ext, remove_ext
from bin.models import get_models
from rich.console import Console
from rich.text import Text
from rich.table import Table
from tabulate import tabulate
from termcolor import colored
from model.common.wordmaker import WordMaker
from bin.config import Config
from utils.utils import makeTable

# Get project's home directory,
BASEDIR = Path(__file__).parents[1]
# All data directory
DATADIR = BASEDIR / "data"

app = typer.Typer()
console = Console()


def show_exception(e: Exception):
    console.print(e, style="red")


def show_error(e):
    console.print(e, style="red")


def show_warning(msg: str):
    console.print(msg, style="yellow")


def getModel(model_name: str):
    # get model, and its instance
    models = get_models(rcic_company_id_name="", temp_num=1)
    model = models.get(model_name)
    if not model:
        show_error(f"{model_name} is not a valid model name.")
        exit(1)
    class_list = model["class_list"]
    the_class = __import__(model["path"], fromlist=class_list)
    the_model = getattr(the_class, class_list[0])
    return the_model


@app.command()
def man(model: str = typer.Argument(None, help="A model name, such as 5708")):
    """Manual of imm app"""
    models = get_models(rcic_company_id_name="", temp_num=1)
    # give specific manu for a model
    if model:
        if model not in models:
            show_error(
                f"{model} is not valid in defined models. Please use 'imm man' to check all models"
            )
            return
        help = models.get(model).get("help")
        if help:
            # print(f"{help.get('description')}")
            # print(tabulate(help.get("helps"), tablefmt="fancy_grid"))
            table = makeTable(f"Help for model {model}", help.get("helps"))
            console.print(table)

        else:
            print("There is no help info provided yet.")
    else:

        table = Table(title="Models List")
        table.add_column("Model", justify="left", style="cyan", no_wrap=True)
        table.add_column("Word", style="magenta")
        table.add_column("Pdf Form", style="magenta")
        table.add_column("Web Form ", style="magenta")
        table.add_column("Description", justify="left", style="green")

        contents = []
        for model, value in models.items():
            word_template = value.get("docx_template")
            pdf_function = value.get("pdf_function")
            web_function = value.get("web_function")
            if word_template:
                temp_name = ", ".join(word_template)
            else:
                temp_name = ""
            contents.append(
                [
                    model,
                    Path(temp_name).name,
                    pdf_function,
                    web_function,
                    value["remark"],
                ]
            )
        print(
            "Every model can do two things. 1. -m make excel document 2. -c check excel content based on the model\nFor specific help, enter mmc model_name to get the model's details.",
        )
        for content in contents:
            table.add_row(*content)

        console.print(table)


@app.command()
def make(model: str, output_excel_name: str):
    """Make excel based on model"""
    output_excel_name = append_ext(output_excel_name, ".xlsx")
    file_exists = Path(output_excel_name).exists()
    if file_exists:
        overwrite = typer.confirm(f"{output_excel_name} is existed, overwrite?")
        if not overwrite:
            return
    # create excel
    the_model = getModel(model)
    the_model(output_excel_file=output_excel_name)
    print(colored(f"{output_excel_name} has been created", "green"))


@app.command()
def check(model: str, excel_name: str, print_json: bool = False):
    """Check input excel based on model"""
    excel_name = append_ext(excel_name, ".xlsx")
    the_model = getModel(model)
    model_obj = the_model(excels=[excel_name])
    if model_obj.dict() != {}:
        print(
            json.dumps(model_obj.dict(), indent=3, default=str)
        ) if print_json else print(
            colored(f"The model has been checked and everything seems good...", "green")
        )


@app.command()
def word(
    model: str,
    excel_name: str,
    word_name: str = typer.Argument(
        None,
        help="Output word name. If none, willl use excel's name without ext, plus .docx",
    ),
    doctype: str = typer.Argument(
        None,
        help="Which document to generate, such as sl, ert,eet,... Use 'imm man' to check word column for details",
    ),
    rciccompany: str = typer.Option(
        "noah", help="Rcic company short name defined in docx templates"
    ),
    tempnum: int = typer.Option(1, help="template number"),
):
    """Make word based on model and input excel"""
    # check
    excel_name = append_ext(excel_name, ".xlsx")
    if word_name:
        word_name = append_ext(word_name, ".docx")
    else:
        word_name = remove_ext(excel_name) + ".docx"

    word_file_exists = Path(word_name).exists()
    excel_file_exists = Path(excel_name).exists()

    if not excel_file_exists:
        print(colored(f"{excel_name} is not existed."))
        return

    if word_file_exists:
        overwrite = typer.confirm(f"{word_name} is existed, overwrite?")
        if not overwrite:
            return

    models = get_models(rcic_company_id_name=rciccompany, temp_num=tempnum)
    template_docx_dict = models.get(model).get("docx_template")
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
        the_only_one_temp = list(template_docx_dict.keys())
        temp_number = len(the_only_one_temp)
        if temp_number == 1:
            return template_docx_dict.get(the_only_one_temp[0])
        elif temp_number > 1:
            raise ValueError(
                "Word templates more than one in the model, but you did not input the doc type abbreviation"
            )
        else:
            return None

    # get model class
    try:
        # if with doc type , get the specific template, or  without args.document, get the only one
        template_docx = (
            template_docx_dict.get(doctype) if doctype else getOnlyOneTemplate()
        )
        if not template_docx:
            raise ValueError(
                f"{doctype} is not a valid document type, please check the manual by typing:'imm man'to see valid word template for each model"
            )
        elif not Path(template_docx).exists():
            raise FileNotFoundError(
                f"{template_docx} is not existed. Please check your template base"
            )

        the_model = getModel(model)
        model_instance = the_model(excels=[excel_name])
        context = model_instance.context(doc_type=doctype)
        wm = WordMaker(template_docx, context, word_name)
        wm.make()
    except Exception as e:
        show_exception(e)


@app.command()
def webform(
    model: str,
    excel_name: str,
    outputjson: str = typer.Argument(
        None,
        help="Output json file name. Without input, excel's name will be used  by adding '.json'",
    ),
    rcic: str = typer.Option(Config.rcic, help="RCIC's short name"),
    initial: bool = typer.Option(
        True, help="Is this for starting a new case. Only used for BCPNP webform."
    ),
    previous: bool = typer.Option(
        False, help="Does this client have previous BCPNP application?"
    ),
    uploaddir: str = typer.Option(
        ".", help="A directory in which all files will be uploaded."
    ),
):
    """Make json file based on model and input excel for webform filling"""
    excel_name = append_ext(excel_name, ".xlsx")
    if outputjson:
        outputjson = append_ext(outputjson, ".json")
    else:
        outputjson = remove_ext(excel_name) + ".json"
    if not uploaddir:
        show_warning(
            "You did not input uploading directory. Without it , the files in current folder will be uploaded."
        )

    key_args = {
        "output_json": outputjson,
        "upload_dir": uploaddir,
        "rcic": rcic,
        "initial": initial,
        "previous": previous,
    }
    the_model = getModel(model)
    app = the_model(excels=[excel_name])
    app.make_web_form(**key_args)


@app.command()
def pdfform(
    model: str,
    excel_name: str,
    outputjson: str = typer.Argument(
        None,
        help="Output json file name. Without input, excel's name will be used  by adding '.json'",
    ),
    rcic: str = typer.Option(Config.rcic, help="RCIC's short name"),
):
    """Make json file based on model and input excel for pdf form filling"""

    excel_name = append_ext(excel_name, ".xlsx")

    if outputjson:
        outputjson = append_ext(outputjson, ".json")
    else:
        outputjson = remove_ext(excel_name) + ".json"

    key_args = {"output_json": outputjson, "rcic_id_name": rcic}
    the_model = getModel(model)
    app = the_model(excels=[excel_name])
    app.make_pdf_form(**key_args)


if __name__ == "__main__":
    app()
