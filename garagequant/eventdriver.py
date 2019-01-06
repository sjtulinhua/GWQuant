# encoding: UTF-8

"""

Event engine definitions

"""
from garagequant.eventtype import *
from collections import defaultdict
from queue import Queue, Empty
from threading import Thread

import logging

logger = logging.getLogger(__name__)


class Event:
    def __init__(self, event_type, event_data=None):
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

        # store handlers, map event_type <-> handler for events
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
        logger.debug(f'[EventLoop] put event: {event.event_type}')
        self.__queue.put(event)

    def start(self):
        self.__active = True
        self.__thread.start()

    def stop(self):
        logger.debug('[EventLoop] stop loop ')
        self.__active = False
        # logger.debug('----- start join the thread ------')
        # self.__thread.join()
        # logger.debug('----- end of join the thread ------')
        pass

    def __run_loop(self):
        # when try to stop, will not stop until all the events are handled
        while self.__active or not self.__queue.empty():
            try:
                event = self.__queue.get(block=False, timeout=0.5)
                logger.debug(f'[EventLoop] Get event: {event.event_type}')
                self.__handle(event)
            except Empty:
                self.__queue.put(Event(EVENT_EMPTY_QUEUE))

        # when loop stopped, queue thread stops too
        return

    def __handle(self, event):
        if event.event_type in self.__handler_map:
            [handler(event.event_data) for handler in self.__handler_map[event.event_type]]
        pass


# testing
def test_event_driver():
    logger.info('start test_event_driver')

    type_a = 'type_a'
    type_b = 'type_b'

    def type_a_func1(event):
        logger.debug('\t%s: type a func-1' % str(event.event_type))
        # print(event)

    def type_a_func2(event):
        logger.debug('\t%s: type a func-2' % str(event.event_type))
        # print(event)

    def type_b_func1(event):
        logger.debug('\t%s: type b func-1' % str(event.event_type))
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

    logger.info('end of test')
