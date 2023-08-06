import csv
import numpy as np


def load_csv(csv_path) -> list:
    lables = []
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for i_row in reader:
            lables.append(i_row)
    return np.array(lables).astype(float)
