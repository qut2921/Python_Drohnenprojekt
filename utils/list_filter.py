import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from haversine import haversine, Unit


def choose_folder(colorProfile):
    """
    Choose the folder based on the color profile.
    """
    if colorProfile == 0:
        return "/blue"
    elif colorProfile == 1:
        return "/red"
    elif colorProfile == 2:
        return "/yellow"
    elif colorProfile == 4:
        return "/orange"
    else:
        raise ValueError("Invalid color profile. Must be between 0 and 4.")


def filter_near_duplicates(color):
# Load CSV with no headers
    df = pd.read_csv("Mission1/Found_object"+ color +"/image_processed.csv", header=None)

    # Set descriptive column names
    df.columns = ["sequence", "image", "n_ned", "e_ned", "latitude", "longitude","shape"]

    # Initialize keep mask
    keep_mask = [True] * len(df)

    # Check for near-duplicates
    for i in range(len(df)):
        print(f"Checking row {i + 1}/{len(df)}")
        if not keep_mask[i]:
            continue
        coord_i = (df.at[i, "latitude"], df.at[i, "longitude"])
        for j in range(i + 1, len(df)):
            print(f"Comparing with row {j + 1}/{len(df)}")
            coord_j = (df.at[j, "latitude"], df.at[j, "longitude"])
            if haversine(coord_i, coord_j, unit=Unit.METERS) < 1.5:
                keep_mask[j] = False

    # Filter and save result
    filtered_df = df[keep_mask].reset_index(drop=True)
    filtered_df.to_csv("Mission1/Found_object"+ color+"/filtered_output.csv", index=False, header=None)

    print(f"Filtered CSV saved. {len(df)} → {len(filtered_df)} rows.")
