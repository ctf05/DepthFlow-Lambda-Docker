from Broken import BrokenPath
from unittest.mock import Mock

def mock_symlink(virtual, real, **kwargs):
    print(f"Mocked symlink: {virtual} -> {real}")
    return virtual

BrokenPath.symlink = mock_symlink

# Mock click.confirm to always return True
import click
click.confirm = lambda *args, **kwargs: True