import datasets
import sys

file = sys.argv[1]

ds = datasets.load_dataset('parquet', data_files=file)

