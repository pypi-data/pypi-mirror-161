

import threading
from line_notify import LineNotify
import queue
from loguru import logger

class tLineNotify(threading.Thread):

    def __init__(self, token, name=None):
        threading.Thread.__init__(self)
        self.line_notify = LineNotify(token, name=name)
        self.queue = queue.Queue()
        self.start()

    def on(self):
        self.line_notify.on()

    def off(self):
        self.line_notify.off()

    def format(self, message):
        return self.line_notify.format(message=message)

    def send(self, message, image_path=None, sticker_id=None, package_id=None):
        self.queue.put((message, image_path, sticker_id, package_id))

    def run(self):
        while True:
            try:
                (message, image_ath, sticker_id, package_id) = self.queue.get(timeout=1)
            except queue.Empty:
                pass
            else:
                if message is None:
                    break
                self.line_notify.send(message=message, image_path=image_path, sticker_id=sticker_id, package_id=package_id)

    def stop(self):
        self.queue.put((None, None, None, None))

class TestClass:
    def __init__(self):
        pass

    def print(self):

if __name__ == '__main__':
    pass



