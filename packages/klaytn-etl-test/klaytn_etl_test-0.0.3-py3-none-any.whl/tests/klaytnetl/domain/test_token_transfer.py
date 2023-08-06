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
from klaytnetl.domain.receipt import KlaytnRawReceipt
from klaytnetl.mappers.receipt_mapper import KlaytnReceiptMapper
from klaytnetl.domain.receipt_log import KlaytnRawReceiptLog, KlaytnReceiptLog
from klaytnetl.mappers.receipt_log_mapper import KlaytnReceiptLogMapper
from klaytnetl.service.token_transfer_extractor import KlaytnTokenTransferExtractor
from klaytnetl.mappers.token_transfer_mapper import KlaytnTokenTransferMapper

from klaytnetl.utils import strf_unix_dt, rpc_response_batch_to_results
from datetime import datetime


NETWORK_URI = 'http://13.125.191.49:8551'
TEST_BLOCKS = [range(1467330, 1467430), range(14673300, 14673400), [11649472], [10993804], [11410797]]


def get_web3_provider():
    return ThreadLocalProxy(lambda: get_provider_from_uri(NETWORK_URI, batch=True))

def get_block_mapper(enrich):
    block_mapper = KlaytnBlockMapper(enrich=enrich)

    if enrich is True:
        transaction_mapper = KlaytnTransactionMapper(enrich=enrich)
        receipt_log_mapper = KlaytnReceiptLogMapper(enrich=enrich)

        transaction_mapper.register(receipt_log_mapper=receipt_log_mapper)
        block_mapper.register(transaction_mapper=transaction_mapper)
    else:
        receipt_mapper = KlaytnReceiptMapper()
        receipt_log_mapper = KlaytnReceiptLogMapper(enrich=enrich)

        receipt_mapper.register(receipt_log_mapper=receipt_log_mapper)
        block_mapper.register(receipt_mapper=receipt_mapper)

    return block_mapper

def get_extractor(enrich):
    return KlaytnTokenTransferExtractor(enrich=enrich)

@pytest.fixture(params=[KlaytnRawReceiptLog, KlaytnReceiptLog])
def ReceiptLog(request):
    return request.param

@pytest.fixture(params=TEST_BLOCKS)
def request_dataset(request):
    block_numbers = request.param
    json_rpc = list(
        generate_get_block_with_receipt_by_number_json_rpc(block_numbers))
    response = get_web3_provider().make_batch_request(json.dumps(json_rpc))
    return list(rpc_response_batch_to_results(response))


def test_json_dict_to_block(ReceiptLog, request_dataset):
    enrich = (ReceiptLog == KlaytnReceiptLog)
    block_mapper = get_block_mapper(enrich=enrich)
    extractor = get_extractor(enrich=enrich)
    token_transfer_mapper = KlaytnTokenTransferMapper(enrich=enrich)

    if enrich:
        transaction_mapper = block_mapper.transaction_mapper
        log_mapper = transaction_mapper.receipt_log_mapper
        for block_data in request_dataset:
            block = block_mapper.json_dict_to_block(block_data)
            for transaction in block.transactions:
                logs = (extractor.extract_transfer_from_log(log) for log in transaction.logs if log is not None)
                token_transfers = [token_transfer_mapper.token_transfer_to_dict(log) for log in logs if log is not None]
                print(token_transfers)
    else:
        receipt_mapper = block_mapper.receipt_mapper
        log_mapper = receipt_mapper.receipt_log_mapper
        for block_data in request_dataset:
            block = block_mapper.json_dict_to_block(block_data)
            for receipt in block.receipts:
                logs = (extractor.extract_transfer_from_log(log) for log in receipt.logs if log is not None)
                token_transfers = [token_transfer_mapper.token_transfer_to_dict(log) for log in logs if log is not None]
                print(token_transfers)
