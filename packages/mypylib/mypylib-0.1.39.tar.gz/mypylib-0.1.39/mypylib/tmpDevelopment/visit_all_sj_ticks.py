from mypylib.MP_shioaji_ticks import *


class ML_user(MP_mother):
    def __init__(self, mp_queue: MP_queue, parameters: base_parameter):
        super(ML_user, self).__init__(mp_queue, parameters)

    def do_something(self, index):
        super(ML_user, self).do_something(index)

        while True:
            try:
                file = self.mp_queue.queue_in.get(block=True, timeout=0)

                with open(file) as fp:
                    for line in fp.readlines():
                        pass

                # self.mp_queue.queue_out.put((index, file))

            except queue.Empty:
                break



class user_parameters(base_parameter):
    def __init__(self):
        super(user_parameters, self).__init__()
        self.dir_shioaji_ticks = '../../../shioaji_ticks'


if __name__ == '__main__':
    mp_queue = MP_queue()

    mpm = ML_user(mp_queue, parameters=user_parameters())
    mpm.run()

    for x in mpm.list_out_debug:
        print(f'list debug: {x}')

    for x in mpm.list_out:
        print(f'list out: {x}')
