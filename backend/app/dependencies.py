from app.core.task_store import InMemoryTaskStore


_task_store = InMemoryTaskStore()


def get_task_store() -> InMemoryTaskStore:
    """
    返回进程内单例任务存储。
    """

    return _task_store

