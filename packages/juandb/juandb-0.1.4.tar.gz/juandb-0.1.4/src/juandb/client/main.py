import typing as t
import requests
import aiohttp
import asyncio

from logging import Logger

from .base import BaseClient
from .exceptions import RequestException, APIException

__all__ = [
    'Client',
    'AsyncClient'
]


class Client(BaseClient):
    def __init__(
            self, bot: str, requests_params: t.Optional[t.Dict[str, t.Any]] = None,
            logger: t.Optional[Logger] = Logger("juandb.client.base")
    ):
        super().__init__(bot, requests_params, logger)

    def _init_session(self) -> requests.Session:

        headers = self._get_headers()

        session = requests.session()
        session.headers.update(headers)
        return session

    def _request(self, method, uri: str, signed: bool, **kwargs):

        kwargs = self._get_request_kwargs(method, signed, **kwargs)
        print(f"{method=} ||| {uri=} ||| {kwargs=}")

        self.response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(self.response)

    @staticmethod
    def _handle_response(response: requests.Response):
        if not (200 <= response.status_code < 300):
            raise APIException(response, response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise RequestException('Invalid Response: %s' % response.text)

    def _request_api(
            self, method, path: str, signed: bool = False, **kwargs
    ):
        uri = self._create_api_uri(path)
        return self._request(method, uri, signed, **kwargs)

    def _get(self, path, signed=False, **kwargs) -> t.Dict:
        return self._request_api('get', path, signed, **kwargs)

    def _post(self, path, signed=False, **kwargs) -> t.Dict:
        return self._request_api('post', path, signed, **kwargs)

    def _put(self, path, signed=False, **kwargs) -> t.Dict:
        return self._request_api('put', path, signed, **kwargs)

    def _delete(self, path, signed=False, **kwargs) -> t.Dict:
        return self._request_api('delete', path, signed, **kwargs)

    def create_order(
            self,
            store: str,
            symbol: str,
            side: str,
            type: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        data = self._prepare_order(symbol=symbol, side=side, order_type=type, quantity=quantity, price=price)

        _ = self.OrderData(
            deal_group_id=deal_groups_id,
            source_currency=data.src,
            destination_currency=data.dst,
            type=data.type,
            estimated_source_amount=data.estimated_source_amount,
            estimated_destination_amount=data.estimated_destination_amount,
            # store_order_id=client_id,
            should_cancel_at=cancel_at,
            bot=self.BOT,
            information=information,
        ).dict()

        return self._post('deals', signed=False, json=_, headers={'x-storeClient': store})

    def order_market(
            self,
            store: str,
            symbol: str,
            side: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return self.create_order(
            store=store,
            symbol=symbol,
            type=self.ORDER_TYPE_MARKET,
            side=side,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    def order_limit(
            self,
            store: str,
            symbol: str,
            side: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return self.create_order(
            store=store,
            symbol=symbol,
            type=self.ORDER_TYPE_LIMIT,
            side=side,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    def order_market_buy(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return self.order_market(
            store=store,
            symbol=symbol,
            side=self.SIDE_BUY,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    def order_market_sell(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return self.order_market(
            store=store,
            symbol=symbol,
            side=self.SIDE_SELL,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    def order_limit_buy(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return self.order_limit(
            store=store,
            symbol=symbol,
            side=self.SIDE_BUY,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    def order_limit_sell(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return self.order_limit(
            store=store,
            symbol=symbol,
            side=self.SIDE_SELL,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    def cancel_order(self, order_id: str, store: str) -> t.Dict:
        return self._delete(f'deals/{order_id}', signed=False, headers={'x-storeClient': store})

    def get_open_orders(
            self, store: str, bot: str = None, source_currency: str = None, destination_currency: str = None,
    ) -> t.Dict:
        return self._get(
            'deals/openDeals', signed=False, headers={'x-storeClient': store}, params=self._get_kwargs(
                locals_=locals(), excludes=['store'], exclude_nones=True
            )
        )

    def get_order_status(self, order_id: str, store: str) -> t.Dict:
        return self._get(f'deals/{order_id}', signed=False, headers={'x-storeClient': store})

    def close_connection(self):
        if self.session:
            self.session.close()

    def __del__(self):
        self.close_connection()


class AsyncClient(BaseClient):
    def __init__(
            self,
            bot: str,
            requests_params: t.Optional[t.Dict[str, t.Any]] = None,
            loop: t.Optional[asyncio.AbstractEventLoop] = None,
            logger: t.Optional[Logger] = Logger("juandb.client.base")
    ):

        self.loop = loop or asyncio.get_event_loop()
        super().__init__(bot, requests_params, logger)

    @classmethod
    async def create(
            cls,
            bot: str,
            requests_params: t.Optional[t.Dict[str, t.Any]] = None,
            loop: t.Optional[asyncio.AbstractEventLoop] = None,
            logger: t.Optional[Logger] = Logger("juandb.client.base")
    ) -> 'AsyncClient':

        return cls(bot, requests_params, loop, logger)

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
        return False

    def _init_session(self) -> aiohttp.ClientSession:
        session = aiohttp.ClientSession(
            loop=self.loop,
            headers=self._get_headers()
        )
        return session

    async def _request(self, method, uri: str, signed: bool, **kwargs):

        kwargs = self._get_request_kwargs(method, signed, **kwargs)

        async with getattr(self.session, method)(uri, **kwargs) as response:
            self.response = response
            return await self._handle_response(response)

    @staticmethod
    async def _handle_response(response: aiohttp.ClientResponse):
        if not str(response.status).startswith('2'):
            raise APIException(response, response.status, await response.text())
        try:
            return await response.json()
        except ValueError:
            txt = await response.text()
            raise RequestException(f'Invalid Response: {txt}')

    async def _request_api(self, method, path, signed=False, **kwargs):
        uri = self._create_api_uri(path)
        return await self._request(method, uri, signed, **kwargs)

    async def _get(self, path, signed=False, **kwargs) -> t.Dict:
        return await self._request_api('get', path, signed, **kwargs)

    async def _post(self, path, signed=False, **kwargs) -> t.Dict:
        return await self._request_api('post', path, signed, **kwargs)

    async def _put(self, path, signed=False, **kwargs) -> t.Dict:
        return await self._request_api('put', path, signed, **kwargs)

    async def _delete(self, path, signed=False, **kwargs) -> t.Dict:
        return await self._request_api('delete', path, signed, **kwargs)

    async def create_order(
            self,
            store: str,
            symbol: str,
            side: str,
            type: str,
            deal_groups_id: str,
            information: t.Dict,
            quantity: float,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        data = self._prepare_order(symbol=symbol, side=side, order_type=type, quantity=quantity, price=price)

        _ = self.OrderData(
            deal_group_id=deal_groups_id,
            source_currency=data.src,
            destination_currency=data.dst,
            type=data.type,
            estimated_source_amount=data.estimated_source_amount,
            estimated_destination_amount=data.estimated_destination_amount,
            # store_order_id=client_id,
            should_cancel_at=cancel_at,
            bot=self.BOT,
            information=information,
        ).dict()

        return await self._post('deals', signed=False, json=_, headers={'x-storeClient': store})

    async def order_market(
            self,
            store: str,
            symbol: str,
            side: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return await self.create_order(
            store=store,
            symbol=symbol,
            type=self.ORDER_TYPE_MARKET,
            side=side,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    async def order_limit(
            self,
            store: str,
            symbol: str,
            side: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return await self.create_order(
            store=store,
            symbol=symbol,
            type=self.ORDER_TYPE_LIMIT,
            side=side,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    async def order_market_buy(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return await self.order_market(
            store=store,
            symbol=symbol,
            side=self.SIDE_BUY,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    async def order_market_sell(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return await self.order_market(
            store=store,
            symbol=symbol,
            side=self.SIDE_SELL,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    async def order_limit_buy(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return await self.order_limit(
            store=store,
            symbol=symbol,
            side=self.SIDE_BUY,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    async def order_limit_sell(
            self,
            store: str,
            symbol: str,
            deal_groups_id: str,
            quantity: float,
            information: t.Dict,
            price: float = None,
            client_id: str = None,
            cancel_at: str = None,
    ) -> t.Dict:
        return await self.order_limit(
            store=store,
            symbol=symbol,
            side=self.SIDE_SELL,
            deal_groups_id=deal_groups_id,
            quantity=quantity,
            information=information,
            price=price,
            client_id=client_id,
            cancel_at=cancel_at,
        )

    async def cancel_order(self, order_id: str, store: str) -> t.Dict:
        return await self._delete(f'deals/{order_id}', signed=False, headers={'x-storeClient': store})

    async def get_open_orders(
            self, store: str, bot: str = None, source_currency: str = None, destination_currency: str = None,
    ) -> t.Dict:
        return await self._get(
            'deals/openDeals', signed=False, headers={'x-storeClient': store}, params=self._get_kwargs(
                locals_=locals(), excludes=['store'], exclude_nones=True
            )
        )

    async def get_order_status(self, order_id: str, store: str) -> t.Dict:
        return await self._get(f'deals/{order_id}', signed=False, headers={'x-storeClient': store})

    async def close_connection(self):
        if self.session:
            assert self.session
            await self.session.close()

    def __del__(self):
        asyncio.get_event_loop().create_task(self.close_connection())
