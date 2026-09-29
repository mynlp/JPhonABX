#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


STEP_COMMANDS = {
    'correct': lambda dry: ['bash', 'pipeline/correct_mistake.sh'] + ([] if dry else ['--apply']),
    'resample': lambda dry: [sys.executable, '-m', 'pipeline.convert_to_16kHz'] + (['--dry-run'] if dry else []),
    'align': lambda dry: [sys.executable, '-m', 'pipeline.align_morae'],
    'mora_seq': lambda dry: [sys.executable, '-m', 'pipeline.make_mora_seq_csv'],
    'pairs': lambda dry: [sys.executable, '-m', 'pipeline.make_abx_pairs'],
    'pitch': lambda dry: [sys.executable, '-m', 'pipeline.annotate_pitch'],
    'f0': lambda dry: [sys.executable, '-m', 'pipeline.annotate_f0'],
    'extract': lambda dry: [sys.executable, '-m', 'pipeline.extract_all_trimora_bimora'],
    'abx_dataset': lambda dry: [sys.executable, '-m', 'pipeline.make_abx_dataset'],
    'final': lambda dry: [sys.executable, '-m', 'pipeline.make_final_datasets'],
    'human_eval': lambda dry: [sys.executable, '-m', 'pipeline.human_evaluation'],
    # not part of DEFAULT_STEPS: only needed to regenerate the listening test material
    'triplet_folder': lambda dry: [sys.executable, '-m', 'pipeline.create_triplet_folder'],
}

DEFAULT_STEPS = [
    'correct',
    'resample',
    'align',
    'mora_seq',
    'pairs',
    'pitch',
    'f0',
    'extract',
    'abx_dataset',
    'final',
    'human_eval',
]


def run_step(step: str, dry_run: bool) -> None:
    if step not in STEP_COMMANDS:
        raise ValueError(f'Unknown step: {step}')
    command = STEP_COMMANDS[step](dry_run)
    print(f"\n=== Running step: {step} ===")
    print('Command:', ' '.join(command))
    completed = subprocess.run(command, check=False, cwd=REPO_ROOT)
    if completed.returncode != 0:
        raise RuntimeError(f"Step '{step}' failed with exit code {completed.returncode}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the full JPhonABX dataset construction pipeline.')
    parser.add_argument(
        '--steps',
        default=','.join(DEFAULT_STEPS),
        help='Comma-separated list of pipeline steps to run. Available: ' + ', '.join(STEP_COMMANDS.keys()),
    )
    parser.add_argument('--dry-run', action='store_true', help='Run correction and resampling in dry-run mode.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    steps = [step.strip() for step in args.steps.split(',') if step.strip()]
    for step in steps:
        run_step(step, args.dry_run)
    print('\nPipeline completed successfully.')


if __name__ == '__main__':
    main()
