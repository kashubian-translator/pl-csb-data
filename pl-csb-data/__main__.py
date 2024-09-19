import config_loader
import data_preparer
import data_normalizer

def process_data(data_paths: dict) -> None:
    data_preparer.prepare(data_paths["source_file"], data_paths["target_file"], data_paths["output_file"])
    data_normalizer.normalize(data_paths["output_file"], data_paths["output_file"]) 


if __name__ == "__main__":
    config = config_loader.load()

    process_data(config["TRAINING"])
    process_data(config["EVALUATION"])
