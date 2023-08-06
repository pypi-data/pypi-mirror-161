from __future__ import annotations

import importlib.resources as pkg_resources
import os
from typing import Sequence

from jinja2 import Template

from . import templates


def get_template(name: str) -> str:
    """Load template and returns it in a string

    Template can be a relative file name in which case the template will be
    loaded from the bundled templates. If an absolute path is given then it
    will be loaded from that path.
    """
    if os.path.isabs(name):
        with open(name) as file:
            return file.read()

    return pkg_resources.read_text(templates, name)


def get_default_template() -> str:
    return get_template('prepare_commit_msg_append.j2')


def get_rendered_template(
        template: str,
        variables: dict[str, Sequence[str]],
) -> str:
    tpl = Template(template)
    return tpl.render(variables)
