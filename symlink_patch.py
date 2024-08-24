import click
click.confirm = lambda *args, **kwargs: True

from Broken import BrokenPath
from unittest.mock import Mock

BrokenPath.symlink = Mock()