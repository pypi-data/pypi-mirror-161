# MIT License
#
# Copyright (c) 2019 Jettson Lim, jettson.lim@groundx.xyz
# Copyright (c) 2018 Evgeniy Filatov, evgeniyfilatov@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from klaytnetl.domain.trace import EthTrace
from klaytnetl.domain.trace import KlaytnRawTrace, KlaytnTrace
from klaytnetl.domain.trace_block import KlaytnRawTraceBlock, KlaytnTraceBlock
from klaytnetl.domain.transaction import KlaytnRawTransaction, KlaytnTransaction
from klaytnetl.mappers.base import BaseMapper
from klaytnetl.mixin.enrichable_mixin import EnrichableMixin
from klaytnetl.mappers.transaction_mapper import KlaytnTransactionMapper
from klaytnetl.mainnet_daofork_state_changes import DAOFORK_BLOCK_NUMBER
from klaytnetl.utils import hex_to_dec, to_normalized_address, strf_unix_dt

from deprecated import deprecated
from typing import Union, List, Tuple


class KlaytnTraceMapper(BaseMapper, EnrichableMixin):
    def __init__(self, enrich=True):
        super(KlaytnTraceMapper, self).__init__(enrich=enrich)
        self.transaction_mapper = KlaytnTransactionMapper(enrich=True)  # Must be enrich = True

    def trace_block_to_trace(self, trace_block: Union[KlaytnTraceBlock, KlaytnRawTraceBlock]) -> Union[List[KlaytnTrace], List[KlaytnRawTrace]]:
        block_number = trace_block.block_number
        transaction_traces = trace_block.transaction_traces

        traces: List[Union[KlaytnRawTrace, KlaytnTrace]] = []
        counter = -1

        for tx_index, tx_trace in enumerate(transaction_traces):

            if tx_trace.get('logs') is None:
                rst, ctr = self._iterate_transaction_trace(
                    block_number=block_number,
                    tx_index=tx_index,
                    tx_hash=tx_trace.get('transactionHash'),
                    tx_status=hex_to_dec(tx_trace.get('transactionReceiptStatus')),
                    tx_trace=tx_trace,
                    parent_status=1,
                    counter=counter + 1,
                    trace_address=[],
                    block_hash=trace_block.block_hash if isinstance(trace_block, KlaytnTraceBlock) else None,
                    block_timestamp=trace_block.block_timestamp if isinstance(trace_block, KlaytnTraceBlock) else None)
            else:
                rst, ctr = self._single_transaction(
                    tx_trace=tx_trace,
                    counter=counter + 1,
                    block_timestamp=trace_block.block_timestamp if isinstance(trace_block, KlaytnTraceBlock) else None)

            counter = ctr
            traces.extend(rst)

        return traces

    def _single_transaction(self, tx_trace, counter, **kwargs) -> Tuple[Union[List[KlaytnTrace], List[KlaytnRawTrace]], int]:

        transaction: KlaytnTransaction = self.transaction_mapper.json_dict_to_transaction(tx_trace,
            block_timestamp=kwargs.get('block_timestamp') or 0)  # FIXME

        trace = KlaytnRawTrace()

        trace.block_number = transaction.block_number

        trace.transaction_index = transaction.transaction_index
        trace.transaction_hash = transaction.hash

        trace.trace_index = counter

        trace.from_address = transaction.from_address
        trace.to_address = transaction.to_address

        trace.input = transaction.input if transaction.input is not None else '0x'
        trace.output = '0x'

        trace.value = transaction.value
        trace.gas = transaction.gas
        trace.gas_used = transaction.receipt_gas_used

        trace.error = None
        trace.status = transaction.receipt_status

        # FIXME
        trace.trace_type = 'call'
        trace.call_type = 'call'

        trace.subtraces = 0
        trace.trace_address = []

        result = [trace if not self.enrich else KlaytnTrace.enrich(trace,
            block_hash=transaction.block_hash,
            block_timestamp=transaction.block_timestamp,
            transaction_receipt_status=transaction.receipt_status)]

        return result, counter

    def _iterate_transaction_trace(self, block_number, tx_index, tx_hash, tx_status, tx_trace, parent_status, counter, trace_address=[], **kwargs) -> Union[Tuple[List[KlaytnTrace], int], Tuple[List[KlaytnRawTrace], int]]:

        trace = KlaytnRawTrace()


        trace.block_number = block_number

        trace.transaction_index = tx_index
        trace.transaction_hash = tx_hash

        trace.trace_index = counter

        trace.from_address = to_normalized_address(tx_trace.get('from'))
        trace.to_address = to_normalized_address(tx_trace.get('to'))

        trace.input = tx_trace.get('input', '0x')
        trace.output = tx_trace.get('output', '0x')

        trace.value = hex_to_dec(tx_trace.get('value'))
        trace.gas = hex_to_dec(tx_trace.get('gas'))
        trace.gas_used = hex_to_dec(tx_trace.get('gasUsed'))

        trace.error = tx_trace.get('error')

        trace.status = tx_status * parent_status * (1 if tx_trace.get('error') is None or len(tx_trace.get('error')) <= 0 else 0)

        # lowercase for compatibility with parity traces
        trace.trace_type = tx_trace.get('type').lower()
        if trace.trace_type == 'selfdestruct':
            # rename to suicide for compatibility with parity traces
            trace.trace_type = 'suicide'
        elif trace.trace_type in ('call', 'callcode', 'delegatecall', 'staticcall'):
            trace.call_type = trace.trace_type
            trace.trace_type = 'call'

        calls = tx_trace.get('calls', [])

        trace.subtraces = len(calls)
        trace.trace_address = trace_address

        result = [trace if not self.enrich else KlaytnTrace.enrich(trace,
            block_hash=kwargs.get('block_hash'),
            block_timestamp=kwargs.get('block_timestamp'),
            transaction_receipt_status=tx_status)]

        for call_index, call_trace in enumerate(calls):
            rst, ctr = self._iterate_transaction_trace(
                block_number=block_number,
                tx_index=tx_index,
                tx_hash=tx_hash,
                tx_status=tx_status,
                tx_trace=call_trace,
                parent_status=trace.status,
                counter=counter + 1,
                trace_address=trace_address + [call_index],
                **kwargs)

            counter = ctr
            result.extend(rst)

        return result, counter

    def trace_to_dict(self, trace: Union[KlaytnRawTrace, KlaytnTrace], serializable=True) -> dict:
        trace_dict = {
            'type': 'trace',
            'block_number': trace.block_number,
            'transaction_hash': trace.transaction_hash,
            'transaction_index': trace.transaction_index,
            'trace_index': trace.trace_index,
            'from_address': trace.from_address,
            'to_address': trace.to_address,
            'value': int(trace.value) if serializable else trace.value,
            'input': trace.input,
            'output': trace.output,
            'trace_type': trace.trace_type,
            'call_type': trace.call_type,
            'gas': trace.gas,
            'gas_used': trace.gas_used,
            'subtraces': trace.subtraces,
            'trace_address': trace.trace_address,
            'error': trace.error,
            'status': trace.status
        }

        if self.enrich and isinstance(trace, KlaytnTrace):
            trace_dict['block_hash'] = trace.block_hash
            trace_dict['block_timestamp'] = trace.block_timestamp.isoformat() if serializable else trace.block_timestamp
            trace_dict['block_unix_timestamp'] = trace.block_timestamp.timestamp()
            trace_dict['transaction_receipt_status'] = trace.transaction_receipt_status

        return trace_dict


@deprecated
class EthTraceMapper(object):
    def json_dict_to_trace(self, json_dict):
        trace = EthTrace()

        trace.block_number = json_dict.get('blockNumber')
        trace.transaction_hash = json_dict.get('transactionHash')
        trace.transaction_index = json_dict.get('transactionPosition')
        trace.subtraces = json_dict.get('subtraces')
        trace.trace_address = json_dict.get('traceAddress', [])

        error = json_dict.get('error')

        if error:
            trace.error = error

        action = json_dict.get('action')
        if action is None:
            action = {}
        result = json_dict.get('result')
        if result is None:
            result = {}

        trace_type = json_dict.get('type')
        trace.trace_type = trace_type

        # common fields in call/create
        if trace_type in ('call', 'create'):
            trace.from_address = to_normalized_address(action.get('from'))
            trace.value = hex_to_dec(action.get('value'))
            trace.gas = hex_to_dec(action.get('gas'))
            trace.gas_used = hex_to_dec(result.get('gasUsed'))

        # process different trace types
        if trace_type == 'call':
            trace.call_type = action.get('callType')
            trace.to_address = to_normalized_address(action.get('to'))
            trace.input = action.get('input')
            trace.output = result.get('output')
        elif trace_type == 'create':
            trace.to_address = result.get('address')
            trace.input = action.get('init')
            trace.output = result.get('code')
        elif trace_type == 'suicide':
            trace.from_address = to_normalized_address(action.get('address'))
            trace.to_address = to_normalized_address(action.get('refundAddress'))
            trace.value = hex_to_dec(action.get('balance'))
        elif trace_type == 'reward':
            trace.to_address = to_normalized_address(action.get('author'))
            trace.value = hex_to_dec(action.get('value'))
            trace.reward_type = action.get('rewardType')

        return trace

    def geth_trace_to_traces(self, geth_trace):
        block_number = geth_trace.block_number
        transaction_traces = geth_trace.transaction_traces

        traces = []

        for tx_index, tx_trace in enumerate(transaction_traces):
            if tx_trace is None:
                continue
            traces.extend(self._iterate_transaction_trace(
                block_number,
                tx_index,
                tx_trace,
            ))

        return traces

    def genesis_alloc_to_trace(self, allocation):
        address = allocation[0]
        value = allocation[1]

        trace = EthTrace()

        trace.block_number = 0
        trace.to_address = address
        trace.value = value
        trace.trace_type = 'genesis'
        trace.status = 1

        return trace

    def daofork_state_change_to_trace(self, state_change):
        from_address = state_change[0]
        to_address = state_change[1]
        value = state_change[2]

        trace = EthTrace()

        trace.block_number = DAOFORK_BLOCK_NUMBER
        trace.from_address = from_address
        trace.to_address = to_address
        trace.value = value
        trace.trace_type = 'daofork'
        trace.status = 1

        return trace

    def _iterate_transaction_trace(self, block_number, tx_index, tx_trace, trace_address=[]):
        trace = EthTrace()

        trace.block_number = block_number
        trace.transaction_index = tx_index

        trace.from_address = to_normalized_address(tx_trace.get('from'))
        trace.to_address = to_normalized_address(tx_trace.get('to'))

        trace.input = tx_trace.get('input')
        trace.output = tx_trace.get('output')

        trace.value = hex_to_dec(tx_trace.get('value'))
        trace.gas = hex_to_dec(tx_trace.get('gas'))
        trace.gas_used = hex_to_dec(tx_trace.get('gasUsed'))

        trace.error = tx_trace.get('error')

        # lowercase for compatibility with parity traces
        trace.trace_type = tx_trace.get('type').lower()

        if trace.trace_type == 'selfdestruct':
            # rename to suicide for compatibility with parity traces
            trace.trace_type = 'suicide'
        elif trace.trace_type in ('call', 'callcode', 'delegatecall', 'staticcall'):
            trace.call_type = trace.trace_type
            trace.trace_type = 'call'

        result = [trace]

        calls = tx_trace.get('calls', [])

        trace.subtraces = len(calls)
        trace.trace_address = trace_address

        for call_index, call_trace in enumerate(calls):
            result.extend(self._iterate_transaction_trace(
                block_number,
                tx_index,
                call_trace,
                trace_address + [call_index]
            ))

        return result

    def trace_to_dict(self, trace):
        return {
            'type': 'trace',
            'block_number': trace.block_number,
            'transaction_hash': trace.transaction_hash,
            'transaction_index': trace.transaction_index,
            'from_address': trace.from_address,
            'to_address': trace.to_address,
            'value': trace.value,
            'input': trace.input,
            'output': trace.output,
            'trace_type': trace.trace_type,
            'call_type': trace.call_type,
            'reward_type': trace.reward_type,
            'gas': trace.gas,
            'gas_used': trace.gas_used,
            'subtraces': trace.subtraces,
            'trace_address': trace.trace_address,
            'error': trace.error,
            'status': trace.status,
            'trace_id': trace.trace_id,
        }
