from pathlib import Path

import yaml

from yt2navidrome.template.models import Template
from yt2navidrome.utils.logging import get_logger


class TemplateReader:
    logger = get_logger(__name__)

    @classmethod
    def read_directory(cls, directory_path: Path) -> list[Template]:
        """
        Reads all YAML files in a directory and converts them into Template instances.

        Args:
            directory_path: The path to the directory containing YAML files.

        Returns:
            A list of Template instances.
        """

        # Check if the directory exists
        if not directory_path.is_dir():
            print(f"Error: Directory not found at {directory_path}")
            return []

        templates: list[Template] = []

        # Iterate through all files in the specified directory
        for file_path in directory_path.iterdir():
            # We only want files ending in .yaml or .yml (case-insensitive)
            if file_path.name.lower().endswith((".yaml", ".yml")):
                cls.logger.debug(f"Processing file: {file_path}")

                try:
                    # Open and read the YAML file
                    with open(file_path) as f:
                        template = yaml.load(f, Loader=yaml.FullLoader)  # noqa: S506

                    # Check if data was loaded successfully and is a dictionary
                    if isinstance(template, Template):
                        templates.append(template)
                        cls.logger.debug(f"Successfully created template : {template.summary()}")
                    else:
                        cls.logger.warning(f"File {file_path} is empty or not a valid Template.")

                except yaml.YAMLError:
                    cls.logger.exception(f"Error parsing YAML in {file_path}")
                except TypeError:
                    # This catches errors if the YAML structure doesn't match the dataclass fields
                    cls.logger.exception(f"Error creating Template for {file_path}. Data mismatch")
                except Exception:
                    cls.logger.exception(f"An unexpected error occurred while processing {file_path}")

        return templates
