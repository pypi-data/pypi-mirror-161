import typing as t
from abc import ABC, abstractmethod

import requests
from logging import Logger
from pydantic import BaseModel


from ..const import COINS, TYPES


__all__ = [
    'BaseClient',
]


class BaseClient(ABC):
    class PreparedOrderData(BaseModel):
        type: str
        src: str
        dst: str
        estimated_source_amount: float
        estimated_destination_amount: float

    class OrderData(BaseModel):
        deal_group_id: str
        source_currency: str
        destination_currency: str
        type: str
        estimated_source_amount: str
        estimated_destination_amount: str
        store_order_id: t.Optional[str] = None
        should_cancel_at: t.Optional[str] = None
        bot: str
        information: t.Dict[str, t.Any]

    API_URL = 'http:localhost:8000/api/'

    REQUEST_TIMEOUT: float = 10

    SIDE_BUY = 'BUY'
    SIDE_SELL = 'SELL'

    ORDER_TYPE_LIMIT = 'LIMIT'
    ORDER_TYPE_MARKET = 'MARKET'
    # ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
    # ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    # ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
    # ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    # ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

    def __init__(
            self, bot: str, requests_params: t.Optional[t.Dict[str, str]] = None,
            logger: t.Optional[Logger] = Logger("juandb.client.base")
    ):
        self.BOT = bot

        self._requests_params = requests_params
        self.session = self._init_session()
        self.logger = logger

        return

    @staticmethod
    def _get_src_dst(symbol: str) -> t.Tuple[str, str]:
        symbol = symbol.upper()
        if symbol.endswith('BTC'):
            return symbol.split('BTC')[0], 'BTC'
        if symbol.endswith('USDT'):
            return symbol.split('USDT')[0], 'USDT'
        if symbol.endswith('TMN'):
            return symbol.split('TMN')[0], 'TMN'

        raise ValueError(f'Invalid symbol: {symbol}')

    def _prepare_order(
            self, symbol: str, side: str, order_type: str, quantity: float, price: float
    ) -> PreparedOrderData:
        self.logger.debug(f'Preparing order for {symbol} {side} {order_type} {quantity} {price}')
        src, dst = self._get_src_dst(symbol)

        if side.lower() == 'buy':
            src, dst = dst, src

            estimated_source_amount = quantity * price
            estimated_destination_amount = quantity

        else:
            estimated_source_amount = quantity
            estimated_destination_amount = quantity * price

        src = COINS.get(src)
        dst = COINS.get(dst)

        order_type = TYPES.get(order_type.upper())

        self.logger.debug(
            f'Prepared order: {src} {dst} {order_type} {estimated_source_amount} {estimated_destination_amount}'
        )

        return self.PreparedOrderData(
            src=src,
            dst=dst,
            estimated_source_amount=estimated_source_amount,
            estimated_destination_amount=estimated_destination_amount,
            type=order_type
        )

    @staticmethod
    def _get_kwargs(locals_: t.Dict, excludes: t.List[str] = None, exclude_nones: bool = False) -> t.Dict:
        _del_keys = ['self', 'cls']
        if excludes is not None:
            _del_keys.extend(excludes)

        if exclude_nones is True:
            return {key: value for key, value in locals_.items() if (key not in _del_keys) and (value is not None)}

        return {key: value for key, value in locals_.items() if key not in _del_keys}

    @staticmethod
    def _get_headers() -> t.Dict:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        return headers

    def _create_api_uri(self, path: str) -> str:
        return self.API_URL + '/' + path

    def _get_request_kwargs(self, method, signed: bool, **kwargs) -> t.Dict:
        # set default requests timeout
        kwargs['timeout'] = self.REQUEST_TIMEOUT

        # add our global requests params
        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del (kwargs['data']['requests_params'])

        if signed is True:
            headers = kwargs.get('headers', {})
            headers.update({'x-api-key': 'NICE'})
            kwargs['headers'] = headers

        # if get request assign data array to params value for requests lib
        if data and method == 'get':
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            del (kwargs['data'])

        return kwargs

    @staticmethod
    def _pick(result: t.Union[t.Dict, t.List], key: str, value: str = None) -> t.Union[t.Dict, t.List]:
        result = result.copy()
        if isinstance(result, dict):
            symbol_data = result.get(key)
            result.clear()
            result[key] = symbol_data

            return result
        if isinstance(result, list):
            assert value is not None, "value is required for list"
            # print(f"Looking for {key=} with {value=} in {result}")
            result_ = [item for item in result if item[key] == value]

            return result_

    @abstractmethod
    def _init_session(self) -> requests.Session:
        raise NotImplementedError('_init_session not implemented')

    @abstractmethod
    def _request(self, method, uri: str, signed: bool, **kwargs):
        raise NotImplementedError('_request not implemented')

    @staticmethod
    @abstractmethod
    def _handle_response(response: requests.Response):
        raise NotImplementedError('_handle_response not implemented')

    @abstractmethod
    def _request_api(
            self, method, path: str, signed: bool = False, **kwargs
    ):
        raise NotImplementedError('_request_api not implemented')

    @abstractmethod
    def _get(self, path, signed=False, **kwargs) -> t.Dict:
        raise NotImplementedError('_get not implemented')

    @abstractmethod
    def _post(self, path, signed=False, **kwargs) -> t.Dict:
        raise NotImplementedError('_post not implemented')

    @abstractmethod
    def _put(self, path, signed=False, **kwargs) -> t.Dict:
        raise NotImplementedError('_put not implemented')

    @abstractmethod
    def _delete(self, path, signed=False, **kwargs) -> t.Dict:
        raise NotImplementedError('_delete not implemented')

    @abstractmethod
    def create_order(
            self,
            store: str,
            symbol: str,
            side: str,
            type: str,
            deal_groups_id: int,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        raise NotImplementedError('create_order not implemented')

    @abstractmethod
    def order_market(
            self,
            store: str,
            symbol: str,
            side: str,
            deal_groups_id: int,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        raise NotImplementedError('order_market not implemented')

    @abstractmethod
    def order_limit(
            self,
            store: str,
            symbol: str,
            side: str,
            deal_groups_id: int,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        raise NotImplementedError('order_limit not implemented')

    @abstractmethod
    def order_market_buy(
            self,
            store: str,
            symbol: str,
            deal_groups_id: int,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        raise NotImplementedError('order_market_buy not implemented')

    @abstractmethod
    def order_market_sell(
            self,
            store: str,
            symbol: str,
            deal_groups_id: int,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        raise NotImplementedError('order_market_sell not implemented')

    @abstractmethod
    def order_limit_buy(
            self,
            store: str,
            symbol: str,
            deal_groups_id: int,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        raise NotImplementedError('order_limit_buy not implemented')

    @abstractmethod
    def order_limit_sell(
            self,
            store: str,
            symbol: str,
            deal_groups_id: int,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        raise NotImplementedError('order_limit_sell not implemented')

    @abstractmethod
    def cancel_order(self, order_id: str, store: str) -> t.Dict:
        raise NotImplementedError('cancel_order not implemented')

    @abstractmethod
    def get_open_orders(
            self, store: str, bot: str = None, source_currency: str = None, destination_currency: str = None,
    ) -> t.Dict:
        raise NotImplementedError('get_open_orders not implemented')

    @abstractmethod
    def get_order_status(self, order_id: str, store: str) -> t.Dict:
        raise NotImplementedError('get_order_status not implemented')

    @abstractmethod
    def close_connection(self):
        raise NotImplementedError('close_connection not implemented')
