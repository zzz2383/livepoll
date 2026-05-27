# polls/tasks.py
import threading
import time
from django.utils import timezone 


class PollScheduler:
    """后台线程，每分钟检查一次到期投票并关闭"""
    
    def __init__(self):
        self._thread = None
        self._stop_event = threading.Event()
    
    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
    
    def _run(self):
        # 等待 Django 完全启动
        time.sleep(5)
        while not self._stop_event.is_set():
            try:
                self._check_and_close()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"PollScheduler error: {e}")
            # 每 60 秒检查一次
            self._stop_event.wait(60)
    
    def _check_and_close(self):
        from polls.services import PollService
        service = PollService()
        service.close_expired_polls()