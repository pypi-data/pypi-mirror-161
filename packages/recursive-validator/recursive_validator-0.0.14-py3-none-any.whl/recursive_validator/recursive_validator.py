import argparse, os
from loguru import logger
from recursive_validator.helpers.file_helpers import (
    dynamic_import_from_src,
    matches_patterns,
)
from recursive_validator.helpers.data_helpers import DataHandler
from recursive_validator.helpers.log_helpers import LogHandler


def main(args):
    # Import all of the loaders from the directory
    modules = dynamic_import_from_src(args["loaders_path"])

    # If there are no loaders then throw and error and exit
    if len(modules) == 0:
        logger.error(
            "There are no loaders in the directory {}".format(args["loaders_path"])
        )
        exit()

    # Setup the include patterns
    include_patterns = args["include_patterns"].split(",")
    include_patterns = [s.strip() for s in include_patterns]

    # Setup the exclude patterns
    exclude_patterns = args["exclude_patterns"].split(",")
    exclude_patterns = [s.strip() for s in exclude_patterns]

    log_handler = LogHandler()

    # Create an iterator to walk through the input directory
    for root, dirs, files in os.walk(args["input_directory"], topdown=False):

        for file_name in files:

            file_path = os.path.join(root, file_name)

            if matches_patterns(file_path, exclude_patterns):
                continue

            if not matches_patterns(file_path, include_patterns):
                continue

            # Pass parameters to each loader
            for module in modules:
                try:
                    log_handler.set_file_path(file_path)
                    data_helper = DataHandler(file_path, file_name)
                    mmodule_loader = module.Loader(data_helper, log_handler)
                    mmodule_loader.initialize()
                except Exception as e:
                    logger.error(e)
                    raise

    log_handler.print_messages()

    logger.info("Complete...")


def app():

    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "--input_directory",
        type=str,
        dest="input_directory",
        default="./",
        help="The input directory to scan.",
        required=True,
    )

    parser.add_argument(
        "--include_patterns",
        type=str,
        dest="include_patterns",
        default="*.y*ml",
        help="The patterns to include.",
        required=False,
    )

    parser.add_argument(
        "--exclude_patterns",
        type=str,
        dest="exclude_patterns",
        default="*/backups/*",
        help="The patterns to exclude.",
        required=False,
    )

    parser.add_argument(
        "--loaders_path",
        type=str,
        dest="loaders_path",
        help="The patterns to a directory containing loaders.",
        required=True,
    )

    args = vars(parser.parse_args())

    main(args)
