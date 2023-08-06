import typing as t

from sqlalchemy import create_engine
from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, JSON, DECIMAL, Integer, Boolean, text
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import PendingRollbackError, IntegrityError

from datetime import datetime
import pytz

import json


def _get_kwargs(params: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    try:
        params.pop('self')
    except KeyError:
        pass
    return {k: v for k, v in params.items() if v is not None}


class JuanORM:
    __BASE = declarative_base()

    def __init__(self, db_url: str, create_tables: bool = False):
        self._engine = create_engine(db_url)
        self._engine.connect()

        self._Base = self.__BASE
        self._Base.bind = self._engine

        self._Session = sessionmaker(bind=self._engine)
        self._session = self._Session()

        if create_tables is True:
            self.create_tables()

    @staticmethod
    def serialize(result: t.List) -> t.List[t.Dict[str, t.Any]]:
        return [_.dict() for _ in result]

    def _add(self, obj: object):
        try:
            self._session.add(obj)
        except PendingRollbackError:
            self._rollback()
        except Exception as e:
            print(e)
            self._session.rollback()

    def _commit(self):
        try:
            self._session.commit()
        except PendingRollbackError:
            self._rollback()
        except IntegrityError:
            self._session.rollback()
        except Exception as e:
            print(e)
            self._session.rollback()

    def _rollback(self):
        self._session.rollback()

    def _query(self, table) -> Query:
        try:
            self._session.commit()
        except PendingRollbackError:
            self._rollback()
        except Exception as e:
            self._rollback()
            raise e

        try:
            return self._session.query(table)
        except Exception as e:
            print(e)
            self._rollback()

    def _add_commit(self, obj: object):
        self._add(obj)
        self._commit()

    def _execute(self, sql: str):
        try:
            self._session.execute(sql)
        except PendingRollbackError:
            self._rollback()
        except Exception as e:
            print(e)
            self._session.rollback()

    def _execute_sql(self, sql: str):
        self._execute(sql)
        self._commit()

    def create_tables(self):
        self._Base.metadata.create_all(self._engine)

    def drop_table(self, table: str):
        self._Base.metadata.tables[table].drop(self._engine)

    def drop_all_tables(self):
        self._Base.metadata.drop_all(self._engine)

    def recreate_all_tables(self):
        self.drop_all_tables()
        self.create_tables()

    class DealGroups(__BASE):
        __tablename__ = 'deal_groups'

        id = Column(BigInteger, primary_key=True, autoincrement=True)
        reason_information = Column(JSON, nullable=True)
        created_at = Column(DateTime, nullable=True, default=None)
        updated_at = Column(DateTime, nullable=True, default=None)

        def __repr__(self):
            return f'<DealGroups(id={self.id}, ' \
                   f'reason_information={self.reason_information}, ' \
                   f'created_at={self.created_at}, ' \
                   f'updated_at={self.updated_at})>'

        def __str__(self):
            return str(self.__repr__())

        def dict(self) -> t.Dict[str, t.Union[str, t.Dict, datetime]]:
            return {
                'id': self.id,
                'reason_information': self.reason_information,
                'created_at': self.created_at,
                'updated_at': self.updated_at
            }

        def json(self):
            return json.dumps(self.dict())

    def deal_group__get(
            self, id: int, reason_information: t.Dict = None, created_at: str = None, updated_at: str = None
    ) -> t.List[DealGroups]:
        kwargs: t.Dict[str, t.Any] = _get_kwargs(locals())

        # get self.Deals with given parameters
        data = self._query(self.DealGroups).filter_by(**kwargs).all()
        return data

    def deal_group__insert(
            self, reason_information: t.Dict = None, created_at: str = None, updated_at: str = None
    ) -> DealGroups:

        if created_at is None:
            created_at = datetime.now(tz=pytz.timezone('Asia/Tehran'))
        if updated_at is None:
            updated_at = datetime.now(tz=pytz.timezone('Asia/Tehran'))

        _ = self.DealGroups(
            reason_information=reason_information,
            created_at=created_at,
            updated_at=updated_at
        )
        self._add_commit(_)
        return _

    def deal_group__update(
            self, id: int, reason_information: str = None, created_at: str = None, updated_at: str = None
    ) -> DealGroups:
        kwargs = _get_kwargs(locals())

        if len(kwargs) == 0:
            raise ValueError('Nothing to update')

        kwargs['updated_at'] = datetime.now(tz=pytz.timezone('Asia/Tehran'))

        _ = self.DealGroups.__table__.update().where(self.DealGroups.id == id).values(**kwargs)
        self._add_commit(_)

        # _ = self._query(self.DealGroups).filter(self.DealGroups.id == id).update(d)
        self._commit()

        return _

    def deal_group__delete(self, id: int):
        self._query(self.DealGroups).filter(self.DealGroups.id == id).delete()
        self._commit()

    class Deals(__BASE):
        __tablename__ = 'deals'

        id = Column(BigInteger, primary_key=True, autoincrement=True)
        deal_group_id = Column(BigInteger, ForeignKey('deal_groups.id'), nullable=False)
        store = Column(String(255), nullable=False)
        source_currency = Column(String(255), nullable=False)
        destination_currency = Column(String(255), nullable=False)
        estimated_source_amount = Column(DECIMAL(30, 15), nullable=True, default=None)
        processed_source_amount = Column(DECIMAL(30, 15), nullable=True, default=None)
        estimated_destination_amount = Column(DECIMAL(30, 15), nullable=True, default=None)
        processed_destination_amount = Column(DECIMAL(30, 15), nullable=True, default=None)
        status = Column(String(255), nullable=False)
        type = Column(String(255), nullable=False)
        processed_at = Column(DateTime, nullable=True, default=None)
        should_cancel_at = Column(DateTime, nullable=True, default=None)
        finalized_at = Column(DateTime, nullable=True, default=None)
        created_at = Column(DateTime, nullable=True, default=None)
        updated_at = Column(DateTime, nullable=True, default=None)
        store_order_id = Column(String(255), nullable=True, default=None)
        logs = Column(JSON, nullable=True, default=None)
        bot = Column(String(255), nullable=True, default=None)
        owner_type = Column(String(255), nullable=True, default=None)
        owner_id = Column(BigInteger, nullable=True, default=None)

        def __repr__(self):
            return f'<Deal(id={self.id}, ' \
                   f'deal_group_id={self.deal_group_id}, ' \
                   f'store={self.store}, ' \
                   f'source_currency={self.source_currency}, ' \
                   f'destination_currency={self.destination_currency}, ' \
                   f'estimated_source_amount={self.estimated_source_amount}, ' \
                   f'processed_source_amount={self.processed_source_amount}, ' \
                   f'estimated_destination_amount={self.estimated_destination_amount}, ' \
                   f'processed_destination_amount={self.processed_destination_amount}, ' \
                   f'status={self.status}, ' \
                   f'type={self.type}, ' \
                   f'processed_at={self.processed_at}, ' \
                   f'should_cancel_at={self.should_cancel_at}, ' \
                   f'finalized_at={self.finalized_at}, ' \
                   f'created_at={self.created_at}, ' \
                   f'updated_at={self.updated_at}, ' \
                   f'store_order_id={self.store_order_id}, ' \
                   f'logs={self.logs}, ' \
                   f'bot={self.bot}, ' \
                   f'owner_type={self.owner_type}, ' \
                   f'owner_id={self.owner_id})>'

        def __str__(self):
            return str(self.__repr__())

        def dict(self):
            return {
                'id': self.id,
                'deal_group_id': self.deal_group_id,
                'store': self.store,
                'source_currency': self.source_currency,
                'destination_currency': self.destination_currency,
                'estimated_source_amount': self.estimated_source_amount,
                'processed_source_amount': self.processed_source_amount,
                'estimated_destination_amount': self.estimated_destination_amount,
                'processed_destination_amount': self.processed_destination_amount,
                'status': self.status,
                'type': self.type,
                'processed_at': self.processed_at,
                'should_cancel_at': self.should_cancel_at,
                'finalized_at': self.finalized_at,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'store_order_id': self.store_order_id,
                'logs': self.logs,
                'bot': self.bot,
                'owner_type': self.owner_type,
                'owner_id': self.owner_id
            }

        def json(self):
            return json.dumps(self.dict())

    def deals__get(
            self,
            id: int = None,
            deal_group_id: int = None,
            store: str = None,
            source_currency: str = None,
            destination_currency: str = None,
            status: str = None,
            type_: str = None,
            estimated_source_amount: float = None,
            processed_source_amount: float = None,
            estimated_destination_amount: float = None,
            processed_destination_amount: float = None,
            processed_at: datetime = None,
            should_cancel_at: datetime = None,
            finalized_at: datetime = None,
            created_at: datetime = None,
            updated_at: datetime = None,
            store_order_id: str = None,
            logs: str = None,
            bot: str = None,
            owner_type: str = None,
            owner_id: int = None
    ) -> t.List[Deals]:
        kwargs: t.Dict[str, t.Any] = _get_kwargs(locals())

        # get self.Deals with given parameters
        data = self._query(self.Deals).filter_by(**kwargs).all()
        return data

    def deals__insert(
            self,
            deal_group_id: int,
            store: str,
            source_currency: str,
            destination_currency: str,
            status: str,
            type_: str,
            estimated_source_amount: float = None,
            processed_source_amount: float = None,
            estimated_destination_amount: float = None,
            processed_destination_amount: float = None,
            processed_at: datetime = None,
            should_cancel_at: datetime = None,
            finalized_at: datetime = None,
            created_at: datetime = None,
            updated_at: datetime = None,
            store_order_id: str = None,
            logs: str = None,
            bot: str = None,
            owner_type: str = None,
            owner_id: int = None
    ) -> Deals:
        if created_at is None:
            created_at = datetime.now()
        if updated_at is None:
            updated_at = datetime.now()

        _ = self.Deals(
            deal_group_id=deal_group_id, store=store, source_currency=source_currency,
            destination_currency=destination_currency, estimated_source_amount=estimated_source_amount,
            processed_source_amount=processed_source_amount, estimated_destination_amount=estimated_destination_amount,
            processed_destination_amount=processed_destination_amount, status=status, type=type_,
            processed_at=processed_at, should_cancel_at=should_cancel_at, finalized_at=finalized_at,
            created_at=created_at, updated_at=updated_at, store_order_id=store_order_id,
            logs=logs, bot=bot, owner_type=owner_type, owner_id=owner_id
        )
        self._add_commit(_)
        return _

    def deals__update(
            self,
            id: int = None,
            deal_group_id: int = None,
            store: str = None,
            source_currency: str = None,
            destination_currency: str = None,
            status: str = None,
            type_: str = None,
            estimated_source_amount: float = None,
            processed_source_amount: float = None,
            estimated_destination_amount: float = None,
            processed_destination_amount: float = None,
            processed_at: datetime = None,
            should_cancel_at: datetime = None,
            finalized_at: datetime = None,
            created_at: datetime = None,
            updated_at: datetime = None,
            store_order_id: str = None,
            logs: str = None,
            bot: str = None,
            owner_type: str = None,
            owner_id: int = None
    ):
        kwargs = _get_kwargs(locals())
        if len(kwargs) == 0:
            raise ValueError('Nothing to update')

        kwargs['updated_at'] = datetime.utcnow()

        if 'id' in kwargs.keys():
            self._query(self.Deals).filter_by(id=id).update(kwargs)
        elif 'store_order_id' in kwargs.keys():
            self._query(self.Deals).filter_by(store_order_id=store_order_id).update(kwargs)
        else:
            raise ValueError('Either id or store_order_id must be specified')

        self._commit()

    def deals__delete(self, id: int):
        self._query(self.Deals).filter_by(id=id).delete()
        self._commit()

    class CoinMap(__BASE):
        __tablename__ = 'coin_map'
        id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True, index=True, doc='ID')
        symbol = Column(String(255), nullable=False, unique=True)
        name = Column(String(255), nullable=False, unique=True)
        is_active = Column(Boolean, nullable=False, default=True, server_default=text('true'))
        is_fiat = Column(Boolean, nullable=False, default=False, server_default=text('false'))
        is_crypto = Column(Boolean, nullable=False, default=True, server_default=text('true'))
        created_at = Column(DateTime, nullable=False, server_default=text('now()'))
        updated_at = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))

        def __repr__(self):
            return f'<CoinMap(id={self.id}, ' \
                   f'symbol={self.symbol}, ' \
                   f'name={self.name}, ' \
                   f'is_active={self.is_active}, ' \
                   f'is_fiat={self.is_fiat}, ' \
                   f'is_crypto={self.is_crypto}, ' \
                   f'created_at={self.created_at}, ' \
                   f'updated_at={self.updated_at})>'

        def __str__(self):
            return self.__repr__()

        def dict(self):
            return {
                'id': self.id,
                'symbol': self.symbol,
                'name': self.name,
                'is_active': self.is_active,
                'is_fiat': self.is_fiat,
                'is_crypto': self.is_crypto,
                'created_at': self.created_at,
                'updated_at': self.updated_at
            }

        def json(self):
            return json.dumps(self.dict())

    def coin_map__insert(
            self, symbol: str, name: str, is_active: bool = True, is_fiat: bool = False,
            is_crypto: bool = True
    ) -> CoinMap:
        _ = self.CoinMap(
            symbol=symbol,
            name=name,
            is_active=is_active,
            is_fiat=is_fiat,
            is_crypto=is_crypto,
        )
        self._add_commit(_)

        return _

    def coin_map__get(self, id: int = None, symbol: str = None, name: str = None) -> t.List[CoinMap]:
        kwargs: t.Dict[str, t.Any] = _get_kwargs(locals())

        # get self.Deals with given parameters
        data = self._query(self.CoinMap).filter_by(**kwargs).all()
        return data

    def coin_map__map(self):
        data = self.coin_map__get()
        _ = {}

        for coin in data:
            _[coin.symbol] = coin.name

        return _
