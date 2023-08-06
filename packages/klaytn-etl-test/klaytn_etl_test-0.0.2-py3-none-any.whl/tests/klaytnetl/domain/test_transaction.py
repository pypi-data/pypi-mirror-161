import pytest
import json

from typing import List

from klaytnetl.providers.auto import get_provider_from_uri
from klaytnetl.thread_local_proxy import ThreadLocalProxy
from klaytnetl.json_rpc_requests import generate_get_block_with_receipt_by_number_json_rpc

from klaytnetl.domain.block import KlaytnRawBlock, KlaytnBlock
from klaytnetl.mappers.block_mapper import KlaytnBlockMapper
from klaytnetl.domain.transaction import KlaytnRawTransaction, KlaytnTransaction
from klaytnetl.mappers.transaction_mapper import KlaytnTransactionMapper

from klaytnetl.utils import strf_unix_dt, rpc_response_batch_to_results
from datetime import datetime


NETWORK_URI = 'http://13.125.191.49:8551'
TEST_BLOCKS = [range(1467330, 1467430), range(14673300, 14673400), [11649472], [10993804], [11410797]]


def get_web3_provider():
    return ThreadLocalProxy(lambda: get_provider_from_uri(NETWORK_URI, batch=True))

def get_block_mapper(enrich):
    block_mapper = KlaytnBlockMapper(enrich=enrich)
    transaction_mapper = KlaytnTransactionMapper(enrich=enrich)
    block_mapper.register(transaction_mapper=transaction_mapper)
    return block_mapper


@pytest.fixture(params=[KlaytnRawTransaction, KlaytnTransaction])
def Transaction(request):
    return request.param

@pytest.fixture(params=TEST_BLOCKS)
def request_dataset(request):
    block_numbers = request.param
    json_rpc = list(
        generate_get_block_with_receipt_by_number_json_rpc(block_numbers))
    response = get_web3_provider().make_batch_request(json.dumps(json_rpc))
    return list(rpc_response_batch_to_results(response))


def test_json_dict_to_block(Transaction, request_dataset):
    block_mapper = get_block_mapper(enrich=(Transaction == KlaytnTransaction))
    transaction_mapper = block_mapper.transaction_mapper

    for block_data in request_dataset:
        block = block_mapper.json_dict_to_block(block_data)
        transactions = [transaction_mapper.transaction_to_dict(tx) for tx in block.transactions]

        print(transactions)
