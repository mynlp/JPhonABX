import os
import difflib
from transformers import pipeline
from parse_accent import parse_pitch_accent
from surface2katakana_with_acc import katakana_to_phones
import utils

pitch_symbols = ['_', '↑', '↓']
special_phonemes = ['cl', 'N']
vowels = ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u']
consonants = ['b', 'by', 'ch', 'd', 'dy', 'f', 'g', 'gy', 'h', 'hy', 'j', 'k', 'ky', 'm', 'my', 'n', 'ny', 'p', 'py', 'r', 'ry', 's', 'sh', 't', 'ts', 'ty', 'v', 'w', 'y', 'z']

def phoneme_to_mora(phoneme_seq_with_pitch):
    mora_seq = []
    prev_phoneme = None
    for phoneme in phoneme_seq_with_pitch.split(' '):
        if phoneme in pitch_symbols:
            if prev_phoneme is not None:
                print(phoneme, 'error')
                break
            mora_seq.append(phoneme)
        elif phoneme in special_phonemes:
            if prev_phoneme is not None:
                print(phoneme, 'error')
                break
            mora_seq.append(phoneme)
        elif phoneme in vowels:
            if prev_phoneme is not None:
                mora_seq.append(prev_phoneme+phoneme)
            else:
                mora_seq.append(phoneme)
            prev_phoneme = None
        else:
            if prev_phoneme is not None:
                print(phoneme, 'error')
                break
            prev_phoneme = phoneme
    return mora_seq

model_id = "AkitoP/whisper-large-v3-japense-phone_accent"

pipe = pipeline(
    task="automatic-speech-recognition",
    model=model_id
)

correction_dict = {'u': ['we', 'wo'], 'vi': ['byu'], 'mi': ['byu'], 'mi': ['be'], 'chi': ['tsu', 'shu'], 'pa': ['bi'], 'te': ['di'], 'ge': ['rya'],
                   'ki yu': ['kyu'], 'ki yo': ['kyo'],
                   'mi u': ['myu'],
                   'vi u': ['byu'], 'bi yu': ['byu'], 'bi o': ['byo'], 'bi yo': ['byo'],
                   'i a': ['ya'],
                   'di a': ['rya'], 'di ya': ['rya'], 'ri u': ['ryu'], 'ri yu': ['ryu'],
                   'mu i': ['wi'], 'u e': ['we'], 'u o': ['wo'],
                   'N yu': ['nyu'], 'tsu yu': ['chu'], 'tsu ya': ['tsa'], 'fu o': ['fo'],
                   'ri': ['ru i'], 'wa': ['o a'], 'wo': ['u o'], 'sha': ['shi ha'], 'za': ['zu a'], 'da': ['de a']}
# pred: gold

def correct_labels(sm, gold_mora_seq, gold_mora_seq_lower, pred_mora_seq_with_pitch, spk_idx, file_idx):
    gold_mora_seq_with_pitch = []
    error = False
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            gold_mora_seq_with_pitch += gold_mora_seq[i1:i2]
        elif tag == 'insert':
            for symbol in pred_mora_seq_with_pitch[j1:j2]:
                if symbol in pitch_symbols:
                    gold_mora_seq_with_pitch += [symbol]
        elif tag == 'replace':
            if any(pitch_symbol in pred_mora_seq_with_pitch[j1:j2] for pitch_symbol in pitch_symbols):
                k = i1
                l = j1
                seq_to_add = []
                if l < j2 and pred_mora_seq_with_pitch[l] in pitch_symbols:
                    seq_to_add.append(pred_mora_seq_with_pitch[l])
                    l += 1
                while k < i2 or l < j2:
                    if ((len(seq_to_add) > 0 and seq_to_add[-1] == '_') or (k == 0 and l == 0)) and k < i2 and l < j2-2 and pred_mora_seq_with_pitch[l+1] == '↑' and correction_dict.get(pred_mora_seq_with_pitch[l]+' '+pred_mora_seq_with_pitch[l+2]) is not None and gold_mora_seq_lower[k] in correction_dict[pred_mora_seq_with_pitch[l]+' '+pred_mora_seq_with_pitch[l+2]]:
                        # x → _ y ↑ z のパターンは _ x ↑
                        seq_to_add += [gold_mora_seq[k], '↑']
                        k += 1
                        l += 3
                    elif k < i2 and l < j2-1 and correction_dict.get(pred_mora_seq_with_pitch[l]+' '+pred_mora_seq_with_pitch[l+1]) is not None and gold_mora_seq_lower[k] in correction_dict[pred_mora_seq_with_pitch[l]+' '+pred_mora_seq_with_pitch[l+1]]:
                        # x → y z のパターンは x
                        seq_to_add.append(gold_mora_seq[k])
                        k += 1
                        l += 2
                    elif k < i2-1 and l < j2 and correction_dict.get(pred_mora_seq_with_pitch[l]) is not None and gold_mora_seq_lower[k]+' '+gold_mora_seq_lower[k+1] in correction_dict[pred_mora_seq_with_pitch[l]]:
                        # x y → z のパターンは x y
                        seq_to_add += gold_mora_seq[k:k+2]
                        k += 2
                        l += 1
                    elif k < i2 and l < j2 and correction_dict.get(pred_mora_seq_with_pitch[l]) is not None and gold_mora_seq_lower[k] in correction_dict[pred_mora_seq_with_pitch[l]]:
                        # x → y のパターンは x
                        seq_to_add.append(gold_mora_seq[k])
                        k += 1
                        l += 1
                    elif k < i2 and gold_mora_seq_lower[k] == 'cl':
                        # cl → のパターン
                        if k > 0 and pred_mora_seq_with_pitch[l] == gold_mora_seq_lower[k-1][-1]:
                            # cl → x かつxが直前の音の延長
                            l += 1
                        seq_to_add.append(gold_mora_seq[k])
                        k += 1
                    elif l < j2 and pred_mora_seq_with_pitch[l] == 'cl':
                        l += 1
                    elif k < i2 and gold_mora_seq_lower[k] == 'N':
                        # N → のパターン
                        if k > 0 and pred_mora_seq_with_pitch[l] == gold_mora_seq_lower[k-1][-1]:
                            # N → x かつxが直前の音の延長
                            l += 1
                        elif k < len(gold_mora_seq_lower)-1 and pred_mora_seq_with_pitch[l] in vowels and pred_mora_seq_with_pitch[l] == gold_mora_seq_lower[k+1]:
                            # N → x かつxが直後の母音へ接続
                            l += 1
                        else:
                            pass
                        seq_to_add.append(gold_mora_seq[k])
                        k += 1
                    elif l < j2 and pred_mora_seq_with_pitch[l] == 'N':
                        l += 1
                    elif k < i2 and l < j2 and (gold_mora_seq_lower[k][-1] == pred_mora_seq_with_pitch[l][-1] or gold_mora_seq_lower[k][:-1] == pred_mora_seq_with_pitch[l][:-1] or gold_mora_seq_lower[k][0] == pred_mora_seq_with_pitch[l][0] or (gold_mora_seq_lower[k] in vowels and pred_mora_seq_with_pitch[l] in vowels)):
                        # 母音が一致 or 子音が一致（byu/beなども） or 両方母音
                        seq_to_add.append(gold_mora_seq[k])
                        k += 1
                        l += 1
                    elif k > 0 and gold_mora_seq_lower[k] == gold_mora_seq_lower[k-1][-1]:
                        # goldが直前の音の延長
                        seq_to_add.append(gold_mora_seq[k])
                        k += 1
                    elif k > 0 and l < j2 and pred_mora_seq_with_pitch[l] == gold_mora_seq_lower[k-1][-1]:
                        # predが直前の音の延長
                        l += 1
                    else:
                        break
                    if l < j2 and pred_mora_seq_with_pitch[l] in pitch_symbols:
                        seq_to_add.append(pred_mora_seq_with_pitch[l])
                        l += 1
                if k == i2-1 and k < len(gold_mora_seq_lower)-1 and l == j2 and gold_mora_seq_lower[k] in vowels and gold_mora_seq_lower[k] == gold_mora_seq_lower[k+1]:
                    # goldが直後の母音へ接続
                    seq_to_add.append(gold_mora_seq[k])
                    k += 1
                if k == i2 and l == j2-1 and pred_mora_seq_with_pitch[l] in vowels and pred_mora_seq_with_pitch[l] == gold_mora_seq_lower[k]:
                    # predが直後の母音へ接続
                    # N -> e, N -> o,
                    l += 1
                if k == i2 and l == j2:
                    print('spk_idx', spk_idx, 'file_idx', file_idx, gold_mora_seq[i1:i2], pred_mora_seq_with_pitch[j1:j2])
                    gold_mora_seq_with_pitch += seq_to_add
                else:
                    print('error:', 'spk_idx', spk_idx, 'file_idx', file_idx)
                    print(gold_mora_seq[i1:i2])
                    print(pred_mora_seq_with_pitch[j1:j2])
                    print(tag, i1, i2, j1, j2)
                    print(gold_mora_seq)
                    print(pred_mora_seq_with_pitch)
                    error = True
                    break
            else:
                gold_mora_seq_with_pitch += gold_mora_seq[i1:i2]
        else: # 'delete'
            gold_mora_seq_with_pitch += gold_mora_seq[i1:i2]
    return gold_mora_seq_with_pitch, error

def annotate(audio_file, gold_mora_seq, spk_idx, file_idx):
    result = pipe(audio_file)["text"]
    # print(result)
    phoneme_seq_with_pitch = katakana_to_phones(result)
    # print(phoneme_seq_with_pitch)
    pred_mora_seq_with_pitch = phoneme_to_mora(phoneme_seq_with_pitch)
    # print(pred_mora_seq_with_pitch)
    gold_mora_seq_lower = [s.lower() if s != 'N' else s for s in gold_mora_seq]
    sm = difflib.SequenceMatcher(None, gold_mora_seq_lower, pred_mora_seq_with_pitch)
    gold_mora_seq_with_pitch, error = correct_labels(sm, gold_mora_seq, gold_mora_seq_lower, pred_mora_seq_with_pitch, spk_idx, file_idx)
    return gold_mora_seq_with_pitch, error

def process_all(root: str = 'jvs_ver1'):
    for i in range(1, 101):
        spk_idx = str(i).zfill(3)
        spk_dir = f"{root}/jvs{spk_idx}/parallel100"
        for j in range(1, 101):
            file_idx = str(j).zfill(3)
            audio_file = os.path.join(spk_dir, f"wav24kHz16bit/VOICEACTRESS100_{file_idx}.wav")
            if not os.path.isfile(audio_file):
                print(audio_file, 'does not exist.')
            else:
                mora_alignment_path = os.path.join(spk_dir, f"mora_alignment_csv/mora_alignment_{file_idx}.csv")
                mora_alignment = utils.read_csv(mora_alignment_path)
                gold_mora_seq = mora_alignment['mora'].tolist()
                gold_mora_seq_with_pitch, error = annotate(audio_file, gold_mora_seq, spk_idx, file_idx)
                if not error:
                    pitch_seq = list(parse_pitch_accent(gold_mora_seq_with_pitch).replace('0', 'L').replace('1', 'H'))
                    # print(pitch_seq)
                    mora_alignment['pitch'] = pitch_seq
                    utils.write_csv(mora_alignment, mora_alignment_path, index=False)


def main():
    process_all()


if __name__ == '__main__':
    main()
