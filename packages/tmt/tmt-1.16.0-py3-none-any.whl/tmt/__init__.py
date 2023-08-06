""" Test Management Tool """

# Version is replaced before building the package
__version__ = '1.16.0 (decf1f9)'

__all__ = [
    'Tree',
    'Test',
    'Plan',
    'Story',
    'Run',
    'Guest',
    'GuestSsh',
    'Result',
    'Status',
    'Clean']

from tmt.base import Clean, Plan, Result, Run, Status, Story, Test, Tree
from tmt.steps.provision import Guest, GuestSsh
