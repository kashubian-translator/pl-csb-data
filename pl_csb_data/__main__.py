import config_loader
import data_preparer
import data_normalizer


def process_data(data_paths: dict, language: dict) -> None:
    data_preparer.prepare(
        data_paths["source_file"],
        data_paths["target_file"],
        data_paths["output_file"],
        language["source_language"],
        language["target_language"]
    )
    data_normalizer.normalize(
        data_paths["output_file"],
        data_paths["output_file"]
    )


if __name__ == "__main__":
    config = config_loader.load()

    process_data(config["TRAINING"], config["LANGUAGE"])
    process_data(config["EVALUATION"], config["LANGUAGE"])
