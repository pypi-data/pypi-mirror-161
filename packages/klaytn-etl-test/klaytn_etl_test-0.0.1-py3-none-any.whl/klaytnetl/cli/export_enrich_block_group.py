# MIT License
#
# Copyright (c) 2019 Jettson Lim, jettson.lim@groundx.xyz
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
import tempfile, shutil

from klaytnetl.jobs.export_enrich_block_group_job import ExportEnrichBlockGroupJob
from klaytnetl.jobs.exporters.enrich_block_group_item_exporter import enrich_block_group_item_exporter
from blockchainetl.logging_utils import logging_basic_config
from klaytnetl.providers.auto import get_provider_from_uri
from klaytnetl.thread_local_proxy import ThreadLocalProxy
from klaytnetl.cli.s3_sync import get_path, sync_to_s3

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-b', '--batch-size', default=100, type=int, help='The number of blocks to export at a time.')
@click.option('-p', '--provider-uri', type=str, help='Klaytn Node IP address & port, http://localhost:8551')
@click.option('-t', '--timeout', default=60, type=int, help='The connection time out')
@click.option('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
@click.option('--blocks-output', default=None, type=str,
              help='The output file for blocks. If not provided blocks will not be exported. Use "-" for stdout')
@click.option('--transactions-output', default=None, type=str,
              help='The output file for transactions. '
                   'If not provided transactions will not be exported. Use "-" for stdout')
@click.option('--logs-output', default=None, type=str,
              help='The output file for logs. If not provided logs will not be exported. Use "-" for stdout')
@click.option('--token-transfers-output', default=None, type=str,
              help='The output file for token transfers. '
                   'If not provided token transfers will not be exported. Use "-" for stdout')
@click.option('--s3-bucket', default=None, type=str, help='S3 bucket for syncing export data.')
@click.option('--file-format', default='json', type=str,
              help='Export file format. "json" (default) or "csv".')
@click.option('--file-maxlines', default=None, type=int,
              help='Limit max lines per single file. '
                   'If not provided, output will be a single file.')
@click.option('--compress', is_flag=True, type=bool,
              help='Enable compress option using gzip. '
                   'If not provided, the option will be disabled.')
def export_enrich_block_group(start_block, end_block, batch_size, provider_uri, timeout, max_workers, blocks_output,
                                   transactions_output, logs_output, token_transfers_output,
                                   s3_bucket, file_format, file_maxlines, compress):
    """Exports block groups from Klaytn node."""
    if blocks_output is None and transactions_output is None and logs_output is None and token_transfers_output is None:
        raise ValueError('At least one of --blocks-output, --transactions-output, --logs-output, or --token-transfers-output options must be provided')

    if file_format not in {'json', 'csv'}:
        raise ValueError('"--file-format" option only supports "json" or "csv".')

    if isinstance(file_maxlines, int) and file_maxlines <= 0:
        file_maxlines = None

    exporter_options = {
        'file_format': file_format,
        'file_maxlines': file_maxlines,
        'compress': compress
    }

    # s3 export
    if s3_bucket is not None:
        tmpdir = tempfile.mkdtemp()
    else:
        tmpdir = None


    job = ExportEnrichBlockGroupJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(provider_uri, timeout=timeout, batch=True)),
        max_workers=max_workers,
        item_exporter=enrich_block_group_item_exporter(get_path(tmpdir, blocks_output),
                                                       get_path(tmpdir, transactions_output),
                                                       get_path(tmpdir, logs_output),
                                                       get_path(tmpdir, token_transfers_output),
                                                       **exporter_options),
        export_blocks=blocks_output is not None,
        export_transactions=transactions_output is not None,
        export_logs=logs_output is not None,
        export_token_transfers=token_transfers_output is not None)
    job.run()

    if s3_bucket is not None:
        sync_to_s3(s3_bucket, tmpdir, {blocks_output, transactions_output, logs_output, token_transfers_output}, file_maxlines is None)
        shutil.rmtree(tmpdir)
