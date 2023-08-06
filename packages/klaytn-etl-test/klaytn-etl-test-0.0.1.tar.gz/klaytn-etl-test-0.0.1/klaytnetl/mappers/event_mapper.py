"""
Klaytn Event Mapper
team: Ground X, Data Science Team
created: Jettson Lim, 2019-09-03
"""

from klaytnetl.domain.block import KlaytnBlock
from klaytnetl.domain.transaction import KlaytnTransaction
from klaytnetl.domain.event import KlaytnEvent
from klaytnetl.utils import hex_to_dec


class KlaytnEventMapper(object):

    def block_json_dict_to_events(self, block_json_dict, event_hash=None):
        events = []

        block = KlaytnBlock()
        block.number = hex_to_dec(block_json_dict.get('number'))
        block.hash = block_json_dict.get('hash')
        block.timestamp = hex_to_dec(block_json_dict.get('timestamp'))
        block.timestamp_fos = hex_to_dec(block_json_dict.get('timestampFoS'))
        if 'transactions' in block_json_dict:
            for tx_json_dict in block_json_dict['transactions']:
                if isinstance(tx_json_dict, dict):
                    transaction = KlaytnTransaction()
                    transaction.hash = tx_json_dict.get('transactionHash')
                    transaction.index = hex_to_dec(tx_json_dict.get('transactionIndex'))
                    transaction.status = hex_to_dec(tx_json_dict.get('status'))
                    if 'logs' in tx_json_dict:
                        for log_json_dict in tx_json_dict['logs']:
                            if isinstance(log_json_dict, dict):
                                event = KlaytnEvent()

                                event.block_number = block.number
                                event.block_hash = block.hash
                                event.block_timestamp = block.timestamp
                                event.block_timestamp_fos = block.timestamp_fos
                                event.transaction_hash = transaction.hash
                                event.transaction_index = transaction.index
                                event.transaction_status = transaction.status
                                event.log_index = hex_to_dec(log_json_dict.get('logIndex'))
                                event.log_address = log_json_dict.get('address')
                                event.log_data = log_json_dict.get('data')
                                event.log_topics = self._safe_convert_to_topics(log_json_dict.get('topics'))

                                if self._match_first_hash(event.log_topics, event_hash) is True:
                                    events.append(event)

        return events


    def event_to_dict(self, event):
        return {
            'type': 'event',
            'block_number': event.block_number,
            'block_hash': event.block_hash,
            'block_timestamp': event.block_timestamp,
            'block_timestamp_fos': event.block_timestamp_fos,
            'transaction_hash': event.transaction_hash,
            'transaction_index': event.transaction_index,
            'transaction_status': event.transaction_status,
            'log_index': event.log_index,
            'log_address': event.log_address,
            'log_data': event.log_data,
            'log_topics': event.log_topics,
        }


    def dict_to_event(self, _dict):
        event = KlaytnEvent()

        event.block_number = _dict.get('block_number')
        event.block_hash = _dict.get('block_hash')
        event.block_timestamp = _dict.get('block_timestamp')
        event.block_timestamp_fos = _dict.get('block_timestamp_fos')
        event.transaction_hash = _dict.get('transaction_hash')
        event.transaction_index = _dict.get('transaction_index')
        event.transaction_status = _dict.get('transaction_status')
        event.log_index = _dict.get('log_index')
        event.log_address = _dict.get('log_address')
        event.log_data = _dict.get('log_data')
        event.log_topics = _dict.get('log_topics')

        return event

    def _safe_convert_to_topics(self, raw):
        if isinstance(raw, str):
            if len(raw.strip()) == 0:
                return []
            else:
                return raw.strip().split(',')
        else:
            return raw

    def _match_first_hash(self, topics, event_hash):
        if event_hash is None:
            return True
        if not isinstance(topics, list) or topics == []:
            return False

        # event_hash is not None
        # topics is a non-empty list, i.e., topics[0] exists
        return topics[0] == event_hash
