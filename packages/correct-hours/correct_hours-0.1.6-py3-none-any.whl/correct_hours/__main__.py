from openpyxl import load_workbook
from argparse import ArgumentParser
from pathlib import Path

from correct_hours.workbook_processor import WorkbookProcessor

parser = ArgumentParser()
parser.add_argument("directory", help="Location of Excel files", type=str)

args = parser.parse_args()
directory = args.directory


def get_new_file_name(filepath):
    path = Path(filepath)
    return f"{path.parent.absolute()}/output/copy_{path.name}"


# create output folder
Path(f"{directory}/output").mkdir(parents=True, exist_ok=True)
files = Path(directory).glob('*')
for f in files:
    if f.is_file():
        if not str.startswith(f.name, "~"):
            filepath = f.absolute()
            print(f"Processing file {filepath}...")
            workbook = load_workbook(filename=filepath)
            processor = WorkbookProcessor(workbook)
            processor.process()
            new_file_name = get_new_file_name(filepath)
            workbook.save(filename=new_file_name)
            print(f"Finished processing file. Created file {new_file_name}.")
