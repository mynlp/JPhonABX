"""Common utilities for dataset scripts."""
from pathlib import Path
from typing import Iterator
import soundfile as sf
import pandas as pd


def ensure_dir(path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)


def speaker_dirs(root: str = "jvs_ver1", prefix: str = "jvs", start: int = 1, end: int = 100) -> Iterator[Path]:
    for i in range(start, end + 1):
        yield Path(root) / f"{prefix}{str(i).zfill(3)}"


def iter_audio_files(root: str = "jvs_ver1", prefix: str = "jvs", start: int = 1, end: int = 100, subdir: str = "parallel100/wav24kHz16bit", pattern: str = "VOICEACTRESS100_{:03d}.wav"):
    for i in range(start, end + 1):
        spk_idx = str(i).zfill(3)
        base = Path(root) / f"{prefix}{spk_idx}" / subdir
        for j in range(1, 101):
            yield base / pattern.format(j)


def read_wav(path: str):
    return sf.read(str(path))


def read_csv(path: str, **kwargs):
    return pd.read_csv(path, **kwargs)


ROLES = ('TGT', 'OTH', 'X')


DATA_DIR = 'data'


def discrimination_csv(contrast: str, humaneval: bool = False, suffix: str = '') -> str:
    return f"{DATA_DIR}/{'humaneval_' if humaneval else ''}{contrast}_discrimination{suffix}.csv"


def referenced_fragments(humaneval: bool = False):
    """{(spk_idx, filename)} referenced as TGT/OTH/X by the released triplet metadata."""
    fragments = set()
    for contrast in ('mora', 'accent'):
        df = read_csv(discrimination_csv(contrast, humaneval),
                      dtype={f'spk_idx_{role}': str for role in ROLES})
        for role in ROLES:
            fragments.update(zip(df[f'spk_idx_{role}'], df[f'filename_{role}']))
    return fragments


def write_csv(df, path: str, **kwargs):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(p), **kwargs)
