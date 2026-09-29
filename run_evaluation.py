#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


FLOW_STEPS = {
    'with-context': ['features', 'score'],
    'without-context': ['fragments', 'features', 'score'],
}

CONTRASTS = ['mora', 'accent']


def step_commands(step: str, flow: str, args: argparse.Namespace) -> list:
    humaneval = ['--humaneval'] if args.humaneval else []

    if step == 'fragments':
        return [[sys.executable, '-m', 'evaluation.extract_required_trimora_bimora'] + humaneval]

    if step == 'features':
        if flow == 'with-context':
            # per-utterance features cover every triplet CSV, so they are never subset-specific
            return [[sys.executable, '-m', 'evaluation.extract_feature_per_file', args.model]]
        return [[sys.executable, '-m', 'evaluation.extract_feature_per_fragment', args.model] + humaneval]

    script = 'evaluation.evaluate_models' if flow == 'with-context' else 'evaluation.evaluate_models_fragment'
    return [[sys.executable, '-m', script, args.model, args.distance, contrast, args.layer] + humaneval
            for contrast in CONTRASTS]


def run_step(step: str, flow: str, args: argparse.Namespace) -> None:
    print(f"\n=== Running step: {step} ===")
    for command in step_commands(step, flow, args):
        print('Command:', ' '.join(command))
        if args.dry_run:
            continue
        completed = subprocess.run(command, check=False, cwd=REPO_ROOT)
        if completed.returncode != 0:
            raise RuntimeError(f"Step '{step}' failed with exit code {completed.returncode}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run a JPhonABX evaluation flow end to end.')
    parser.add_argument('flow', choices=sorted(FLOW_STEPS), help='which evaluation flow to run')
    parser.add_argument('--model', required=True, help='Hugging Face model name, e.g. imprt/kushinada-hubert-base')
    parser.add_argument('--distance', help='distance used for DTW, e.g. cosine (required for the score step)')
    parser.add_argument('--layer', help='transformer layer to score (required for the score step)')
    parser.add_argument('--humaneval', action='store_true',
                        help='use the 500-triplet human evaluation subsets instead of the full dataset')
    parser.add_argument('--steps', help='comma-separated subset of the flow steps to run')
    parser.add_argument('--dry-run', action='store_true', help='print the commands without running them')
    args = parser.parse_args()

    flow_steps = FLOW_STEPS[args.flow]
    if args.steps:
        args.steps = [step.strip() for step in args.steps.split(',') if step.strip()]
        unknown = [step for step in args.steps if step not in flow_steps]
        if unknown:
            parser.error(f"unknown step(s) for {args.flow}: {', '.join(unknown)}. Available: {', '.join(flow_steps)}")
    else:
        args.steps = flow_steps

    if 'score' in args.steps and not (args.distance and args.layer):
        parser.error('--distance and --layer are required for the score step')
    return args


def main() -> None:
    args = parse_args()
    for step in args.steps:
        run_step(step, args.flow, args)
    print('\nEvaluation completed successfully.')


if __name__ == '__main__':
    main()
