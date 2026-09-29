import pandas as pd
import utils

df_mora_discrimination = pd.read_csv(utils.discrimination_csv('mora'), dtype={'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str})
df_accent_discrimination = pd.read_csv(utils.discrimination_csv('accent'), dtype={'spk_idx_TGT': str, 'spk_idx_OTH': str, 'spk_idx_X': str})

df_mora_eval = df_mora_discrimination.sample(n=500, random_state=1)
df_accent_eval = df_accent_discrimination.sample(n=500, random_state=1)
df_mora_eval.to_csv(utils.discrimination_csv('mora', True), index=False)
df_accent_eval.to_csv(utils.discrimination_csv('accent', True), index=False)

df_mora_eval.groupby(by=['contrast_type', 'TGT', 'OTH', 'context', 'spkTGTX', 'genderTGTX', 'pitchTGTX'])['filename_TGT'].count().reset_index().to_csv(utils.discrimination_csv('mora', True, '_stat'), index=False)
df_accent_eval.groupby(by=['num_mora', 'pitch_TGT', 'pitch_OTH', 'spkTGTX', 'genderTGTX'])['filename_TGT'].count().reset_index().to_csv(utils.discrimination_csv('accent', True, '_stat'), index=False)
