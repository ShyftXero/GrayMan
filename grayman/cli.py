from typer import Typer
from helpers import unwrap_dict, wrap_dict
from pathlib import Path
from rich import print
app = Typer()


@app.command()
def unwrap_file(file:Path):
	with open(file, 'rb') as f:
		data = f.read()
	unwrapped = unwrap_dict(data)
	print(unwrapped)
	


if __name__ == '__main__':
	app()
