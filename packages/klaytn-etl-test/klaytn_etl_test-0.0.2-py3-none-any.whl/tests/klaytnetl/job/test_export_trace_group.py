import pytest
import json

from typing import List

from web3 import Web3
from web3.middleware import geth_poa_middleware

from blockchainetl.jobs.exporters.console_item_exporter import ConsoleItemExporter
from blockchainetl.jobs.exporters.in_memory_item_exporter import InMemoryItemExporter
from klaytnetl.jobs.export_enrich_trace_group_job import ExportEnrichTraceGroupJob
from klaytnetl.jobs.export_raw_trace_group_job import ExportRawTraceGroupJob
from blockchainetl.logging_utils import logging_basic_config
from klaytnetl.providers.auto import get_provider_from_uri
from klaytnetl.thread_local_proxy import ThreadLocalProxy
from datetime import datetime


NETWORK_URI = 'http://13.125.191.49:8551'
TEST_BLOCKS = [(1, 101), (14673300, 14673400), (11649472, 11649472),
               (10993804, 10993804), (11410797, 11410797)]


@pytest.fixture(params=[ExportEnrichTraceGroupJob, ExportRawTraceGroupJob])
def ExportJob(request):
    return request.param

@pytest.fixture(params=TEST_BLOCKS)
def test_block_range(request):
    return request.param

def web3():
    web3 = Web3(get_provider_from_uri(NETWORK_URI))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return ThreadLocalProxy(lambda: web3)


def test_json_dict_to_block(ExportJob, test_block_range):
    # exporter = InMemoryItemExporter(item_types=['trace_block'])
    exporter = ConsoleItemExporter()
    job = ExportJob(
        start_block=test_block_range[0],
        end_block=test_block_range[1],
        batch_size=100,
        batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(
            'http://13.125.191.49:8551', timeout=120, batch=True)),
        web3=web3(),
        max_workers=10,
        item_exporter=exporter,
        export_traces=True,
        export_contracts=True,
        export_tokens=True)

    job.run()

    # print(json.dumps(exporter.get_items('trace_block')))
