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

from klaytnetl.jobs.export_raw_traces_job import ExportRawTracesJob
from klaytnetl.jobs.exporters.raw_traces_item_exporter import raw_traces_item_exporter
from blockchainetl.logging_utils import logging_basic_config
from klaytnetl.providers.auto import get_provider_from_uri
from klaytnetl.thread_local_proxy import ThreadLocalProxy
from klaytnetl.cli.s3_sync import get_path, sync_to_s3

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-b', '--batch-size', default=100, type=int, help='The number of blocks to process at a time.')
@click.option('-o', '--output', default='-', type=str,
              help='The output file for geth traces. If not specified stdout is used.')
@click.option('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
@click.option('-p', '--provider-uri', type=str, help='Klaytn Node IP address & port, http://localhost:8551')
@click.option('-t', '--timeout', default=60, type=int, help='The connection time out')
@click.option('--s3-sync', default=None, type=str, help='S3 bucket for syncing export data.')
@click.option('--file-format', default='json', type=str, help='Export file format. "json" (default) or "csv".')
@click.option('--file-maxlines', default=None, type=int, help='Limit max lines per single file. If not provided, output will be a single file.')
@click.option('--compress', is_flag=True, type=bool, help='Enable compress option using gzip. If not provided, the option will be disabled.')
def export_raw_traces(start_block, end_block, batch_size, output, max_workers,
                      provider_uri, timeout, s3_bucket, file_format, file_maxlines, compress):
    """Exports traces from Klaytn node."""

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

    job = ExportRawTracesJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(lambda: get_provider_from_uri(
            provider_uri, timeout=timeout, batch=True)),
        max_workers=max_workers,
        item_exporter=raw_traces_item_exporter(get_path(tmpdir, output), **exporter_options))

    job.run()

    if s3_bucket is not None:
        sync_to_s3(s3_bucket, tmpdir, {output}, file_maxlines is None)
        shutil.rmtree(tmpdir)
