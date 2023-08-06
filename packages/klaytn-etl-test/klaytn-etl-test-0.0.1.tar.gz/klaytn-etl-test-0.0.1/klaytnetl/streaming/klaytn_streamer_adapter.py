import logging

from web3 import Web3
from web3.middleware import geth_poa_middleware

from blockchainetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from klaytnetl.enumeration.entity_type import EntityType

from klaytnetl.jobs.export_blocks_job import ExportBlocksJob
from klaytnetl.jobs.export_receipts_job import ExportReceiptsJob
from klaytnetl.jobs.export_traces_job import ExportTracesJob
from klaytnetl.jobs.extract_contracts_job import ExtractContractsJob
from klaytnetl.jobs.extract_token_transfers_job import ExtractTokenTransfersJob
from klaytnetl.jobs.extract_tokens_job import ExtractTokensJob

from klaytnetl.jobs.export_enrich_block_group_job import ExportEnrichBlockGroupJob
from klaytnetl.jobs.export_enrich_trace_group_job import ExportEnrichTraceGroupJob

from klaytnetl.streaming.enrich import enrich_transactions, enrich_logs, enrich_token_transfers, enrich_traces, \
    enrich_contracts, enrich_tokens
from klaytnetl.streaming.klaytn_item_id_calculator import KlaytnItemIdCalculator
from klaytnetl.thread_local_proxy import ThreadLocalProxy


class KlaytnStreamerAdapter:
    def __init__(
            self,
            batch_web3_provider,
            item_exporter=ConsoleItemExporter(),
            batch_size=100,
            max_workers=5,
            entity_types=tuple(EntityType.ALL_FOR_STREAMING)):
        self.batch_web3_provider = batch_web3_provider
        self.item_exporter = item_exporter
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.entity_types = entity_types
        self.item_id_calculator = KlaytnItemIdCalculator()

    def open(self):
        self.item_exporter.open()

    def get_current_block_number(self):
        web3 = Web3(self.batch_web3_provider)
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        return int(web3.eth.getBlock("latest").number)

    def export_all(self, start_block, end_block):
        # Export block group
        blocks, transactions, logs, token_transfers = [], [], [], []
        if self._should_export(EntityType.BLOCK) or self._should_export(EntityType.TRANSACTION) or self._should_export(EntityType.LOG) or self._should_export(EntityType.TOKEN_TRANSFER):
            blocks, transactions, logs, token_transfers = self._export_enrich_block_group(start_block, end_block)

        # Export trace group
        traces, contracts, tokens = [], [], []
        if start_block > 0 and self._should_export(EntityType.TRACE) or self._should_export(EntityType.CONTRACT) or self._should_export(EntityType.TOKEN):
            traces, contracts, tokens = self._export_enrich_trace_group(start_block, end_block)

        logging.info('Exporting with ' + type(self.item_exporter).__name__)

        all_items = blocks + \
            transactions + \
            logs + \
            token_transfers + \
            traces + \
            contracts + \
            tokens

        self.calculate_item_ids(all_items)

        self.item_exporter.export_items(all_items)

    def _export_enrich_block_group(self, start_block, end_block):
        block_group_item_exporter = InMemoryItemExporter(item_types=['block', 'transaction', 'log', 'token_transfer'])
        block_group_job = ExportEnrichBlockGroupJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=block_group_item_exporter,
            export_blocks=self._should_export(EntityType.BLOCK),
            export_transactions=self._should_export(EntityType.TRANSACTION),
            export_logs=self._should_export(EntityType.LOG),
            export_token_transfers=self._should_export(EntityType.TOKEN_TRANSFER)
        )
        block_group_job.run()
        blocks = block_group_item_exporter.get_items('block')
        transactions = block_group_item_exporter.get_items('transaction')
        logs = block_group_item_exporter.get_items('log')
        token_transfers = block_group_item_exporter.get_items('token_transfer')

        return blocks, transactions, logs, token_transfers

    def _export_enrich_trace_group(self, start_block, end_block):
        trace_group_item_exporter = InMemoryItemExporter(item_types=['trace', 'contract', 'token'])
        web3 = Web3(self.batch_web3_provider)
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        trace_group_job = ExportEnrichTraceGroupJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            web3=ThreadLocalProxy(lambda: web3),
            max_workers=self.max_workers,
            item_exporter=trace_group_item_exporter,
            export_traces=self._should_export(EntityType.TRACE),
            export_contracts=self._should_export(EntityType.CONTRACT),
            export_tokens=self._should_export(EntityType.TOKEN)
        )
        trace_group_job.run()
        traces = trace_group_item_exporter.get_items('trace')
        contracts = trace_group_item_exporter.get_items('contract')
        tokens = trace_group_item_exporter.get_items('token')

        return traces, contracts, tokens


    def _should_export(self, entity_type):
        if entity_type == EntityType.BLOCK:
            return EntityType.BLOCK in self.entity_types or self._should_export(EntityType.TRANSACTION)

        if entity_type == EntityType.TRANSACTION:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(EntityType.LOG)

        if entity_type == EntityType.LOG:
            return EntityType.LOG in self.entity_types or self._should_export(EntityType.TOKEN_TRANSFER)

        if entity_type == EntityType.TOKEN_TRANSFER:
            return EntityType.TOKEN_TRANSFER in self.entity_types

        if entity_type == EntityType.TRACE:
            return EntityType.TRACE in self.entity_types or self._should_export(EntityType.CONTRACT)

        if entity_type == EntityType.CONTRACT:
            return EntityType.CONTRACT in self.entity_types or self._should_export(EntityType.TOKEN)

        if entity_type == EntityType.TOKEN:
            return EntityType.TOKEN in self.entity_types

        raise ValueError('Unexpected entity type ' + entity_type)

    def calculate_item_ids(self, items):
        for item in items:
            item['item_id'] = self.item_id_calculator.calculate(item)

    def close(self):
        self.item_exporter.close()
