# encoding: UTF-8

"""

Event engine definitions

"""

# queue management
EVENT_EMPTY_QUEUE = 'event_empty_queue'
EVENT_STOP_LOOP = 'event_stop_loop'

# strategy
EVENT_NEW_BAR = 'event_on_bar'

# data
EVENT_DATA_FEED_BEGIN = 'event_data_feeding_begin'
EVENT_DATA_FEED_END = 'event_data_feeding_end'
EVENT_NEXT_BAR = 'event_next_bar'
