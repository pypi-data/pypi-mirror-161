"""
Klaytn Event
team: Ground X, Data Science Team
created: Jettson Lim, 2019-09-03
"""

class KlaytnEvent(object):
    def __init__(self):
        self.block_number = None
        self.block_hash = None
        self.block_timestamp = None
        self.block_timestamp_fos = None    # Quantity: The fraction of a second of the timestamp

        self.transaction_hash = None
        self.transaction_index = None
        self.transaction_status = None

        self.log_index = None
        self.log_address = None
        self.log_data = None
        self.log_topics = []
