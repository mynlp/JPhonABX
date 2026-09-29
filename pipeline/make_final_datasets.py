import pandas as pd
import utils


def normalize_pitch2(pitch: str) -> str:
    if pitch == 'HHH':
        return 'LLL'
    if pitch == 'HH':
        return 'LL'
    return pitch


def pitch_match(pitch_tgt: str, pitch_x: str) -> str:
    return 'match' if normalize_pitch2(pitch_tgt) == normalize_pitch2(pitch_x) else 'unmatch'


def add_discrimination_flags(df: pd.DataFrame, include_pitch: bool = True) -> pd.DataFrame:
    df = df.copy()
    df['spkTGTX'] = df.apply(lambda row: 'match' if row['spk_idx_TGT'] == row['spk_idx_X'] else 'unmatch', axis=1)
    df['genderTGTX'] = df.apply(lambda row: 'match' if row['gender_TGT'] == row['gender_X'] else 'unmatch', axis=1)
    if include_pitch:
        df['pitchTGTX'] = df.apply(lambda row: pitch_match(row['pitch_TGT'], row['pitch_X']), axis=1)
    return df


def sample_rows(df: pd.DataFrame, n: int | None = None, random_state: int = 1) -> pd.DataFrame:
    subset = df.copy()
    if n is None:
        return subset
    return subset.sample(n=n, random_state=random_state)


def build_mora_special_first(df: pd.DataFrame) -> pd.DataFrame:
    special1 = df[(df['TGT'].str.replace('b', 'p') == df['OTH']) | (df['TGT'].str.replace('p', 'b') == df['OTH'])]
    special2 = df[(df['TGT'].str.replace('g', 'k') == df['OTH']) | (df['TGT'].str.replace('k', 'g') == df['OTH'])].sample(n=200, random_state=1)
    special3 = df[(df['TGT'].str.replace('d', 't') == df['OTH']) | (df['TGT'].str.replace('t', 'd') == df['OTH'])].sample(n=125, random_state=1)
    special4 = df[(df['TGT'].str.replace('z', 'j') == df['OTH']) | (df['TGT'].str.replace('j', 'z') == df['OTH'])].sample(n=75, random_state=1)
    return pd.concat([special1, special2, special3, special4])


def build_mora_special_middle(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['TGT_is_long'] = df.apply(lambda row: row['TGT'] in ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u'] and row['context'].split('_')[0].endswith(row['TGT']), axis=1)
    df['OTH_is_long'] = df.apply(lambda row: row['OTH'] in ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u'] and row['context'].split('_')[0].endswith(row['OTH']), axis=1)
    special1 = df[((df['TGT'] == 'N') & (df['OTH'] == 'cl'))
                  | ((df['TGT'] == 'cl') & (df['OTH'] == 'N'))
                  | ((df['TGT'] == 'cl') & (df['OTH_is_long'] == True))
                  | ((df['TGT_is_long'] == True) & (df['OTH'] == 'cl'))]
    special2 = df[((df['TGT'] == 'N') & (df['OTH_is_long'] == True))
                  | ((df['TGT_is_long'] == True) & (df['OTH'] == 'N'))].sample(n=150, random_state=1)
    special3 = df[(df['TGT'].str.replace('b', 'p') == df['OTH']) | (df['TGT'].str.replace('p', 'b') == df['OTH'])]
    special4 = df[(df['TGT'].str.replace('g', 'k') == df['OTH']) | (df['TGT'].str.replace('k', 'g') == df['OTH'])].sample(n=200, random_state=1)
    special5 = df[(df['TGT'].str.replace('d', 't') == df['OTH']) | (df['TGT'].str.replace('t', 'd') == df['OTH'])].sample(n=125, random_state=1)
    special6 = df[(df['TGT'].str.replace('z', 'j') == df['OTH']) | (df['TGT'].str.replace('j', 'z') == df['OTH'])].sample(n=75, random_state=1)
    return pd.concat([special1, special2, special3, special4, special5, special6])


def build_mora_special_last(df: pd.DataFrame) -> pd.DataFrame:
    special1 = df[(df['TGT'].str.replace('b', 'p') == df['OTH']) | (df['TGT'].str.replace('p', 'b') == df['OTH'])]
    special2 = df[(df['TGT'].str.replace('g', 'k') == df['OTH']) | (df['TGT'].str.replace('k', 'g') == df['OTH'])].sample(n=200, random_state=1)
    special3 = df[(df['TGT'].str.replace('d', 't') == df['OTH']) | (df['TGT'].str.replace('t', 'd') == df['OTH'])].sample(n=125, random_state=1)
    special4 = df[(df['TGT'].str.replace('z', 'j') == df['OTH']) | (df['TGT'].str.replace('j', 'z') == df['OTH'])]
    return pd.concat([special1, special2, special3, special4])


def sample_mora_not_special(df: pd.DataFrame, counts: dict[tuple[str, str, str], int | None]) -> pd.DataFrame:
    collected = []
    for key, n in counts.items():
        spk, gender, pitch = key
        subset = df[(df['spkTGTX'] == spk) & (df['genderTGTX'] == gender) & (df['pitchTGTX'] == pitch)]
        if n is None:
            collected.append(subset)
        else:
            collected.append(subset.sample(n=n, random_state=1))
    return pd.concat(collected, ignore_index=True)


def sample_mora_contrast(df: pd.DataFrame, contrast_type: str) -> pd.DataFrame:
    df = df[df['contrast_type'] == contrast_type]

    if contrast_type == 'initial':
        special = build_mora_special_first(df)
        not_special = df.drop(index=special.index)
        counts = {
            ('match', 'match', 'match'): 1755,
            ('match', 'match', 'unmatch'): 1755,
            ('unmatch', 'match', 'match'): 7021,
            ('unmatch', 'match', 'unmatch'): 7022,
            ('unmatch', 'unmatch', 'match'): 7022,
            ('unmatch', 'unmatch', 'unmatch'): 7022,
        }
    elif contrast_type == 'medial':
        special = build_mora_special_middle(df)
        not_special = df.drop(index=special.index)
        counts = {
            ('match', 'match', 'match'): 1757,
            ('match', 'match', 'unmatch'): None,
            ('unmatch', 'match', 'match'): 7030,
            ('unmatch', 'match', 'unmatch'): 7030,
            ('unmatch', 'unmatch', 'match'): 7030,
            ('unmatch', 'unmatch', 'unmatch'): 7030,
        }
    elif contrast_type == 'final':
        special = build_mora_special_last(df)
        not_special = df.drop(index=special.index)
        counts = {
            ('match', 'match', 'match'): 1759,
            ('match', 'match', 'unmatch'): 1760,
            ('unmatch', 'match', 'match'): 7039,
            ('unmatch', 'match', 'unmatch'): 7039,
            ('unmatch', 'unmatch', 'match'): 7039,
            ('unmatch', 'unmatch', 'unmatch'): 7039,
        }
    else:
        return pd.DataFrame(columns=df.columns)
    sampled = pd.concat([special, sample_mora_not_special(not_special, counts)], ignore_index=True)
    return sampled.drop(columns=[col for col in ['TGT_is_long', 'OTH_is_long'] if col in sampled.columns], errors='ignore')


def sample_mora_category(df: pd.DataFrame, contrast_type: str, extra_counts: dict[tuple[str, str, str], int | None]) -> pd.DataFrame:
    subset = df[df['contrast_type'] == contrast_type]
    return sample_mora_not_special(subset, extra_counts)


def build_mora_pool(df: pd.DataFrame) -> pd.DataFrame:
    first = sample_mora_contrast(df, 'initial')
    middle = sample_mora_contrast(df, 'medial')
    last = sample_mora_contrast(df, 'final')
    cl = sample_mora_category(df, 'geminate', {
        ('match', 'match', 'match'): None,
        ('match', 'match', 'unmatch'): None,
        ('unmatch', 'match', 'match'): None,
        ('unmatch', 'match', 'unmatch'): None,
        ('unmatch', 'unmatch', 'match'): 15999,
        ('unmatch', 'unmatch', 'unmatch'): None,
    })
    n = sample_mora_category(df, 'nasal', {
        ('match', 'match', 'match'): None,
        ('match', 'match', 'unmatch'): None,
        ('unmatch', 'match', 'match'): 11826,
        ('unmatch', 'match', 'unmatch'): None,
        ('unmatch', 'unmatch', 'match'): 11826,
        ('unmatch', 'unmatch', 'unmatch'): None,
    })
    long_vowel = sample_mora_category(df, 'vowel len', {
        ('match', 'match', 'match'): None,
        ('match', 'match', 'unmatch'): None,
        ('unmatch', 'match', 'match'): 7755,
        ('unmatch', 'match', 'unmatch'): 7755,
        ('unmatch', 'unmatch', 'match'): 7755,
        ('unmatch', 'unmatch', 'unmatch'): 7755,
    })
    return pd.concat([first, middle, last, cl, n, long_vowel], ignore_index=True)


def build_accent_pool(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df[df['num_mora'] == 2]
    df3 = df[df['num_mora'] == 3]

    accent2 = pd.concat([
        sample_rows(df2[(df2['spkTGTX'] == 'match') & (df2['genderTGTX'] == 'match')], n=5444),
        sample_rows(df2[(df2['spkTGTX'] == 'unmatch') & (df2['genderTGTX'] == 'match')], n=21778),
        sample_rows(df2[(df2['spkTGTX'] == 'unmatch') & (df2['genderTGTX'] == 'unmatch')], n=21778),
    ], ignore_index=True)

    accent3 = pd.concat([
        df3[(df3['spkTGTX'] == 'match') & (df3['genderTGTX'] == 'match')],
        sample_rows(df3[(df3['spkTGTX'] == 'unmatch') & (df3['genderTGTX'] == 'match')], n=24928),
        df3[(df3['spkTGTX'] == 'unmatch') & (df3['genderTGTX'] == 'unmatch')],
    ], ignore_index=True)

    return pd.concat([accent2, accent3], ignore_index=True)


def merge_accent_mora_seq(df: pd.DataFrame) -> pd.DataFrame:
    # TGT, OTH and X of an accent triplet always cover the same mora sequence
    df = df.drop(columns=['mora_seq_OTH', 'mora_seq_X']).rename(columns={'mora_seq_TGT': 'mora_seq'})
    columns = [col for col in df.columns if col != 'mora_seq']
    columns.insert(columns.index('num_mora'), 'mora_seq')
    return df[columns]


def write_stats(mora_df: pd.DataFrame, accent_df: pd.DataFrame) -> None:
    mora_df.groupby(by=['contrast_type', 'TGT', 'OTH', 'context', 'spkTGTX', 'genderTGTX', 'pitchTGTX'])['filename_TGT'].count().reset_index().to_csv(utils.discrimination_csv('mora', suffix='_stat'), index=False)
    accent_df.groupby(by=['num_mora', 'pitch_TGT', 'pitch_OTH', 'spkTGTX', 'genderTGTX'])['filename_TGT'].count().reset_index().to_csv(utils.discrimination_csv('accent', suffix='_stat'), index=False)


def build_final_datasets() -> None:
    df_mora = utils.read_csv('abx_dataset_mora.csv', dtype={'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str})
    df_accent = utils.read_csv('abx_dataset_accent.csv', dtype={'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str})

    df_mora = add_discrimination_flags(df_mora)
    df_accent = add_discrimination_flags(df_accent, include_pitch=False)
    df_accent['num_mora'] = df_accent['mora_seq_TGT'].apply(lambda x: 2 if '-' in x else 3)

    mora_sampled = build_mora_pool(df_mora)
    accent_sampled = merge_accent_mora_seq(build_accent_pool(df_accent))

    utils.write_csv(mora_sampled, utils.discrimination_csv('mora'), index=False)
    utils.write_csv(accent_sampled, utils.discrimination_csv('accent'), index=False)
    write_stats(mora_sampled, accent_sampled)


def main() -> None:
    build_final_datasets()


if __name__ == '__main__':
    main()
