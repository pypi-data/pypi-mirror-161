"""PresentationOperation functions.

Presentation operations.
"""
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

# from typing import Any


logging.basicConfig(
    level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s"
)

# use as example for how to do variables to template
# from django example
# jinja examples add to jinja templating
# class BasicListView(View):
# def get(self, request, *args, **kwargs):
#     countries = Country.objects.all()
#     context = {"country_list": countries}
#     return render(request, "list.html", context)


class PresentationOperations:
    """Presentation Operation Functions.

    Args:
        input_dictionary (str): input_dictionary.
        input_template_name (str): template name.
        trim_blocks (bool): trim_blocks.
        lstrip_blocks (bool): lstrip_blocks.

    Returns:
        output_text (str): output text.
    """

    def __init__(
        self,
        input_dictionary: str,
        input_template_name: str,
        trim_blocks: bool = True,
        lstrip_blocks: bool = True,
    ) -> None:
        """Init class."""
        self.input_dictionary = input_dictionary
        self.input_template_name = input_template_name
        self.trim_blocks = trim_blocks
        self.lstrip_blocks = lstrip_blocks

    def __repr__(self) -> str:  # pragma: no cover
        """Display function name using repr."""
        class_name = self.__class__.__name__
        return f"{class_name}"

    # def prepare_template_with_pathlib(self, **kwargs: str) -> Any:  # type: ignore
    def prepare_template_with_pathlib(self, **kwargs: str) -> str:
        """Prepare output using a template and dictionary.

        Take dictionary and a template file.  Combine to create
        template output.

        Returns:
            output_text (str): output text
        """
        # input_dictionary: str = kwargs["input_dictionary"]
        # input_template_name: str = kwargs["input_template_name"]
        autoescape_formats: str = kwargs["autoescape_formats"]

        path_obj: Path = Path(__file__).parent.parent / "templates"
        env: Environment = Environment(
            loader=FileSystemLoader(Path(path_obj)),
            trim_blocks=self.trim_blocks,
            lstrip_blocks=self.lstrip_blocks,
            keep_trailing_newline=False,
            autoescape=select_autoescape(autoescape_formats),
        )
        template: Template = env.get_template(self.input_template_name)
        output_text: str = template.render(jinja_var=self.input_dictionary)

        return output_text
