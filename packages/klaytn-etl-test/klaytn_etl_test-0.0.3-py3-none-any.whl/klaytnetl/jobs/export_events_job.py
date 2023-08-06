"""
Export events directly
team: Ground X, Data Science Team
created: Jettson Lim, 2019-09-03
"""

import json

from klaytnetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from klaytnetl.json_rpc_requests import generate_get_block_with_receipt_by_number_json_rpc
from klaytnetl.mappers.event_mapper import KlaytnEventMapper
from klaytnetl.utils import rpc_response_batch_to_results, validate_range



class ExportEventsJob(BaseJob):
    def __init__(self,
                 block_iterator,
                 batch_size,
                 max_workers,
                 batch_web3_provider,
                 item_exporter,
                 event_hash):
        self.block_iterator = block_iterator

        self.batch_web3_provider = batch_web3_provider

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.item_exporter = item_exporter

        self.event_mapper = KlaytnEventMapper()

        self.event_hash = event_hash

    def _start(self):
        self.item_exporter.open()

    def _export(self):
        self.batch_work_executor.execute(self.block_iterator,
                                         self._export_batch,
                                         total_items=len(self.block_iterator))

    def _export_batch(self, block_number_batch):
        blocks_rpc = list(generate_get_block_with_receipt_by_number_json_rpc(block_number_batch))
        response = self.batch_web3_provider.make_batch_request(json.dumps(blocks_rpc))
        results = rpc_response_batch_to_results(response)
        events = []
        for result in results:
            events = events + self.event_mapper.block_json_dict_to_events(result, self.event_hash)

        for event in events:
            self._export_event(event)

    def _export_event(self, event):
        self.item_exporter.export_item(self.event_mapper.event_to_dict(event))

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()
