import os
import re
from pydub import AudioSegment
import utils

FILENAME_RE = re.compile(r'^(VOICEACTRESS100_\d{3})_(\d+)_(\d+)\.wav$')

ROLES = ('TGT', 'OTH', 'X')
# For contrast_type geminate/nasal/vowel len, OTH == '-': the contrasted mora is deleted
# entirely, so OTH is a bimora clip while TGT and X stay trimora.
EN_HARD = {'geminate', 'nasal', 'vowel len'}


def parse_filename(filename: str):
    m = FILENAME_RE.match(filename)
    if not m:
        raise ValueError(f'Unexpected filename format: {filename}')
    base, start_ms, stop_ms = m.groups()
    file_idx = base.split('_')[1]
    return file_idx, int(start_ms), int(stop_ms)


def add_clip(clips, filename, spk_idx, category):
    file_idx, start_ms, stop_ms = parse_filename(filename)
    key = (spk_idx, file_idx)
    clips.setdefault(key, set()).add((filename, start_ms, stop_ms, category))


def collect_mora_discrimination_clips(clips, csv_path):
    dtypes = {f'spk_idx_{role}': str for role in ROLES}
    df = utils.read_csv(csv_path, dtype=dtypes)
    for row in df.itertuples(index=False):
        oth_category = 'bimora' if row.contrast_type in EN_HARD else 'trimora'
        add_clip(clips, row.filename_TGT, row.spk_idx_TGT, 'trimora')
        add_clip(clips, row.filename_OTH, row.spk_idx_OTH, oth_category)
        add_clip(clips, row.filename_X, row.spk_idx_X, 'trimora')


def collect_accent_discrimination_clips(clips, csv_path):
    dtypes = {f'spk_idx_{role}': str for role in ROLES}
    df = utils.read_csv(csv_path, dtype=dtypes)
    for row in df.itertuples(index=False):
        category = 'bimora' if row.num_mora == 2 else 'trimora'
        for role in ROLES:
            add_clip(clips, getattr(row, f'filename_{role}'), getattr(row, f'spk_idx_{role}'), category)


def collect_required_clips(humaneval: bool = False):
    """Map (spk_idx, file_idx) -> {(filename, start_ms, stop_ms, category)}."""
    clips = {}
    collect_mora_discrimination_clips(clips, utils.discrimination_csv('mora', humaneval))
    collect_accent_discrimination_clips(clips, utils.discrimination_csv('accent', humaneval))
    return clips


def extract_required(root: str = 'jvs_ver1', humaneval: bool = False):
    clips = collect_required_clips(humaneval)
    total = len(clips)

    for n, ((spk_idx, file_idx), segments) in enumerate(clips.items(), start=1):
        spk_p100_dir = f"{root}/jvs{spk_idx}/parallel100"
        wavefile = os.path.join(spk_p100_dir, f'wav16kHz/VOICEACTRESS100_{file_idx}.wav')
        if not os.path.isfile(wavefile):
            print(wavefile, 'does not exist.')
            continue
        wf = AudioSegment.from_wav(wavefile)

        for filename, start_ms, stop_ms, category in segments:
            out_dir = os.path.join(spk_p100_dir, f'wav_{category}')
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, filename)
            if os.path.isfile(out_path):
                continue
            wf[start_ms:stop_ms].export(out_path, format='wav')

        if n % 100 == 0 or n == total:
            print(f'{n}/{total} source files processed.')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='script to cut the trimora/bimora fragments referenced by the released triplet metadata')
    parser.add_argument('--humaneval', action='store_true',
                        help='only cut the fragments referenced by the 500-triplet human evaluation subsets')
    args = parser.parse_args()
    print(args.humaneval)
    extract_required(humaneval=args.humaneval)


if __name__ == '__main__':
    main()
