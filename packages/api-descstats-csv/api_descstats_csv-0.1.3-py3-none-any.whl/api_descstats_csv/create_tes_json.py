from api_descstats_csv.utils import process_csv
import os
import json

filename = r"data/dataset_subset.csv"
path_json_expected = os.path.join(r"data/", "json_test_data.json")

histogram  = 10
b_mean = True
b_max = True
b_std = True
b_hist = True

json_res = process_csv(filename= filename,
            histogram= histogram,
            b_mean = True,
            b_max = True,
            b_std = True,
            b_hist = True)


with open(path_json_expected, "w", encoding="utf-8") as f:
    json.dump(json_res, f, ensure_ascii=False, indent=4)