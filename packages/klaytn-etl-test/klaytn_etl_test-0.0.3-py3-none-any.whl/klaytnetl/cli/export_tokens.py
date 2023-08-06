# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
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


import click
import json

from web3 import Web3
from web3.middleware import geth_poa_middleware

from blockchainetl.file_utils import smart_open
from klaytnetl.jobs.export_tokens_job import ExportTokensJob
from klaytnetl.jobs.exporters.tokens_item_exporter import tokens_item_exporter
from blockchainetl.logging_utils import logging_basic_config
from klaytnetl.thread_local_proxy import ThreadLocalProxy
from klaytnetl.providers.auto import get_provider_from_uri

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-c', '--contracts', required=True, type=str,
              help='The contracts file.')
@click.option('-o', '--output', default='-', type=str, help='The output file. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
@click.option('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
              help='The URI of the web3 provider e.g. '
                   'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
@click.option('-C', '--chain', default='ethereum', type=str, help='The chain network to connect to.')
def export_tokens(contracts, output, max_workers, provider_uri, chain='ethereum'):
    """Exports ERC20/ERC721 tokens."""
    web3 = Web3(get_provider_from_uri(provider_uri))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    with smart_open(contracts, 'r') as contracts_file:

        tokens_iterable = ({
            "contract_address": contract["address"].strip(),
            "block_number": contract["block_number"]
        } for contract in (json.loads(contract) for contract in contracts_file) if contract["is_erc20"] or contract["is_erc721"])

        job = ExportTokensJob(
            tokens_iterable=tokens_iterable,
            web3=ThreadLocalProxy(lambda: web3),
            item_exporter=tokens_item_exporter(output),
            max_workers=max_workers)

        job.run()
