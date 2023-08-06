"""
Export Event data to events_output
team: Ground X, Data Science Team
created: Jettson Lim, 2019-09-03
"""

from blockchainetl.jobs.exporters.composite_item_exporter import CompositeItemExporter

EVENT_FIELDS_TO_EXPORT = [
    'block_number',
    'block_hash',
    'block_timestamp',
    'block_timestamp_fos',
    'transaction_hash',
    'transaction_index',
    'transaction_status',
    'log_index',
    'log_address',
    'log_data',
    'log_topics',
]

def events_item_exporter(events_output=None):
    return CompositeItemExporter(
        filename_mapping={
            'event': events_output
        },
        field_mapping={
            'event': EVENT_FIELDS_TO_EXPORT
        }
    )
