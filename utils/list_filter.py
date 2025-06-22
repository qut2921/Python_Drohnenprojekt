import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from haversine import haversine, Unit





def filter_near_duplicates():
# Load CSV with no headers
    df = pd.read_csv("Mission1/Found_object/image_processed.csv", header=None)

    # Set descriptive column names
    df.columns = ["sequence", "image", "object_id", "color", "shape", "latitude", "longitude"]

    # Initialize keep mask
    keep_mask = [True] * len(df)

    # Check for near-duplicates
    for i in range(len(df)):
        print(f"Checking row {i + 1}/{len(df)}")
        if not keep_mask[i]:
            continue
        coord_i = (df.at[i, "latitude"], df.at[i, "longitude"])
        color_i = df.at[i, "color"]
        for j in range(i + 1, len(df)):
            print(f"Comparing with row {j + 1}/{len(df)}")
            coord_j = (df.at[j, "latitude"], df.at[j, "longitude"])
            color_j = df.at[j, "color"]
            if haversine(coord_i, coord_j, unit=Unit.METERS) < 1.5 and color_i == color_j:
                keep_mask[j] = False

    # Filter and save result
    filtered_df = df[keep_mask].reset_index(drop=True)
    filtered_df.to_csv("Mission1/Found_object/filtered_output.csv", index=False)


    print("Shape before saving:", filtered_df.shape)
    print(filtered_df.head())
    print(f"Filtered CSV saved. {len(df)} → {len(filtered_df)} rows.")
