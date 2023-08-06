# MIT License
#
# Copyright (c) 2019 Jettson Lim, jettson.lim@groundx.xyz
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

from klaytnetl.domain.base import BaseDomain
from klaytnetl.utils import strf_unix_dt, int_to_decimal, float_to_datetime, validate_address
from datetime import datetime
from deprecated import deprecated
from decimal import Decimal
from typing import Union, List, NamedTuple, Optional


class KlaytnRawReceipt(BaseDomain):
    def __init__(self):
        self._transaction_hash: str = None
        self._transaction_index: int = None
        self._block_hash: str = None
        self._block_number: int = None
        self._gas_used: int = None
        self._contract_address: Optional[str] = None
        self._logs: list = []
        self._status: int = None

    ### Prop: transaction_hash ###
    @property
    def transaction_hash(self) -> str:
        return self._transaction_hash

    @transaction_hash.setter
    def transaction_hash(self, value: str) -> None:
        value = validate_address(value, digits=66)
        if value is None:
            raise TypeError(f"TypeUnmatched: receipt.transaction_hash cannot be {None}.")

        self._transaction_hash = value

    @transaction_hash.deleter
    def transaction_hash(self) -> None:
        del self._transaction_hash

    ### Prop: transaction_index ###
    @property
    def transaction_index(self) -> int:
        return self._transaction_index

    @transaction_index.setter
    def transaction_index(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"TypeUnmatched: receipt.transaction_index must be {int}.")

        self._transaction_index = value

    @transaction_index.deleter
    def transaction_index(self) -> None:
        del self._transaction_index

    ### Prop: block_hash ###
    @property
    def block_hash(self) -> str:
        return self._block_hash

    @block_hash.setter
    def block_hash(self, value: str) -> None:
        value = validate_address(value, digits=66)
        if value is None:
            raise TypeError(f"TypeUnmatched: receipt.block_hash cannot be {None}.")

        self._block_hash = value

    @block_hash.deleter
    def block_hash(self) -> None:
        del self._block_hash

    ### Prop: block_number ###
    @property
    def block_number(self) -> int:
        return self._block_number

    @block_number.setter
    def block_number(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"TypeUnmatched: receipt.block_number must be {int}.")

        self._block_number = value

    @block_number.deleter
    def block_number(self) -> None:
        del self._block_number

    ### Prop: gas_used ###
    @property
    def gas_used(self) -> int:
        return self._gas_used

    @gas_used.setter
    def gas_used(self, value: Union[int, None]) -> None:
        if value is None:
            self._gas_used = 0
        elif not isinstance(value, int):
            raise TypeError(f"TypeUnmatched: receipt.gas_used must be {int}.")
        else:
            self._gas_used = value

    @gas_used.deleter
    def gas_used(self) -> None:
        del self._gas_used

    ### Prop: contract_address ###
    @property
    def contract_address(self) -> Optional[str]:
        return self._contract_address

    @contract_address.setter
    def contract_address(self, value: Optional[str]) -> None:
        self._contract_address = validate_address(value, digits=42) if value is not None else None


    @contract_address.deleter
    def contract_address(self) -> None:
        del self._contract_address

    ### Prop: logs ###
    @property
    def logs(self) -> list:
        return self._logs

    @logs.setter
    def logs(self, value: list) -> None:
        if not isinstance(value, list):
            raise TypeError(f"TypeUnmatched: receipt.logs must be {list}.")

        self._logs = value

    @logs.deleter
    def logs(self) -> None:
        del self._logs

    ### Prop: status ###
    @property
    def status(self) -> int:
        return self._status

    @status.setter
    def status(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(f"TypeUnmatched: receipt.status must be {int}.")

        self._status = value

    @status.deleter
    def status(self) -> None:
        del self._status


@deprecated
class EthReceipt(object):
    def __init__(self):
        self.transaction_hash = None
        self.transaction_index = None
        self.block_hash = None
        self.block_number = None
        # self.cumulative_gas_used = None
        self.gas_used = None
        self.contract_address = None
        self.logs = []
        # self.root = None
        self.status = None