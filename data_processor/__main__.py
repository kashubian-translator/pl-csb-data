import config_loader
from data_preparer import DataPreparer
from data_normalizer import DataNormalizer
from logging import Logger
from logger import set_up_logger


def process_data(data_paths: dict, language: dict, logger: Logger) -> None:
    DataPreparer(logger).prepare(
        data_paths["source_file"],
        data_paths["target_file"],
        data_paths["output_file"],
        language["source_language"],
        language["target_language"]
    )
    DataNormalizer(logger).normalize(
        data_paths["output_file"],
        data_paths["output_file"]
    )


if __name__ == "__main__":
    logger = set_up_logger(__name__, "INFO")

    config = config_loader.load("data_processor/config.ini", logger)

    logger.info("Processing training data")
    process_data(config["TRAINING"], config["LANGUAGE"], logger)

    logger.info("Processing validation data")
    process_data(config["VALIDATION"], config["LANGUAGE"], logger)
    
    logger.info("Processing validation debug data")
    process_data(config["VALIDATION_DEBUG"], config["LANGUAGE"], logger)

    logger.info("Processing test data")
    process_data(config["TEST"], config["LANGUAGE"], logger)
