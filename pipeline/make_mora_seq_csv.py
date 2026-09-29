import pandas as pd
from pathlib import Path
import utils

vowels = ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u']


def process_mora_seq_csv(speaker: str = 'jvs001', root: str = 'jvs_ver1'):
    # Since jvs001 has all of the 100 files, we only need to look at jvs001.
    trimora_rows = []
    bimora_rows = []
    base = Path(root) / speaker / 'parallel100' / 'mora_alignment_csv'

    for i in range(1, 101):
        file_idx = str(i).zfill(3)
        mora_alignment_csv_path = base / f'mora_alignment_{file_idx}.csv'
        if not mora_alignment_csv_path.is_file():
            print(mora_alignment_csv_path, 'does not exist.')
            continue
        mora_alignment_csv = utils.read_csv(str(mora_alignment_csv_path))

        # trimora
        first_is_long = False
        middle_is_long = False
        last_is_long = False
        for idx in range(len(mora_alignment_csv) - 2):
            filename = f'VOICEACTRESS100_{file_idx}.lab'
            first_stop = mora_alignment_csv.loc[idx, 'stop']
            middle_start = mora_alignment_csv.loc[idx + 1, 'start']
            middle_stop = mora_alignment_csv.loc[idx + 1, 'stop']
            last_start = mora_alignment_csv.loc[idx + 2, 'start']
            if first_stop == middle_start and middle_stop == last_start:
                first_mora = mora_alignment_csv.loc[idx, 'mora']
                middle_mora = mora_alignment_csv.loc[idx + 1, 'mora']
                last_mora = mora_alignment_csv.loc[idx + 2, 'mora']
                context_for_first_mora = '_' + middle_mora + last_mora
                context_for_middle_mora = first_mora + '_' + last_mora
                context_for_last_mora = first_mora + middle_mora + '_'
                first_is_long = bool(middle_is_long)
                middle_is_long = middle_mora in vowels and first_mora.endswith(middle_mora)
                last_is_long = last_mora in vowels and middle_mora.endswith(last_mora)
                if first_mora != 'cl' and last_mora != 'cl':
                    trimora_rows.append([filename, idx, first_mora, middle_mora, last_mora,
                                        context_for_first_mora, context_for_middle_mora, context_for_last_mora,
                                        first_is_long, middle_is_long, last_is_long])
            else:
                first_is_long = False
                middle_is_long = False
                last_is_long = False

        # bimora
        first_is_long = False
        last_is_long = False
        for idx in range(len(mora_alignment_csv) - 1):
            filename = f'VOICEACTRESS100_{file_idx}.lab'
            first_stop = mora_alignment_csv.loc[idx, 'stop']
            last_start = mora_alignment_csv.loc[idx + 1, 'start']
            if first_stop == last_start:
                first_mora = mora_alignment_csv.loc[idx, 'mora']
                last_mora = mora_alignment_csv.loc[idx + 1, 'mora']
                first_is_long = bool(last_is_long)
                last_is_long = last_mora in vowels and first_mora.endswith(last_mora)
                if first_mora != 'cl' and last_mora != 'cl':
                    bimora_rows.append([filename, idx, first_mora, last_mora, first_is_long, last_is_long])
            else:
                first_is_long = False
                last_is_long = False

    trimora_df = pd.DataFrame(trimora_rows,
                              columns=['filename', 'idx', 'first_mora', 'middle_mora', 'last_mora',
                                       'context_for_first_mora', 'context_for_middle_mora', 'context_for_last_mora',
                                       'first_is_long', 'middle_is_long', 'last_is_long'])
    utils.write_csv(trimora_df, 'trimora.csv', index=False)

    bimora_df = pd.DataFrame(bimora_rows, columns=['filename', 'idx', 'first_mora', 'last_mora', 'first_is_long', 'last_is_long'])
    utils.write_csv(bimora_df, 'bimora.csv', index=False)


def main():
    process_mora_seq_csv()


if __name__ == '__main__':
    main()
