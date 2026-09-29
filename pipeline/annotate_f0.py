import os
from scipy.io import wavfile
import crepe
import utils


def process_f0(root: str = 'jvs_ver1'):
    for i in range(1, 101):
        spk_idx = str(i).zfill(3)
        spk_dir = f"{root}/jvs{spk_idx}/parallel100"
        for j in range(1, 101):
            file_idx = str(j).zfill(3)
            audio_file = os.path.join(spk_dir, f"wav16kHz/VOICEACTRESS100_{file_idx}.wav")
            if not os.path.isfile(audio_file):
                print(audio_file, 'does not exist.')
            else:
                mora_alignment_path = os.path.join(spk_dir, f"mora_alignment_csv/mora_alignment_{file_idx}.csv")
                mora_alignment = utils.read_csv(mora_alignment_path)
                sr, wf = wavfile.read(audio_file)
                time, frequency, confidence, activation = crepe.predict(wf, sr, viterbi=True)
                mora_alignment['f0'] = mora_alignment.apply(lambda key: frequency[int(key['start']*100)+1:int(key['stop']*100)+1].mean(), axis=1)
                utils.write_csv(mora_alignment, mora_alignment_path, index=False)


def main():
    process_f0()


if __name__ == '__main__':
    main()
