"""
Module Description.


"""
import logging
from pathlib import Path

from mako.template import Template

DIR = Path(__file__).parent.absolute()

logger = logging.getLogger(__name__)


def writeTemplate(filename: str,
                  outputpath: Path,
                  data: dict = {},
                  templatepath: Path = DIR / 'templates') -> None:
    """
    [summary]

    [extended_summary]

    Args:
        filename (str): [description]
        data (dict, optional): [description]. Defaults to {}.
        outputpath (Path, optional): [description]. Defaults to None.
    """
    template = str(templatepath / f'{filename}.tmpl')
    mytemplate = Template(filename=template, output_encoding='utf-8')
    outputpath.mkdir(exist_ok=True, parents=True)
    (outputpath / filename).write_bytes(mytemplate.render(**data))
