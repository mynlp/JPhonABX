import pandas as pd
from itertools import combinations
import utils


def build_abx_pairs(trimora_csv_path: str = 'trimora.csv', bimora_csv_path: str = 'bimora.csv'):
    trimora_csv = utils.read_csv(trimora_csv_path)
    bimora_csv = utils.read_csv(bimora_csv_path)

    abx_pairs = []

    # first mora contrast
    first_mora_candidates_per_context = trimora_csv.groupby('context_for_first_mora')['first_mora'].unique().reset_index()
    first_mora_candidates_per_context['num_first_mora'] = first_mora_candidates_per_context['first_mora'].apply(len)

    for i in range(len(first_mora_candidates_per_context)):
        context = first_mora_candidates_per_context.loc[i, 'context_for_first_mora']
        first_mora_candidates = first_mora_candidates_per_context.loc[i, 'first_mora']
        for first_mora1, first_mora2 in combinations(first_mora_candidates, 2):
            abx_pairs.append(['initial', first_mora1, first_mora2, context])

    first_mora_contrast_value_counts = first_mora_candidates_per_context['num_first_mora'].value_counts().reset_index()
    first_mora_contrast_value_counts['num_contrast'] = first_mora_contrast_value_counts['num_first_mora'] * (first_mora_contrast_value_counts['num_first_mora'] - 1) * first_mora_contrast_value_counts['count'] // 2
    print('number of first mora contrasts:', first_mora_contrast_value_counts['num_contrast'].sum())

    # middle mora contrast
    middle_mora_candidates_per_context = trimora_csv.groupby('context_for_middle_mora')['middle_mora'].unique().reset_index()
    middle_mora_candidates_per_context['num_middle_mora'] = middle_mora_candidates_per_context['middle_mora'].apply(len)

    for i in range(len(middle_mora_candidates_per_context)):
        context = middle_mora_candidates_per_context.loc[i, 'context_for_middle_mora']
        middle_mora_candidates = middle_mora_candidates_per_context.loc[i, 'middle_mora']
        for middle_mora1, middle_mora2 in combinations(middle_mora_candidates, 2):
            abx_pairs.append(['medial', middle_mora1, middle_mora2, context])

    middle_mora_contrast_value_counts = middle_mora_candidates_per_context['num_middle_mora'].value_counts().reset_index()
    middle_mora_contrast_value_counts['num_contrast'] = middle_mora_contrast_value_counts['num_middle_mora'] * (middle_mora_contrast_value_counts['num_middle_mora'] - 1) * middle_mora_contrast_value_counts['count'] // 2
    print('number of middle mora contrasts:', middle_mora_contrast_value_counts['num_contrast'].sum())

    # last mora contrast
    last_mora_candidates_per_context = trimora_csv.groupby('context_for_last_mora')['last_mora'].unique().reset_index()
    last_mora_candidates_per_context['num_last_mora'] = last_mora_candidates_per_context['last_mora'].apply(len)

    for i in range(len(last_mora_candidates_per_context)):
        context = last_mora_candidates_per_context.loc[i, 'context_for_last_mora']
        last_mora_candidates = last_mora_candidates_per_context.loc[i, 'last_mora']
        for last_mora1, last_mora2 in combinations(last_mora_candidates, 2):
            abx_pairs.append(['final', last_mora1, last_mora2, context])

    last_mora_contrast_value_counts = last_mora_candidates_per_context['num_last_mora'].value_counts().reset_index()
    last_mora_contrast_value_counts['num_contrast'] = last_mora_contrast_value_counts['num_last_mora'] * (last_mora_contrast_value_counts['num_last_mora'] - 1) * last_mora_contrast_value_counts['count'] // 2
    print('number of last mora contrasts:', last_mora_contrast_value_counts['num_contrast'].sum())

    # add context column
    bimora_csv['context_for_middle_mora'] = bimora_csv['first_mora'] + '_' + bimora_csv['last_mora']

    # special cases (cl, N, long vowel)
    trimora_cl_middle = trimora_csv[trimora_csv['middle_mora'] == 'cl']
    trimora_cl_middle_contexts = trimora_cl_middle.groupby('context_for_middle_mora')['middle_mora'].count().reset_index()
    trimora_cl_middle_contexts = trimora_cl_middle_contexts.merge(bimora_csv[['context_for_middle_mora']].drop_duplicates(subset='context_for_middle_mora'), how='inner', on='context_for_middle_mora')
    for context in trimora_cl_middle_contexts['context_for_middle_mora']:
        abx_pairs.append(['geminate', 'cl', '-', context])
    print('number of cl contrasts:', len(trimora_cl_middle_contexts))

    trimora_N_middle = trimora_csv[trimora_csv['middle_mora'] == 'N']
    trimora_N_middle_contexts = trimora_N_middle.groupby('context_for_middle_mora')['middle_mora'].count().reset_index()
    trimora_N_middle_contexts = trimora_N_middle_contexts.merge(bimora_csv[['context_for_middle_mora']].drop_duplicates(subset='context_for_middle_mora'), how='inner', on='context_for_middle_mora')
    for context in trimora_N_middle_contexts['context_for_middle_mora']:
        abx_pairs.append(['nasal', 'N', '-', context])
    print('number of N contrasts:', len(trimora_N_middle_contexts))

    trimora_long_vowel_middle = trimora_csv[trimora_csv['middle_is_long'] == True]
    trimora_long_vowel_middle_contexts = trimora_long_vowel_middle.groupby('context_for_middle_mora')['middle_mora'].count().reset_index()
    trimora_long_vowel_middle_contexts = trimora_long_vowel_middle_contexts.merge(bimora_csv[['first_mora', 'context_for_middle_mora']].drop_duplicates(subset='context_for_middle_mora'), how='inner', on='context_for_middle_mora')
    for context, first_mora in zip(trimora_long_vowel_middle_contexts['context_for_middle_mora'], trimora_long_vowel_middle_contexts['first_mora']):
        abx_pairs.append(['vowel len', first_mora[-1], '-', context])
    print('number of long vowel contrasts:', len(trimora_long_vowel_middle_contexts))

    abx_pairs_df = pd.DataFrame(abx_pairs, columns=['contrast_type', 'TGT', 'OTH', 'context'])
    utils.write_csv(abx_pairs_df, 'abx_pairs_mora.csv', index=False)


def main():
    build_abx_pairs()


if __name__ == '__main__':
    main()
