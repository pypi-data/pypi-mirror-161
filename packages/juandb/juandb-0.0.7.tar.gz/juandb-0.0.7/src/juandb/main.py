import typing as t
from datetime import datetime
import pytz


from .const import COINS, TYPES
from .orders_db_wrapper import JuanORM


# TODO: Sanity check. Not the code, but the code writer ...


class Juan:
    def __init__(self, bot: str, db_url: str):
        self._orm = JuanORM(db_url)

        self._bot: str = bot

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

    def create_order(
            self, store: str, symbol: str, side: str, amount: float,
            price: float, order_type: str,
            reason_information: t.Dict[str, t.Any] = None, deal_groups_id: int = None,
            order_id: str = None, cancel_at: datetime = None
    ) -> JuanORM.Deals:
        src, dst = self._get_src_dst(symbol)

        if side.lower() == 'buy':
            src, dst = dst, src

            estimated_source_amount = amount * price
            estimated_destination_amount = amount

        else:
            estimated_source_amount = amount
            estimated_destination_amount = amount * price

        src = COINS.get(src)
        dst = COINS.get(dst)

        order_type = TYPES.get(order_type.upper())

        if deal_groups_id is None:
            deal_groups_id = self._orm.deal_group__insert(reason_information).id

        _ = self._orm.deals__insert(
            deal_group_id=deal_groups_id,
            store=store,
            source_currency=src,
            destination_currency=dst,
            status='CREATED',
            type_=order_type,
            estimated_source_amount=estimated_source_amount,
            estimated_destination_amount=estimated_destination_amount,
            store_order_id=order_id,
            should_cancel_at=cancel_at,
            bot=self._bot,
        )

        return _

    def cancel_order(self, db_id: int = None, store_order_id: str = None) -> JuanORM.Deals:
        if not (db_id or store_order_id):
            raise ValueError('Either db_id or store_order_id must be provided')
        return self._orm.deals__update(db_id, store_order_id=store_order_id, should_cancel_at=datetime.now(
            pytz.timezone('Asia/Tehran')
        ))

    def open_orders(self, type_: str = None, side: str = None) -> t.List[JuanORM.Deals]:
        if side is not None:
            raise NotImplementedError('Side filtering is not implemented')

        return self._orm.deals__get(bot=self._bot, type_=type_)

    def order_status(self, db_id: int = None, store_order_id: t.Any = None) -> t.List[JuanORM.Deals]:
        if not (db_id or store_order_id):
            raise ValueError('Either db_id or store_order_id must be provided')

        return self._orm.deals__get(id=db_id, store_order_id=store_order_id)

    def create_deal_group(self, reason_information: t.Dict[str, t.Any]) -> JuanORM.DealGroups:
        return self._orm.deal_group__insert(reason_information)
