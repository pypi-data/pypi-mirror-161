import csv
import numpy as np
import pandas as pd
from tqdm import tqdm


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    """by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified"""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return "{:.1f} {}{}".format(num, "Yi", suffix)


def get_header(filename: str) -> list["str"]:
    with open(filename) as csvfile:
        datareader = csv.reader(csvfile)
        return next(datareader)


def read_col(filename: str, col: str) -> np.ndarray:
    arr = pd.read_csv(filename, engine="pyarrow", usecols=[col])
    arr = arr.values
    arr = arr[~np.isnan(arr)]
    arr = arr.astype(np.float32)
    return arr


def calculate_metrics(
    arr: np.dtype,
    col: str,
    b_mean: bool = False,
    b_max: bool = False,
    b_std: bool = False,
    b_hist: bool = False,
    sz: int = 10,
) -> dict:

    selected_metrics = {"name": col}

    # Calculate simple metrics (mean, std, max)
    simple_metrics = [
        ["mean", b_mean, np.mean],
        ["max", b_max, np.max],
        ["std", b_std, np.std],
    ]

    for v in simple_metrics:
        if v[1] == True:
            metric = round(v[2](arr), 2).astype(str)
            selected_metrics.update({v[0]: metric})

    # Calculate histogram
    bins = int(arr.shape[0] / sz)
    if b_hist == True:
        if bins < 3:
            raise ValueError("Histogram with less than 3 bins, try a smaller bin size")
        elif bins > 2 * 3840:
            raise ValueError(f"Too many bins, try a bigger bin size. Suggestion size: {int((arr.shape[0]/(2*3840))+2)}")

        hist, bin_edges = np.histogram(arr, bins=bins)

        selected_metrics.update(
            {
                "histogram": [
                    {
                        "from": round(bin_edges[i], 2).astype(str),
                        "to": round(bin_edges[i + 1], 2).astype(str),
                        "count": hist[i].astype(str),
                    }
                    for i in range(len(hist))
                ]
            }
        )

    del arr

    return selected_metrics


def process_csv(
    filename: str,
    histogram: int,
    b_mean: bool = False,
    b_max: bool = False,
    b_std: bool = False,
    b_hist: bool = False,
) -> dict:

    headers = get_header(filename)
    headers.remove("timestamp")

    data = []

    for col in tqdm(headers):

        # Load
        arr = read_col(filename, col)

        # Calculate and format results
        metrics_dict = calculate_metrics(
            arr=arr, col=col, b_mean=b_mean, b_max=b_max, b_std=b_std, b_hist=b_hist, sz=histogram
        )

        # Save results
        data.append(metrics_dict)
        del arr
        del metrics_dict

    return data


def metrics2pandas(
    filename: str, histogram: int, b_mean: bool = False, b_max: bool = False, b_std: bool = False, b_hist: bool = False
) -> pd.DataFrame:
    data = process_csv(filename, histogram=histogram, b_mean=b_mean, b_max=b_max, b_std=b_std, b_hist=b_hist)
    data = pd.DataFrame(data)

    return data
