from collections import defaultdict
from pathlib import Path
import pandas as pd
from typing import List

silent_phonemes = ['sil', 'pau']
special_phonemes = ['cl', 'N']
vowels = ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u']
# consonants = ['b', 'by', 'ch', 'd', 'dy', 'f', 'g', 'gy', 'h', 'hy', 'j', 'k', 'ky', 'm', 'my', 'n', 'ny', 'p', 'py', 'r', 'ry', 's', 'sh', 't', 'ts', 'ty', 'v', 'w', 'y', 'z']


def process_speaker(spk_idx: int, root: str = 'jvs_ver1', corrected_base: str = 'jvs_hiho-master/aligned_labels_openjtalk') -> None:
    spk_idx_s = str(spk_idx).zfill(3)
    spk_p100_dir = f"{root}/jvs{spk_idx_s}/parallel100"
    spk_p100_dir_corrected = f"{corrected_base}/jvs{spk_idx_s}"
    phoneme_count = defaultdict(int)
    # phoneme_alignment_csv_list = []
    mora_count = defaultdict(int)
    # mora_alignment_csv_list = []

    for j in range(1, 101):
        file_idx = str(j).zfill(3)
        labelfile = Path(spk_p100_dir_corrected) / f"VOICEACTRESS100_{file_idx}.lab"
        if not labelfile.is_file():
            print(labelfile, 'does not exist.')
            continue

        # phoneme_alignment: List[List[str]] = []
        mora_alignment: List[List[str]] = []
        prev_phoneme = None
        prev_start = None
        prev_stop = "0.0000"

        with open(labelfile, mode='r') as f:
            for line in f:
                start, stop, phoneme = line.rstrip().split(' ')
                phoneme_count[phoneme] += 1
                # phoneme_alignment.append([start, stop, phoneme])
                try:
                    assert prev_stop == start
                except AssertionError:
                    print('warning: breaks in timing', labelfile, start, prev_stop)
                if phoneme in silent_phonemes:
                    if prev_phoneme is not None:
                        print(labelfile, start, stop, phoneme, 'error')
                        break
                    prev_phoneme = None
                    prev_start = None
                    prev_stop = stop
                elif phoneme in special_phonemes:
                    if prev_phoneme is not None:
                        print(labelfile, start, stop, phoneme, 'error')
                        break
                    mora_alignment.append([start, stop, phoneme])
                    mora_count[phoneme] += 1
                    prev_phoneme = None
                    prev_start = None
                    prev_stop = stop
                elif phoneme in vowels:
                    if prev_phoneme is not None:
                        mora_alignment.append([prev_start, stop, prev_phoneme + phoneme])
                        mora_count[prev_phoneme + phoneme] += 1
                    else:
                        mora_alignment.append([start, stop, phoneme])
                        mora_count[phoneme] += 1
                    prev_phoneme = None
                    prev_start = None
                    prev_stop = stop
                else:
                    if prev_phoneme is not None:
                        print(labelfile, start, stop, phoneme, 'error')
                        break
                    prev_phoneme = phoneme
                    prev_start = start
                    prev_stop = stop
        # phoneme_alignment_csv = pd.DataFrame(phoneme_alignment, columns=['start', 'stop', 'phoneme'])
        # phoneme_alignment_csv_list.append(phoneme_alignment_csv)
        mora_alignment_csv = pd.DataFrame(mora_alignment, columns=['start', 'stop', 'mora'])
        # mora_alignment_csv_list.append(mora_alignment_csv)
        mora_alignment_csv_dir = Path(spk_p100_dir) / 'mora_alignment_csv'
        mora_alignment_csv_dir.mkdir(parents=True, exist_ok=True)
        mora_alignment_csv.to_csv(mora_alignment_csv_dir / f'mora_alignment_{file_idx}.csv', index=False)

    # print('len_phoneme_count:', len(phoneme_count))
    # print('phoneme_count:', phoneme_count)
    # print('len_mora_count:', len(mora_count))
    # print('mora_count:', mora_count)
    # print('len_mora_alignment_csv_list', len(mora_alignment_csv_list))


def main():
    for i in range(1, 101):
        process_speaker(i)


if __name__ == '__main__':
    main()
