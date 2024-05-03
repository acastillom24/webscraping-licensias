import sys
import pandas as pd


def split_csv(input_file, output_files, delimiter, partition_len):
    try:
        df = pd.read_csv(
            input_file,
            sep=delimiter,
            dtype=str)

        split_df = [df[i:(i + partition_len)] for i in range(0, len(df), partition_len)]

        for idx, el in enumerate(split_df):
            el.to_csv(f'{output_files}_part{idx + 1}.csv', index=False, sep='|')

        print('Complete split file...')

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python split_file.py <input_file.csv> <output_files> <delimiter> <partition_len>")
    else:
        var_input_file = sys.argv[1]
        var_output_files = sys.argv[2]
        if len(sys.argv) > 3:
            var_delimiter = sys.argv[3]
            var_partition_len = int(sys.argv[4])
        else:
            var_delimiter = '|'
            var_partition_len = 1000

        split_csv(var_input_file, var_output_files, var_delimiter, var_partition_len)
