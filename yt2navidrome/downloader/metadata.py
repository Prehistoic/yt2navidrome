import re
from typing import Any

from yt2navidrome.template.models import Argument, MetadataParser, PostProcessor
from yt2navidrome.utils.logging import get_logger


class MetadataUtils:
    logger = get_logger(__name__)

    @classmethod
    def run_parser(cls, input_object: Any, parser: MetadataParser) -> dict[str, str]:
        """
        Run a MetadataParser against an object to extract required metadata.

        Args:
            input_object: The object to extract metadata from.
            parser: The parser to use

        Returns:
            A dict containing the extracted metadata
        """
        cls.logger.debug(parser.summary())

        try:
            source = getattr(input_object, parser.source)
        except Exception:
            cls.logger.exception(f"Failed to get attribute {parser.source} from {type(input_object)} instance")
            return {}

        compiled_pattern = re.compile(parser.pattern)
        match = compiled_pattern.search(source)

        if match:
            cls.logger.debug(f"Found matching values: {match.groupdict()}")
            extracted_metadata = match.groupdict()

            if parser.post_processors:
                for post_processor in parser.post_processors:
                    cls.run_post_processor(extracted_metadata, post_processor)

            return extracted_metadata
        else:
            cls.logger.debug("Found no matching values")
            return {}

    @classmethod
    def run_post_processor(cls, metadata: dict[str, str], post_processor: PostProcessor) -> None:
        """
        Run a PostProcessor to refine extracted metadata.

        Args:
            metadata: The metadata dict to update.
            post_processor: The PostProcessor defining the action to perform and its args
        """
        cls.logger.debug(post_processor.summary())

        if any(input_key not in metadata for input_key in post_processor.input):
            cls.logger.error(f"Post processing failed. Metadata missing a key in {post_processor.input}")
            return

        if post_processor.action == "split":
            metadata[post_processor.output] = cls.run_split(
                input_value=metadata.get(post_processor.input[0], ""), args=post_processor.args
            )
        else:
            cls.logger.error(f"Unsupported post processing action: {post_processor.action}")

    #### POST PROCESSING METHODS ####

    @classmethod
    def run_split(cls, input_value: str, args: list[Argument] | None) -> str:
        """
        Perform a split on the input value.

        Args:
            input_value: The value to process.
            args: The arguments required for the split action

        Returns:
            A string obtained by splitting the input and rejoining it
        """
        # First we check that we got all required args
        if not args:
            cls.logger.error("Missing required arguments: separators and glue")
            return input_value

        for arg in args:
            if arg.key == "separators":
                separators: str = arg.value
            elif arg.key == "glue":
                glue: str = arg.value

        if separators is None or glue is None:
            cls.logger.error("Missing required arguments: separators and/or glue")
            return input_value

        # Then split input_value on any of the separators
        pattern = "|".join(map(re.escape, separators))
        parts: list[str] = re.split(pattern, input_value)
        parts = [p for p in parts if p.strip()]  # Remove empty parts

        # Finally rejoin with glue
        result = glue.join(parts)

        cls.logger.debug(f"Value after splitting: {result}")
        return result
