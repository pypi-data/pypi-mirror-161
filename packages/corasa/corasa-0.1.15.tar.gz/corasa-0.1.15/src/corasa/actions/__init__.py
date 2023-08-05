from rasa_sdk.executor import ActionExecutor

from .core import InitializeConversation, Eval, Set, Push, Pop, CreateEvent
from .helpers import action, ActionContext
from .patch_action_executor import run


def init_corasa_actions():
    # Monkey matching of the ActionExecutor class.
    ActionExecutor.run = run

