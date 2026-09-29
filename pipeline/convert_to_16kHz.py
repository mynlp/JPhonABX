#!/usr/bin/env python3
"""Resample JVS wav files to 16 kHz and write to a separate folder.
"""
import argparse
import logging
from pathlib import Path

import soundfile as sf
from scipy.signal import resample


def resample_file(in_path: Path, out_path: Path, target_sr: int) -> bool:
    try:
        data, sr = sf.read(str(in_path))
    except Exception as e:
        logging.warning("Failed to read %s: %s", in_path, e)
        return False

    if sr == target_sr:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            sf.write(str(out_path), data, sr)
            return True
        except Exception as e:
            logging.warning("Failed to write %s: %s", out_path, e)
            return False

    number_of_samples = round(len(data) * float(target_sr) / sr)

    try:
        resampled = resample(data, number_of_samples)
    except Exception as e:
        logging.warning("Resampling failed for %s (sr=%s -> %s): %s", in_path, sr, target_sr, e)
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # write as float; user can convert subtype if needed
        sf.write(str(out_path), resampled, target_sr)
        return True
    except Exception as e:
        logging.warning("Failed to write %s: %s", out_path, e)
        return False


def main():
    parser = argparse.ArgumentParser(description="Batch resample JVS wavs to 16 kHz")
    parser.add_argument("--root", default="jvs_ver1", help="JVS root folder (default: jvs_ver1)")
    parser.add_argument("--spk-prefix", default="jvs", help="Speaker prefix (default: jvs)")
    parser.add_argument("--spk-start", type=int, default=1)
    parser.add_argument("--spk-end", type=int, default=100)
    parser.add_argument("--in-subdir", default="parallel100/wav24kHz16bit")
    parser.add_argument("--out-subdir", default="parallel100/wav16kHz")
    parser.add_argument("--pattern", default="VOICEACTRESS100_{:03d}.wav")
    parser.add_argument("--target-sr", type=int, default=16000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    root = Path(args.root)

    total = 0
    success = 0

    for i in range(args.spk_start, args.spk_end + 1):
        spk_idx = str(i).zfill(3)
        spk_dir = root / f"{args.spk_prefix}{spk_idx}" / args.in_subdir
        out_base = root / f"{args.spk_prefix}{spk_idx}" / args.out_subdir

        for j in range(1, 101):
            total += 1
            file_name = args.pattern.format(j)
            in_path = spk_dir / file_name
            out_path = out_base / file_name

            if not in_path.exists():
                logging.debug("Missing: %s", in_path)
                continue

            if args.dry_run:
                logging.info("Would resample: %s -> %s", in_path, out_path)
                success += 1
                continue

            ok = resample_file(in_path, out_path, args.target_sr)
            if ok:
                success += 1

    logging.info("Processed %d files (successful: %d)", total, success)


if __name__ == "__main__":
    main()
