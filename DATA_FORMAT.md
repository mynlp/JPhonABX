# JPhonABX metadata file format

This document describes the columns of the two released metadata files in `data/`, `mora_discrimination.csv` and `accent_discrimination.csv`. See the main [README](README.md) for how these files are used.

## `mora_discrimination.csv`

Each row is one ABX triplet for mora discrimination.

| Column | Meaning |
|---|---|
| `contrast_type` | `initial`/`medial`/`final`/`nasal`/`geminate`/`vowel len` |
| `TGT`, `OTH` | The contrasted mora. `OTH` is `-` for the `geminate`/`nasal`/`vowel len` contrasts, where the contrast is the presence vs. absence of the mora |
| `X` | The mora at the contrasted position in X. `X` always equals `TGT` |
| `context` | The mora sequence shared by _target_, _other_, and X, with `_` marking the contrasted position (e.g. `_isu`, `ne_to`, `see_`) |
| `filename_TGT`/`filename_OTH`/`filename_X` | Source JVS recording filename |
| `spk_idx_TGT`/`spk_idx_OTH`/`spk_idx_X` | JVS speaker index (`spk_idx_OTH` always equals `spk_idx_TGT`) |
| `pitch_TGT`/`pitch_OTH`/`pitch_X` | Pitch accent pattern (`H`/`L` per mora). `pitch_TGT` and `pitch_OTH` are the same for the `initial`/`medial`/`final` contrasts; for the `nasal`/`geminate`/`vowel len` contrasts, their first and last labels are the same. In both cases, all-`H` and all-`L` patterns (e.g. `HHH` and `LLL`) count as the same |
| `mora_seq_TGT`/`mora_seq_OTH`/`mora_seq_X` | Mora sequence (`mora_seq_X` always equals `mora_seq_TGT`). A `-` marks a two-mora fragment, standing in for the absent middle mora |
| `gender_TGT`/`gender_OTH`/`gender_X` | Speaker gender (`M`/`F`). `gender_OTH` always equals `gender_TGT` |
| `spkTGTX` | Whether _target_ and X share the same speaker (`match`/`unmatch`) |
| `genderTGTX` | Whether _target_ and X share the same speaker gender (`match`/`unmatch`) |
| `pitchTGTX` | Whether _target_ and X share the same pitch accent pattern (`match`/`unmatch`) |

Example row:

```
contrast_type,TGT,OTH,X,context,filename_TGT,spk_idx_TGT,pitch_TGT,mora_seq_TGT,gender_TGT,filename_OTH,spk_idx_OTH,pitch_OTH,mora_seq_OTH,gender_OTH,filename_X,spk_idx_X,pitch_X,mora_seq_X,gender_X,spkTGTX,genderTGTX,pitchTGTX
initial,ba,pa,ba,_isu,VOICEACTRESS100_010_4282_4672.wav,057,HHH,baisu,F,VOICEACTRESS100_068_3162_3612.wav,057,HHH,paisu,F,VOICEACTRESS100_010_3802_4142.wav,063,HLL,baisu,F,unmatch,match,unmatch
```

## `accent_discrimination.csv`

Each row is one ABX triplet for accent discrimination.

| Column | Meaning |
|---|---|
| `filename_TGT`/`filename_OTH`/`filename_X` | Source JVS recording filename |
| `spk_idx_TGT`/`spk_idx_OTH`/`spk_idx_X` | JVS speaker index |
| `pitch_TGT`/`pitch_OTH`/`pitch_X` | Pitch accent pattern (`H`/`L` per mora). `pitch_X` always equals `pitch_TGT`, with all-`H` and all-`L` patterns (e.g. `HH` and `LL`) counting as the same |
| `gender_TGT`/`gender_OTH`/`gender_X` | Speaker gender (`M`/`F`). `gender_OTH` always equals `gender_TGT` |
| `spkTGTX` | Whether _target_ and X share the same speaker (`match`/`unmatch`) |
| `genderTGTX` | Whether _target_ and X share the same speaker gender (`match`/`unmatch`) |
| `mora_seq` | Mora sequence, shared by TGT, OTH, and X. A `-` marks a two-mora fragment, standing in for the absent middle mora |
| `num_mora` | Number of morae in the shared mora sequence |

Example row:

```
filename_TGT,spk_idx_TGT,pitch_TGT,gender_TGT,filename_OTH,spk_idx_OTH,pitch_OTH,gender_OTH,filename_X,spk_idx_X,pitch_X,gender_X,spkTGTX,genderTGTX,mora_seq,num_mora
VOICEACTRESS100_065_2522_2692.wav,083,LL,F,VOICEACTRESS100_100_3702_3942.wav,083,LH,F,VOICEACTRESS100_098_2582_2772.wav,083,HH,F,match,match,ba-a,2
```
