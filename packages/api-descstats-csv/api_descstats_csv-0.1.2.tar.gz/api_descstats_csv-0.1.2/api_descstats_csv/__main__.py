import json
import os

import typer
from rich.console import Console
from utils import process_csv

app = typer.Typer(
    name="api_descstats_csv",
    help="Calculate simple descreptive stats from csv with Python with cli or import respecting the limit of 512 MB ",
    add_completion=False,
)

console = Console()


@app.command()
def main(
    filename: str = typer.Option(..., help="Path to readable csv."),
    histogram: int = typer.Option(..., help="Size of histogram bins."),
    output_path: str = typer.Option(..., help="Path to save metrics as json."),
    b_mean: bool = typer.Option(False, help="Determines if mean will be calculated."),
    b_max: bool = typer.Option(False, help="Determines if max will be calculated."),
    b_std: bool = typer.Option(False, help="Determines if std will be calculated."),
    b_hist: bool = typer.Option(False, help="Determines if histogram will be calculated."),
) -> None:

    console.print(f"[bold yellow]Processing each column of CSV[/]")

    data = process_csv(filename, histogram, b_mean, b_max, b_std, b_hist)

    data = {"columns": data}

    # Persist results
    path_json = os.path.join(output_path, "json_data.json")

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    console.print(f"[bold green]Results saved in {output_path}")


if __name__ == "__main__":
    app()
