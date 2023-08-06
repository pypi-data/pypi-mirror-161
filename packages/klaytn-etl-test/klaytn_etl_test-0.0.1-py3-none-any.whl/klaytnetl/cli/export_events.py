"""
Export events directly
team: Ground X, Data Science Team
created: Jettson Lim, 2019-09-03
"""

import click

from klaytnetl.jobs.export_events_job import ExportEventsJob
from klaytnetl.jobs.exporters.events_item_exporter import events_item_exporter
from blockchainetl.logging_utils import logging_basic_config
from klaytnetl.providers.auto import get_provider_from_uri
from klaytnetl.thread_local_proxy import ThreadLocalProxy
from klaytnetl.utils import validate_range

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, type=int, help='Start block')
@click.option('-e', '--end-block', default=None, type=int, help='End block')
@click.option('-l', '--block-list', default=None, type=str, help='List of blocks to be parsed')
@click.option('-p', '--provider-uri', default='https://mainnet.infura.io', type=str,
              help='The URI of the web3 provider e.g. '
                   'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
@click.option('-b', '--batch-size', default=100, type=int, help='The number of blocks to export at a time.')
@click.option('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
@click.option('-e', '--event-hash', default=None, type=str, help='The event signature hash to export.')
@click.option('--events-output', default='-', type=str,
              help='The output file for events. If not provided blocks will not be exported. Use "-" for stdout')
@click.option('-t', '--timeout', default=60, type=int, help='IPC or HTTP request timeout.')
@click.option('-c', '--chain', default='ethereum', type=str, help='The chain network to connect to.')
def export_events(start_block, end_block, block_list, provider_uri, batch_size, max_workers, event_hash, events_output, timeout=60, chain='ethereum'):

    if end_block is not None:
        validate_range(start_block, end_block)
        block_iterator = range(start_block, end_block + 1)
    elif block_list is not None:
        block_iterator = set([int(block) for block in block_list.split(':')])
    else:
        raise ValueError('Either --end-block or --block-list options must be provided')

    job = ExportEventsJob(
        block_iterator=block_iterator,
        batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(provider_uri, timeout=timeout, batch=True)),
        batch_size=batch_size,
        max_workers=max_workers,
        item_exporter=events_item_exporter(events_output),
        event_hash=event_hash)
    job.run()
