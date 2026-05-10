import argparse
import asyncio
import pathlib

from evaluation.evaluator import evaluate
from evaluation.extractor import extract_gold_markdown, extract_prediction_markdown
from evaluation.other_util import setup_logger


def main():
    setup_logger()

    parser = argparse.ArgumentParser(description='FindDeepResearch End-to-End Evaluation')
    parser.add_argument('--prediction_folder', type=str, required=True, help='Path to prediction folder')
    parser.add_argument('--track', type=str, required=True, help='findocresearch or findeepresearch')
    parser.add_argument('--model', type=str, default='gpt-4.1', help='Model name')
    parser.add_argument('--extraction_only', action='store_true', help='Run only extraction phase')
    parser.add_argument('--evaluation_only', action='store_true', help='Run only evaluation phase')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing results')

    args = parser.parse_args()

    # Ground Truth Extraction
    if not args.extraction_only:
        asyncio.get_event_loop().run_until_complete(
            extract_gold_markdown(
                track=args.track,
                model=args.model,
                overwrite=args.overwrite
            )
        )

    # Prediction Extraction
    extractor_save_folder = (pathlib.Path(args.prediction_folder).parent / 'converted').as_posix()
    if not args.evaluation_only:
        asyncio.get_event_loop().run_until_complete(
            extract_prediction_markdown(
                prediction_folder=args.prediction_folder,
                save_folder=extractor_save_folder,
                model=args.model,
                track=args.track,
                overwrite=args.overwrite
            )
        )

    # Evaluation
    evaluator_save_folder = (pathlib.Path(args.prediction_folder).parent / 'evaluation').as_posix()
    if not args.extraction_only:
        asyncio.get_event_loop().run_until_complete(
            evaluate(
                prediction_folder=extractor_save_folder,
                save_folder=evaluator_save_folder,
                model=args.model,
                track=args.track,
                prediction_name='demo',
                overwrite=args.overwrite
            )
        )


if __name__ == '__main__':
    main()
