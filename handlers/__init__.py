from handlers.del_msg import delete_messages
from handlers.handlers_common import router as common
from handlers.handlers_default import router as default
from handlers.handlers_title_add import router as title_add
from handlers.handlers_title_list import router as title_list

__all__ = (
    "common",
    "title_add",
    "title_list",
    "default",
    "delete_messages",
)
