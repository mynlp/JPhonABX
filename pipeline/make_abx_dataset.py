from pathlib import Path
import pandas as pd
import utils


INPUT_WAV_INFO = 'wav_files_info.csv'
OUTPUT_WAV_INFO_TMP = 'wav_files_info_tmp.csv'
ABX_PAIRS_MORA_CSV = 'abx_pairs_mora.csv'
ABX_DATASET_MORA_CSV = 'abx_dataset_mora.csv'
ABX_DATASET_ACCENT_CSV = 'abx_dataset_accent.csv'
GENDER_TXT = 'jvs_ver1/gender_f0range.txt'
CHUNK_SIZE = 100000


def normalize_pitch(pitch: str) -> str:
    if pitch == 'HHH':
        return 'LLL'
    if pitch == 'HH':
        return 'LL'
    return pitch


def normalize_pitch3(pitch2: str) -> str:
    return pitch2[0] + pitch2[-1]


def load_wav_files_info(path: str) -> pd.DataFrame:
    df = utils.read_csv(path, dtype={'spk_idx': str})
    df['file_idx'] = df['filename'].apply(lambda x: x.split('_')[1])
    df['pitch2'] = df['pitch'].apply(normalize_pitch)
    df['pitch3'] = df['pitch2'].apply(normalize_pitch3)
    df['mora_seq'] = df['first_mora'] + df['middle_mora'] + df['last_mora']
    return df


def load_gender_info(path: str) -> pd.DataFrame:
    df = utils.read_csv(path, sep=' ').rename(columns={'Male_or_Female': 'gender'})
    df['spk_idx'] = df['speaker'].apply(lambda x: x[-3:])
    return df[['spk_idx', 'gender']]


def categorize_abx_pairs(abx_pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    def is_special(row: pd.Series) -> bool:
        tgt, oth = row['TGT'], row['OTH']
        return any(
            tgt.replace(a, b) == oth
            for a, b in [('g', 'k'), ('k', 'g'), ('d', 't'), ('t', 'd'), ('b', 'p'), ('p', 'b'), ('z', 'j'), ('j', 'z')]
        )

    special = abx_pairs[abx_pairs.apply(is_special, axis=1)]
    not_special = abx_pairs.drop(index=special.index)

    first = not_special[not_special['contrast_type'] == 'initial']
    middle = not_special[not_special['contrast_type'] == 'medial']
    last = not_special[not_special['contrast_type'] == 'final']
    cl = abx_pairs[abx_pairs['contrast_type'] == 'geminate']
    n = abx_pairs[abx_pairs['contrast_type'] == 'nasal']
    long_vowel = abx_pairs[abx_pairs['contrast_type'] == 'vowel len']

    abx_pairs_1 = pd.concat([special, first, middle, last], ignore_index=True)
    abx_pairs_2 = pd.concat([cl, n, long_vowel], ignore_index=True)

    for df in (abx_pairs_1, abx_pairs_2):
        df['TGT_mora_seq'] = df.apply(lambda row: row['context'].replace('_', row['TGT']), axis=1)
        df['OTH_mora_seq'] = df.apply(lambda row: row['context'].replace('_', row['OTH']), axis=1)
        df['X'] = df['TGT']
        df['X_mora_seq'] = df['TGT_mora_seq']

    abx_pairs_1 = abx_pairs_1[['contrast_type', 'TGT', 'OTH', 'X', 'context', 'TGT_mora_seq', 'OTH_mora_seq', 'X_mora_seq']]
    abx_pairs_2 = abx_pairs_2[['contrast_type', 'TGT', 'OTH', 'X', 'context', 'TGT_mora_seq', 'OTH_mora_seq', 'X_mora_seq']]

    print('number of abx triplets:', len(abx_pairs_1)+len(abx_pairs_2))
    del special, not_special, first, middle, last, cl, n, long_vowel

    return abx_pairs_1, abx_pairs_2


def merge_chunks(left_df: pd.DataFrame, right_csv: str, left_on: list[str], right_on: list[str], right_columns: list[str]) -> pd.DataFrame:
    chunks = []
    for chunk in pd.read_csv(right_csv, chunksize=CHUNK_SIZE, usecols=right_columns, dtype={'spk_idx': str}):
        merged = pd.merge(left_df, chunk, left_on=left_on, right_on=right_on, how='inner')
        chunks.append(merged)
    return pd.concat(chunks, ignore_index=True)


def build_mora_abx_dataset(abx_pairs: pd.DataFrame, wav_tmp_csv: str, output_csv: str) -> int:
    # first, middle, last contrasts use pitch2 to match TGT/OTH with speakers
    tmp1 = merge_chunks(abx_pairs, wav_tmp_csv, ['TGT_mora_seq'], ['mora_seq'], ['filename', 'spk_idx', 'mora_seq', 'pitch', 'pitch2', 'gender'])
    tmp1.rename(columns={
        'filename': 'filename_TGT',
        'spk_idx': 'spk_idx_TGT',
        'mora_seq': 'mora_seq_TGT',
        'pitch': 'pitch_TGT',
        'pitch2': 'pitch2_TGT',
        'gender': 'gender_TGT',
    }, inplace=True)

    tmp2 = merge_chunks(
        tmp1,
        wav_tmp_csv,
        ['OTH_mora_seq', 'spk_idx_TGT', 'pitch2_TGT'],
        ['mora_seq', 'spk_idx', 'pitch2'],
        ['filename', 'spk_idx', 'mora_seq', 'pitch', 'pitch2', 'gender'],
    )
    del tmp1
    tmp2.drop(columns=['pitch2_TGT', 'pitch2'], inplace=True)
    tmp2.rename(columns={
        'filename': 'filename_OTH',
        'spk_idx': 'spk_idx_OTH',
        'mora_seq': 'mora_seq_OTH',
        'pitch': 'pitch_OTH',
        'gender': 'gender_OTH',
    }, inplace=True)

    total = 0
    for i, chunk in enumerate(pd.read_csv(wav_tmp_csv, chunksize=CHUNK_SIZE, usecols=['filename', 'spk_idx', 'mora_seq', 'pitch', 'gender'], dtype={'spk_idx': str})):
        merged = pd.merge(tmp2, chunk, left_on=['X_mora_seq'], right_on=['mora_seq'], how='inner')
        merged.rename(columns={
            'filename': 'filename_X',
            'spk_idx': 'spk_idx_X',
            'mora_seq': 'mora_seq_X',
            'pitch': 'pitch_X',
            'gender': 'gender_X',
        }, inplace=True)
        merged = merged[merged['filename_TGT'] != merged['filename_X']]
        merged = merged.sample(frac=0.505, random_state=1)
        merged.drop(columns=['TGT_mora_seq', 'OTH_mora_seq', 'X_mora_seq'], inplace=True)
        print(merged.isnull().sum())

        merged.to_csv(output_csv, mode='a', index=False, header=(i == 0))
        total += len(merged)
        del chunk, merged

    return total


def build_cl_n_long_abx_dataset(abx_pairs: pd.DataFrame, wav_tmp_csv: str, output_csv: str) -> int:
    # TGT, X: 3 morae, OTH: 2 morae
    tmp1 = merge_chunks(abx_pairs, wav_tmp_csv, ['TGT_mora_seq'], ['mora_seq'], ['filename', 'spk_idx', 'mora_seq', 'pitch', 'pitch3', 'gender'])
    tmp1.rename(columns={
        'filename': 'filename_TGT',
        'spk_idx': 'spk_idx_TGT',
        'mora_seq': 'mora_seq_TGT',
        'pitch': 'pitch_TGT',
        'pitch3': 'pitch3_TGT',
        'gender': 'gender_TGT',
    }, inplace=True)

    tmp2 = merge_chunks(
        tmp1,
        wav_tmp_csv,
        ['OTH_mora_seq', 'spk_idx_TGT', 'pitch3_TGT'],
        ['mora_seq', 'spk_idx', 'pitch3'],
        ['filename', 'spk_idx', 'mora_seq', 'pitch', 'pitch3', 'gender'],
    )
    del tmp1
    tmp2.drop(columns=['pitch3_TGT', 'pitch3'], inplace=True)
    tmp2.rename(columns={
        'filename': 'filename_OTH',
        'spk_idx': 'spk_idx_OTH',
        'mora_seq': 'mora_seq_OTH',
        'pitch': 'pitch_OTH',
        'gender': 'gender_OTH',
    }, inplace=True)

    total = 0
    for chunk in pd.read_csv(wav_tmp_csv, chunksize=CHUNK_SIZE, usecols=['filename', 'spk_idx', 'mora_seq', 'pitch', 'gender'], dtype={'spk_idx': str}):
        merged = pd.merge(tmp2, chunk, left_on=['X_mora_seq'], right_on=['mora_seq'], how='inner')
        merged.rename(columns={
            'filename': 'filename_X',
            'spk_idx': 'spk_idx_X',
            'mora_seq': 'mora_seq_X',
            'pitch': 'pitch_X',
            'gender': 'gender_X',
        }, inplace=True)
        merged = merged[merged['filename_TGT'] != merged['filename_X']]
        merged = merged.sample(frac=0.505, random_state=1)
        merged.drop(columns=['TGT_mora_seq', 'OTH_mora_seq', 'X_mora_seq'], inplace=True)
        print(merged.isnull().sum())

        merged.to_csv(output_csv, mode='a', index=False, header=not Path(output_csv).exists())
        total += len(merged)
        del chunk, merged

    return total


def build_pitch_abx_dataset(wav_tmp_csv: str, output_csv: str) -> int:
    wav_info = utils.read_csv(wav_tmp_csv, usecols=['filename', 'spk_idx', 'mora_seq', 'pitch', 'pitch2', 'gender'], dtype={'spk_idx': str})
    valid = (
        wav_info.groupby(['mora_seq', 'spk_idx'])['pitch2']
        .nunique()
        .reset_index()
        .query('pitch2 >= 2')
    )
    wav_info = wav_info.merge(valid[['mora_seq', 'spk_idx']], how='right', on=['mora_seq', 'spk_idx'])
    del valid
    utils.write_csv(wav_info, wav_tmp_csv, index=False)

    merged_chunks = []
    for chunk in pd.read_csv(wav_tmp_csv, chunksize=CHUNK_SIZE, dtype={'spk_idx': str}):
        # OTH has the same mora_seq and spk_idx as TGT
        merged = pd.merge(
            wav_info,
            chunk,
            left_on=['mora_seq', 'spk_idx'],
            right_on=['mora_seq', 'spk_idx'],
            how='inner',
            suffixes=('_TGT', '_OTH'),
        )
        merged_chunks.append(merged)

    abx_pitch = pd.concat(merged_chunks, ignore_index=True)
    del merged_chunks
    abx_pitch.rename(columns={
        'spk_idx': 'spk_idx_TGT',
        'mora_seq': 'mora_seq_TGT',
    }, inplace=True)
    abx_pitch = abx_pitch[abx_pitch['pitch2_TGT'] != abx_pitch['pitch2_OTH']]
    abx_pitch = abx_pitch.drop(columns=['pitch2_OTH'])
    abx_pitch['spk_idx_OTH'] = abx_pitch['spk_idx_TGT']
    abx_pitch['mora_seq_OTH'] = abx_pitch['mora_seq_TGT']
    abx_pitch = abx_pitch[
        [
            'filename_TGT', 'spk_idx_TGT', 'pitch_TGT', 'pitch2_TGT', 'mora_seq_TGT', 'gender_TGT',
            'filename_OTH', 'spk_idx_OTH', 'pitch_OTH', 'mora_seq_OTH', 'gender_OTH',
        ]
    ]
    del wav_info

    if Path(output_csv).exists():
        Path(output_csv).unlink()

    total = 0
    for i, chunk in enumerate(pd.read_csv(wav_tmp_csv, chunksize=CHUNK_SIZE, dtype={'spk_idx': str})):
        # X has the same mora_seq and pitch as TGT
        merged = pd.merge(
            abx_pitch,
            chunk,
            left_on=['mora_seq_TGT', 'pitch2_TGT'],
            right_on=['mora_seq', 'pitch2'],
            how='inner',
        )
        merged.rename(columns={
            'filename': 'filename_X',
            'spk_idx': 'spk_idx_X',
            'mora_seq': 'mora_seq_X',
            'pitch': 'pitch_X',
            'gender': 'gender_X',
        }, inplace=True)
        merged.drop(columns=['pitch2_TGT', 'pitch2'], inplace=True)
        merged = merged[merged['filename_TGT'] != merged['filename_X']]
        merged = merged.sample(frac=0.178, random_state=1)
        print(merged.isnull().sum())

        merged.to_csv(output_csv, mode='a', index=False, header=(i == 0))
        total += len(merged)
        del chunk, merged

    return total


def make_abx_dataset() -> None:
    abx_pairs = utils.read_csv(ABX_PAIRS_MORA_CSV)
    wav_files_info = load_wav_files_info(INPUT_WAV_INFO)
    gender_info = load_gender_info(GENDER_TXT)
    wav_files_info = wav_files_info.merge(gender_info, how='left', on='spk_idx')
    utils.write_csv(wav_files_info, OUTPUT_WAV_INFO_TMP, index=False)
    del gender_info, wav_files_info

    abx_pairs_1, abx_pairs_2 = categorize_abx_pairs(abx_pairs)
    del abx_pairs

    # remove existing abx_dataset_mora.csv because we will use the appending mode in the following steps
    if Path(ABX_DATASET_MORA_CSV).exists():
        Path(ABX_DATASET_MORA_CSV).unlink()

    total_mora = 0
    total_mora += build_mora_abx_dataset(abx_pairs_1, OUTPUT_WAV_INFO_TMP, ABX_DATASET_MORA_CSV)
    total_mora += build_cl_n_long_abx_dataset(abx_pairs_2, OUTPUT_WAV_INFO_TMP, ABX_DATASET_MORA_CSV)
    print('number of abx data for mora discrimination:', total_mora)

    total_pitch = build_pitch_abx_dataset(OUTPUT_WAV_INFO_TMP, ABX_DATASET_ACCENT_CSV)
    print('number of abx data for pitch discrimination:', total_pitch)


def main() -> None:
    make_abx_dataset()


if __name__ == '__main__':
    main()
