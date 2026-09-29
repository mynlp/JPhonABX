import pandas as pd
import os
import shutil
import random
import utils

random.seed(1)

# mora_discrimination = pd.read_csv('abx_dataset.csv', dtype={'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str})
mora_discrimination = pd.read_csv(utils.discrimination_csv('mora', True), dtype={'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str})
mora_discrimination = mora_discrimination[['spk_idx_TGT', 'spk_idx_OTH', 'spk_idx_X', 'filename_TGT', 'filename_OTH', 'filename_X', 'mora_seq_OTH']]
accent_discrimination = pd.read_csv(utils.discrimination_csv('accent', True), dtype={'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str})
accent_discrimination = accent_discrimination[['spk_idx_TGT', 'spk_idx_OTH', 'spk_idx_X', 'filename_TGT', 'filename_OTH', 'filename_X', 'mora_seq']]

mora_discrimination.loc[:, 'filepath_TGT'] = 'jvs_ver1/jvs' + mora_discrimination['spk_idx_TGT'] + '/parallel100/wav_trimora/' + mora_discrimination['filename_TGT']
mora_discrimination.loc[~mora_discrimination['mora_seq_OTH'].str.contains('-'), 'filepath_OTH'] = 'jvs_ver1/jvs' + mora_discrimination['spk_idx_OTH'] + '/parallel100/wav_trimora/' + mora_discrimination['filename_OTH']
mora_discrimination.loc[mora_discrimination['mora_seq_OTH'].str.contains('-'), 'filepath_OTH'] = 'jvs_ver1/jvs' + mora_discrimination['spk_idx_OTH'] + '/parallel100/wav_bimora/' + mora_discrimination['filename_OTH']
mora_discrimination.loc[:, 'filepath_X'] = 'jvs_ver1/jvs' + mora_discrimination['spk_idx_X'] + '/parallel100/wav_trimora/' + mora_discrimination['filename_X']
accent_discrimination.loc[~accent_discrimination['mora_seq'].str.contains('-'), 'filepath_TGT'] = 'jvs_ver1/jvs' + accent_discrimination['spk_idx_TGT'] + '/parallel100/wav_trimora/' + accent_discrimination['filename_TGT']
accent_discrimination.loc[accent_discrimination['mora_seq'].str.contains('-'), 'filepath_TGT'] = 'jvs_ver1/jvs' + accent_discrimination['spk_idx_TGT'] + '/parallel100/wav_bimora/' + accent_discrimination['filename_TGT']
accent_discrimination.loc[~accent_discrimination['mora_seq'].str.contains('-'), 'filepath_OTH'] = 'jvs_ver1/jvs' + accent_discrimination['spk_idx_OTH'] + '/parallel100/wav_trimora/' + accent_discrimination['filename_OTH']
accent_discrimination.loc[accent_discrimination['mora_seq'].str.contains('-'), 'filepath_OTH'] = 'jvs_ver1/jvs' + accent_discrimination['spk_idx_OTH'] + '/parallel100/wav_bimora/' + accent_discrimination['filename_OTH']
accent_discrimination.loc[~accent_discrimination['mora_seq'].str.contains('-'), 'filepath_X'] = 'jvs_ver1/jvs' + accent_discrimination['spk_idx_X'] + '/parallel100/wav_trimora/' + accent_discrimination['filename_X']
accent_discrimination.loc[accent_discrimination['mora_seq'].str.contains('-'), 'filepath_X'] = 'jvs_ver1/jvs' + accent_discrimination['spk_idx_X'] + '/parallel100/wav_bimora/' + accent_discrimination['filename_X']

humaneval_folder_path = 'humaneval'
if os.path.isdir(humaneval_folder_path):
    pass
else:
    os.mkdir(humaneval_folder_path)

randint_test = [random.randint(0, 1) for _ in range(len(mora_discrimination))]
for i, (filepath_TGT, filepath_OTH, filepath_X, filename_TGT, filename_OTH, filename_X, randint) in enumerate(zip(mora_discrimination['filepath_TGT'], mora_discrimination['filepath_OTH'], mora_discrimination['filepath_X'], mora_discrimination['filename_TGT'], mora_discrimination['filename_OTH'], mora_discrimination['filename_X'], randint_test), start=1):
    triplet_idx = 'triplet'+str(i).zfill(4)
    triplet_i_folder_path = os.path.join(humaneval_folder_path, triplet_idx)
    if os.path.isdir(triplet_i_folder_path):
        pass
    else:
        os.mkdir(triplet_i_folder_path)
    shutil.copy(filepath_TGT, triplet_i_folder_path+'/TGT_'+filename_TGT)
    shutil.copy(filepath_OTH, triplet_i_folder_path+'/OTH_'+filename_OTH)
    shutil.copy(filepath_X, triplet_i_folder_path+'/X_'+filename_X)
    triplet_idx = 'P'+str(i).zfill(3)
    test_mora_folder_path = os.path.join(humaneval_folder_path, 'TestP')
    if os.path.isdir(test_mora_folder_path):
        pass
    else:
        os.mkdir(test_mora_folder_path)
    if randint == 0:
        shutil.copy(filepath_TGT, os.path.join(test_mora_folder_path, triplet_idx+'_A.wav'))
        shutil.copy(filepath_OTH, os.path.join(test_mora_folder_path, triplet_idx+'_B.wav'))
    else:
        shutil.copy(filepath_TGT, os.path.join(test_mora_folder_path, triplet_idx+'_B.wav'))
        shutil.copy(filepath_OTH, os.path.join(test_mora_folder_path, triplet_idx+'_A.wav'))
    shutil.copy(filepath_X, os.path.join(test_mora_folder_path, triplet_idx+'_X.wav'))
randint_test_file = os.path.join(test_mora_folder_path, 'randint.txt')
with open(randint_test_file, mode='w') as f:
    for i in randint_test:
        f.write(str(i))

randint_test = [random.randint(0, 1) for _ in range(len(accent_discrimination))]
for i, (filepath_TGT, filepath_OTH, filepath_X, filename_TGT, filename_OTH, filename_X, randint) in enumerate(zip(accent_discrimination['filepath_TGT'], accent_discrimination['filepath_OTH'], accent_discrimination['filepath_X'], accent_discrimination['filename_TGT'], accent_discrimination['filename_OTH'], accent_discrimination['filename_X'], randint_test), start=1):
    triplet_idx = 'triplet'+str(i+500).zfill(4)
    triplet_i_folder_path = os.path.join(humaneval_folder_path, triplet_idx)
    if os.path.isdir(triplet_i_folder_path):
        pass
    else:
        os.mkdir(triplet_i_folder_path)
    shutil.copy(filepath_TGT, triplet_i_folder_path+'/TGT_'+filename_TGT)
    shutil.copy(filepath_OTH, triplet_i_folder_path+'/OTH_'+filename_OTH)
    shutil.copy(filepath_X, triplet_i_folder_path+'/X_'+filename_X)
    triplet_idx = 'A'+str(i).zfill(3)
    test_accent_folder_path = os.path.join(humaneval_folder_path, 'TestA')
    if os.path.isdir(test_accent_folder_path):
        pass
    else:
        os.mkdir(test_accent_folder_path)
    if randint == 0:
        shutil.copy(filepath_TGT, os.path.join(test_accent_folder_path, triplet_idx+'_A.wav'))
        shutil.copy(filepath_OTH, os.path.join(test_accent_folder_path, triplet_idx+'_B.wav'))
    else:
        shutil.copy(filepath_TGT, os.path.join(test_accent_folder_path, triplet_idx+'_B.wav'))
        shutil.copy(filepath_OTH, os.path.join(test_accent_folder_path, triplet_idx+'_A.wav'))
    shutil.copy(filepath_X, os.path.join(test_accent_folder_path, triplet_idx+'_X.wav'))
randint_test_file = os.path.join(test_accent_folder_path, 'randint.txt')
with open(randint_test_file, mode='w') as f:
    for i in randint_test:
        f.write(str(i))
