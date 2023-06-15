import logging
import os
from logging.config import dictConfig

import yaml  # type: ignore


def setup_logging(
    default_path="hasura-authenticationwebhook-rolemapping-service/logging.yml",
    env_key="LOG_CFG",
) -> None:
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            logging_config = yaml.safe_load(f.read())
        dictConfig(logging_config)
    else:
        logging.basicConfig(level=logging.INFO)
