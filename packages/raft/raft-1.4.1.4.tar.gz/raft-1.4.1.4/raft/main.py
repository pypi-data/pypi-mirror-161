"""
Invoke's own 'binary' entrypoint.

Dogfoods the `program` module.
"""

from . import __version__, Program

program = Program(
    name='raft',
    binary='raft',
    binary_names=['raft', 'convoke', ],
    version=__version__,
)
