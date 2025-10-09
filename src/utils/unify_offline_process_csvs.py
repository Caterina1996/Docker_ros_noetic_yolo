#!/usr/bin/env python3.11

import os
import pandas as pd
import argparse
import glob 

def process_csvs(root_dir):
   
    data = []

    csvs = glob.glob(root_dir + "/**/bagfile_data.csv", recursive=True)
    print("I'm gonna process the following csvs: ",csvs)

    for csv in csvs:

        df = pd.read_csv(csv, sep=',')

        # file_id = "/".join(csv.split("PROCESSED/")[-1].split("/")[:-1])  
        file_id="/".join(csv.split("/")[:-1])
        # print("Columns: ",df.columns)

        if 'Total Count' not in df.columns:
            raise KeyError(f"'Total Count' not found :( {csv}")
       

        # Transpose the class column
        species_counts = df.set_index('Class').T
        
        species_counts['file_id'] = file_id      
        data.append(species_counts)

    # Combine in a single DF
    result_df = pd.concat(data, ignore_index=True)

    columns = ['file_id'] +[col for col in result_df.columns if col != 'file_id'] 
    result_df = result_df[columns]


    # Store the unified DF:
    output_path = os.path.join(root_dir, 'species_per_bagfile.csv')
    if os.path.exists(output_path):
        os.remove(output_path)

    result_df.to_csv(output_path, index=False)

    print("CSV unificado generado en ", output_path)


def main():

    parser = argparse.ArgumentParser(description="Unify bagfiles' fish info")
    parser.add_argument('--root_dir',default="output", type=str, help="Root dir to the CSVs")

    args = parser.parse_args()

    process_csvs(args.root_dir)

if __name__ == "__main__":
    main()
