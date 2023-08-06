
import threading
import queue
import os
from playsound import playsound

if os.name == 'nt':
    import winsound

_MYPYLIB_ROOT = os.path.abspath(os.path.dirname(__file__))

class tplaysound(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.queue = queue.Queue()

        self.file_sound_alert = f'{_MYPYLIB_ROOT}/../data/alert.wav'

        self.start()

    def play(self, filename=None):
        self.play_file(filename=filename)

    def play_file(self, filename=None):
        if filename is None:
            filename = self.file_sound_alert
        command = ('play', filename)
        self.queue.put(command)
        # print(f'send command {command}')

    def run(self):
        while True:
            try:
                (cmd, arg) = self.queue.get(timeout=1)
            except queue.Empty:
                pass
            else:
                if cmd == 'stop':
                    break

                if cmd == 'play':
                    # print('got Play')
                    if os.name == 'nt':
                        # print('NT play')
                        winsound.PlaySound(arg, winsound.SND_FILENAME)
                    else:
                        # print('POSIX play')
                        playsound(arg)

    def stop(self):
        self.queue.put(('stop', 'stop'))



if __name__ == '__main__':
    from time import sleep


    tps = tplaysound()
    index = 0
    while True:
        tps.play_file()
        tps.play_file()
        tps.play_file()
        tps.play_file()
        sleep(3)
        index += 1
        if index == 3:
            break
    tps.stop()
    tps.join()
