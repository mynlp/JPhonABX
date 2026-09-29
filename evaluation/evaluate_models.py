import os
import numpy as np
import pandas as pd
from functools import lru_cache
from dtw_experiment import compute_dtw
import utils

def preprocess(df):
    for col in ['TGT', 'OTH', 'X']:
        parts = df[f'filename_{col}'].str.split('_', expand=True)
        start = parts[2].astype(int) // 20
        stop  = parts[3].str.replace('.wav', '', regex=False).astype(int) // 20 + 1

        df[f'start_{col}'] = start
        df[f'stop_{col}']  = stop
        df[f'feat_filename_{col}'] = (
            df[f'spk_idx_{col}'] + '-' + parts[1] + '.npy'
        )
    return df

@lru_cache(maxsize=16384)
def load_feat(path):
    return np.load(path)

def main(model_name, distance, type, layer, humaneval=False):
    dtypes = {'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str}
    if type not in ('mora', 'accent'):
        print('Invalid type')
        return

    triplets_csv = utils.discrimination_csv(type, humaneval)
    triplets = pd.read_csv(triplets_csv, dtype=dtypes)
    triplets = preprocess(triplets)

    # layer_num = 12 if 'base' in model_name else 24
    results_dir = 'abx_results'
    if os.path.isdir(results_dir):
        pass
    else:
        os.makedirs(results_dir)

    base_dir = '_'.join(model_name.split('/'))
    layer_dir = os.path.join(base_dir, f'transf_{layer}')

    result_list = []
    for i, row in enumerate(triplets.itertuples(index=False), start=1):
        if i % 10000 == 0:
            print(i)
        
        TGT_feat = load_feat(os.path.join(layer_dir, row.feat_filename_TGT))[row.start_TGT:row.stop_TGT]
        OTH_feat = load_feat(os.path.join(layer_dir, row.feat_filename_OTH))[row.start_OTH:row.stop_OTH]
        X_feat = load_feat(os.path.join(layer_dir, row.feat_filename_X))[row.start_X:row.stop_X]

        TGTX = compute_dtw(TGT_feat, X_feat, distance, norm_div=True)
        OTHX = compute_dtw(OTH_feat, X_feat, distance, norm_div=True)
        delta = OTHX - TGTX
        result_list.append([TGTX, OTHX, delta, '1' if delta > 0 else '0'])

    result_df = pd.DataFrame(result_list, columns=['TGTX', 'OTHX', 'delta', 'decision'])
    subset = 'humaneval_' if humaneval else ''
    result_df.to_csv(os.path.join(results_dir, f'{base_dir}_transf_{layer}_{type}_{subset}triplet_distances.csv'), index=False)
    print('Saved', type, layer)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to compute distances')
    parser.add_argument('model', metavar='f_do', type=str,
                        help='model')
    parser.add_argument('distance', metavar='f_do', type=str,
                        help='distance wanted')
    parser.add_argument('type', metavar='f_do', type=str,
                        help='mora or accent')
    parser.add_argument('layer', metavar='f_do', type=str,
                        help='layer')
    parser.add_argument('--humaneval', action='store_true',
                        help='use the 500-triplet human evaluation subset instead of the full CSV')
    args = parser.parse_args()
    print(args.model, args.distance, args.type, args.layer, args.humaneval)
    main(args.model, args.distance, args.type, args.layer, args.humaneval)
