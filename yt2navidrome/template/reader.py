import os

import yaml

from yt2navidrome.template import Template
from yt2navidrome.utils.logging import get_logger


class TemplateReader:
    logger = get_logger(__name__)

    @classmethod
    def read_directory(cls, directory_path: str) -> list[Template]:
        """
        Reads all YAML files in a directory and converts them into Template instances.

        Args:
            directory_path: The path to the directory containing YAML files.

        Returns:
            A list of Template instances.
        """

        # Check if the directory exists
        if not os.path.isdir(directory_path):
            print(f"Error: Directory not found at {directory_path}")
            return []

        templates: list[Template] = []

        # Iterate through all files in the specified directory
        for filename in os.listdir(directory_path):
            # We only want files ending in .yaml or .yml (case-insensitive)
            if filename.lower().endswith((".yaml", ".yml")):
                file_path = os.path.join(directory_path, filename)
                cls.logger.debug(f"Processing file: {file_path}")

                try:
                    # Open and read the YAML file
                    with open(file_path) as file:
                        yaml_data = yaml.safe_load(file)

                    # Check if data was loaded successfully and is a dictionary
                    if isinstance(yaml_data, dict):
                        # Use dictionary unpacking (**) to pass key/value pairs
                        # directly to the dataclass constructor.
                        template = Template(**yaml_data)
                        templates.append(template)
                        cls.logger.debug(f"Successfully created template : {template.summary()}")
                    else:
                        cls.logger.warning(f"File {filename} is empty or not a valid map/dictionary.")

                except yaml.YAMLError:
                    cls.logger.exception(f"Error parsing YAML in {filename}")
                except TypeError:
                    # This catches errors if the YAML structure doesn't match the dataclass fields
                    cls.logger.exception(f"Error creating Template for {filename}. Data mismatch")
                except Exception:
                    cls.logger.exception(f"An unexpected error occurred while processing {filename}")

        return templates
