# encoding: UTF-8

"""

Event engine definitions

"""

from collections import defaultdict
from queue import Queue, Empty
from threading import Thread

from util.gqutil import gq_hosting_thread_info, debug_trace


class Event:
    def __init__(self, event_type=None, event_data=None):
        self.event_type = event_type
        self.event_data = event_data  # data would be defined offline by case

    def __str__(self):
        return '\t * Event object: %s \n\t   - type: %s \n\t   - data: %s' \
               % (id(self), str(self.event_type), str(self.event_data))


class EventDriver:
    def __init__(self):
        # queue toggle
        self.__active = False

        # events queue
        self.__queue = Queue()

        # store handlers, map type <-> handler for events
        self.__handler_map = defaultdict(list)

        # handler thread
        self.__thread = Thread(target=self.__run_loop, name='event_handler')

    def register(self, event_type, handler):
        handlers_list = self.__handler_map[event_type]
        if handler not in handlers_list:
            handlers_list.append(handler)

    def unregister(self, event_type, handler):
        handlers_list = self.__handler_map[type]
        if handler in handlers_list:
            handlers_list.remove(handler)

        if not self.__handler_map[event_type]:
            del self.__handler_map[event_type]

    def put_event(self, event):
        debug_trace('----- put event ------')
        self.__queue.put(event)

    def start(self):
        self.__active = True
        self.__thread.start()

    def stop(self):
        debug_trace('*** to stop the thread ')
        self.__active = False
        debug_trace('----- start join the thread ------')
        self.__thread.join()
        debug_trace('----- end of join the thread ------')
        pass

    def __run_loop(self):
        # when try to stop, will not stop until all the events are handled
        while self.__active or not self.__queue.empty():
            debug_trace('*** in thread while loop')
            try:
                event = self.__queue.get(block=True, timeout=0.5)  # 获取事件的阻塞时间设为1秒
                self.__handle(event)
            except Empty:
                pass

        debug_trace('*** end of thread while loop')
        return

    def __handle(self, event):
        if event.event_type in self.__handler_map:
            [handler(event) for handler in self.__handler_map[event.event_type]]
        pass


# testing
def unit_test():
    gq_hosting_thread_info('__main__')

    type_a = 'type_a'
    type_b = 'type_b'

    def type_a_func1(event):
        debug_trace('\n\t%s: type a func-1' % str(event.event_type))
        # print(event)

    def type_a_func2(event):
        debug_trace('\n\t%s: type a func-2' % str(event.event_type))
        # print(event)

    def type_b_func1(event):
        debug_trace('\n\t%s: type b func-1' % str(event.event_type))
        # print(event)

    ed = EventDriver()

    ed.register(type_a, type_a_func1)
    ed.register(type_a, type_a_func2)
    ed.register(type_b, type_b_func1)

    # ed.unregister(type_a, type_a_func1)
    # ed.unregister(type_a, type_a_func2)

    ed.start()

    ed.put_event(Event(type_a, 'put 1st type_a event here'))
    ed.put_event(Event(type_a, 'put 2st type_a event here'))
    ed.put_event(Event(type_b, dict(a=100, b='type_b event with dict data')))

    ed.stop()

    debug_trace('end of test')


if __name__ == '__main__':
    unit_test()
