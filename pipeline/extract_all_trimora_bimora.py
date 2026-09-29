import os
# import wave
import pandas as pd
from math import log
from pydub import AudioSegment
import utils

HL_LL_boundary = -0.13
LL_LH_boundary = 0.054


def check_pitch_label(pitch, f0_1, f0_2):
    valid = True
    log_f0_ratio = log(f0_2) - log(f0_1)
    if pitch == 'LH':
        if log_f0_ratio < LL_LH_boundary:
            valid = False
    elif pitch == 'HL':
        if log_f0_ratio > HL_LL_boundary:
            valid = False
    else:
        if log_f0_ratio < HL_LL_boundary or log_f0_ratio > LL_LH_boundary:
            valid = False
    return valid


def extract_all(root: str = 'jvs_ver1'):
    trimora_csv = utils.read_csv('trimora.csv')
    bimora_csv = utils.read_csv('bimora.csv')
    wav_files_info = []

    for i in range(1, 101):
        spk_idx = str(i).zfill(3)
        spk_p100_dir = f"{root}/jvs{spk_idx}/parallel100"

        for j in range(1, 101):
            file_idx = str(j).zfill(3)
            wavefile = os.path.join(spk_p100_dir, f'wav16kHz/VOICEACTRESS100_{file_idx}.wav')
            if not os.path.isfile(wavefile):
                print(wavefile, 'does not exist.')
                continue
            # wf = wave.open(wavefile, 'rb')
            # print('type: ', type(wf))
            # ch = wf.getnchannels()
            # print('チャンネル数:', ch) # モノラル: 1，ステレオ: 2
            # width = wf.getsampwidth()
            # print('サンプル幅:', width) # バイト数 (1byte=8bit)
            # fr = wf.getframerate()
            # print('サンプリング周波数:', fr)
            # fn = wf.getnframes()
            # print('フレーム数:', fn) # フレームの数
            # print('パラメータ:', wf.getparams())
            # data = wf.readframes(fn)
            # wf.close()
            wf = AudioSegment.from_wav(wavefile)

            mora_alignment_csv_path = os.path.join(spk_p100_dir, f'mora_alignment_csv/mora_alignment_{file_idx}.csv')
            if not os.path.isfile(mora_alignment_csv_path):
                print(mora_alignment_csv_path, 'does not exist.')
                continue
            mora_alignment_csv = utils.read_csv(mora_alignment_csv_path, dtype={'start': float, 'stop': float})
            if 'pitch' not in mora_alignment_csv.columns:
                print(mora_alignment_csv_path, 'pitch information is not annotated.')
                continue

            # trimora
            trimora_in_wavefile = trimora_csv[trimora_csv['filename'] == f'VOICEACTRESS100_{file_idx}.lab']
            trimora_in_wavefile_tmp = trimora_in_wavefile.merge(mora_alignment_csv[['start', 'mora', 'pitch', 'f0']], how='left', left_on='idx', right_on=mora_alignment_csv.index)
            assert (trimora_in_wavefile_tmp['first_mora'] == trimora_in_wavefile_tmp['mora']).all(), 'spk_idx: '+spk_idx+' '+'file_idx: '+file_idx
            trimora_in_wavefile_tmp.drop(columns=['mora'], inplace=True)
            trimora_in_wavefile_tmp.rename(columns={'pitch': 'first_pitch', 'f0': 'first_f0'}, inplace=True)
            trimora_in_wavefile_tmp['middle_mora_idx'] = trimora_in_wavefile_tmp['idx'] + 1
            trimora_in_wavefile_tmp = trimora_in_wavefile_tmp.merge(mora_alignment_csv[['start', 'stop', 'mora', 'pitch', 'f0']], how='left', left_on='middle_mora_idx', right_on=mora_alignment_csv.index)
            assert (trimora_in_wavefile_tmp['middle_mora'] == trimora_in_wavefile_tmp['mora']).all(), 'spk_idx: '+spk_idx+' '+'file_idx: '+file_idx
            trimora_in_wavefile_tmp.drop(columns=['middle_mora_idx', 'mora'], inplace=True)
            trimora_in_wavefile_tmp.rename(columns={'pitch': 'middle_pitch', 'f0': 'middle_f0', 'start_x': 'start', 'start_y': 'boundary1', 'stop': 'boundary2'}, inplace=True)
            trimora_in_wavefile_tmp['last_mora_idx'] = trimora_in_wavefile_tmp['idx'] + 2
            trimora_in_wavefile_with_timestamp = trimora_in_wavefile_tmp.merge(mora_alignment_csv[['stop', 'mora', 'pitch', 'f0']], how='left', left_on='last_mora_idx', right_on=mora_alignment_csv.index)
            assert (trimora_in_wavefile_with_timestamp['last_mora'] == trimora_in_wavefile_with_timestamp['mora']).all(), 'spk_idx: '+spk_idx+' '+'file_idx: '+file_idx
            trimora_in_wavefile_with_timestamp.drop(columns=['last_mora_idx', 'mora'], inplace=True)
            trimora_in_wavefile_with_timestamp.rename(columns={'pitch': 'last_pitch', 'f0': 'last_f0'}, inplace=True)
            trimora_in_wavefile_with_timestamp['pitch'] = trimora_in_wavefile_with_timestamp['first_pitch'] + trimora_in_wavefile_with_timestamp['middle_pitch'] + trimora_in_wavefile_with_timestamp['last_pitch']
            trimora_in_wavefile_with_timestamp.drop(columns=['first_pitch', 'middle_pitch', 'last_pitch'], inplace=True)
            trimora_in_wavefile_with_timestamp['f0'] = trimora_in_wavefile_with_timestamp.apply(lambda key: [key['first_f0'], key['middle_f0'], key['last_f0']], axis=1)
            trimora_in_wavefile_with_timestamp.drop(columns=['first_f0', 'middle_f0', 'last_f0'], inplace=True)

            # bimora
            bimora_in_wavefile = bimora_csv[bimora_csv['filename'] == f'VOICEACTRESS100_{file_idx}.lab']
            bimora_in_wavefile_tmp = bimora_in_wavefile.merge(mora_alignment_csv[['start', 'mora', 'pitch', 'f0']], how='left', left_on='idx', right_on=mora_alignment_csv.index)
            assert (bimora_in_wavefile_tmp['first_mora'] == bimora_in_wavefile_tmp['mora']).all(), 'spk_idx: '+spk_idx+' '+'file_idx: '+file_idx
            bimora_in_wavefile_tmp.drop(columns=['mora'], inplace=True)
            bimora_in_wavefile_tmp.rename(columns={'pitch': 'first_pitch', 'f0': 'first_f0'}, inplace=True)
            bimora_in_wavefile_tmp['last_mora_idx'] = bimora_in_wavefile_tmp['idx'] + 1
            bimora_in_wavefile_with_timestamp = bimora_in_wavefile_tmp.merge(mora_alignment_csv[['start', 'stop', 'mora', 'pitch', 'f0']], how='left', left_on='last_mora_idx', right_on=mora_alignment_csv.index)
            assert (bimora_in_wavefile_with_timestamp['last_mora'] == bimora_in_wavefile_with_timestamp['mora']).all(), 'spk_idx: '+spk_idx+' '+'file_idx: '+file_idx
            bimora_in_wavefile_with_timestamp.drop(columns=['last_mora_idx', 'mora'], inplace=True)
            bimora_in_wavefile_with_timestamp.rename(columns={'pitch': 'last_pitch', 'f0': 'last_f0', 'start_x': 'start', 'start_y': 'boundary'}, inplace=True)
            bimora_in_wavefile_with_timestamp['pitch'] = bimora_in_wavefile_with_timestamp['first_pitch'] + bimora_in_wavefile_with_timestamp['last_pitch']
            bimora_in_wavefile_with_timestamp.drop(columns=['first_pitch', 'last_pitch'], inplace=True)
            bimora_in_wavefile_with_timestamp['f0'] = bimora_in_wavefile_with_timestamp.apply(lambda key: [key['first_f0'], key['last_f0']], axis=1)
            bimora_in_wavefile_with_timestamp.drop(columns=['first_f0', 'last_f0'], inplace=True)

            # write trimmed wavs and collect valid ones
            wav_trimora_path = os.path.join(spk_p100_dir, 'wav_trimora')
            os.makedirs(wav_trimora_path, exist_ok=True)
            for row in trimora_in_wavefile_with_timestamp.itertuples(index=False):
                start_ms = int(row.start * 1000)
                stop_ms = int(row.stop * 1000)
                if stop_ms - start_ms < 230:
                    continue
                f0_vals = row.f0
                if row.middle_mora == 'cl':
                    valid = check_pitch_label(row.pitch[::2], f0_vals[0], f0_vals[2])
                else:
                    valid = check_pitch_label(row.pitch[:2], f0_vals[0], f0_vals[1])
                    if valid:
                        valid = check_pitch_label(row.pitch[1:], f0_vals[1], f0_vals[2])
                if valid:
                    wf_out = wf[start_ms:stop_ms]
                    wavefile_out = os.path.join(wav_trimora_path, f'VOICEACTRESS100_{file_idx}_{start_ms}_{stop_ms}.wav')
                    wf_out.export(wavefile_out, format='wav')
                    wav_files_info.append([f'VOICEACTRESS100_{file_idx}_{start_ms}_{stop_ms}.wav', spk_idx, row.first_mora, row.middle_mora, row.last_mora, row.pitch, row.f0])

            wav_bimora_path = os.path.join(spk_p100_dir, 'wav_bimora')
            os.makedirs(wav_bimora_path, exist_ok=True)
            for row in bimora_in_wavefile_with_timestamp.itertuples(index=False):
                start_ms = int(row.start * 1000)
                stop_ms = int(row.stop * 1000)
                if stop_ms - start_ms < 150:
                    continue
                f0_vals = row.f0
                valid = check_pitch_label(row.pitch, f0_vals[0], f0_vals[1])
                if valid:
                    wf_out = wf[start_ms:stop_ms]
                    wavefile_out = os.path.join(wav_bimora_path, f'VOICEACTRESS100_{file_idx}_{start_ms}_{stop_ms}.wav')
                    wf_out.export(wavefile_out, format='wav')
                    wav_files_info.append([f'VOICEACTRESS100_{file_idx}_{start_ms}_{stop_ms}.wav', spk_idx, row.first_mora, '-', row.last_mora, row.pitch, row.f0])

    wav_files_info_csv = pd.DataFrame(wav_files_info, columns=['filename', 'spk_idx', 'first_mora', 'middle_mora', 'last_mora', 'pitch', 'f0'])
    utils.write_csv(wav_files_info_csv, 'wav_files_info.csv', index=False)


def main():
    extract_all()


if __name__ == '__main__':
    main()
