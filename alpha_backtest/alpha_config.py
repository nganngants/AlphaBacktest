import yaml

class AlphaConfig:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self._load_config()

    def _load_config(self):
        with open(self.config_file, "r") as f:
            config = yaml.safe_load(f)
            self.alpha = config["alpha"]
            self.start_sim_date = config["start_sim_date"]
            self.end_sim_date = config["end_sim_date"]
