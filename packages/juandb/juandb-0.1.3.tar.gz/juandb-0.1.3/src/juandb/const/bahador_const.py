from enum import Enum


__all__ = [
    'COINS',
    'TYPES',
    'STATUS'
]


class _Enum(Enum):
    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def dict(cls):
        return {str(e.value): e.value for e in cls}

    @classmethod
    def get(cls, key: str = None):
        if key is None:
            return cls.dict()
        return cls.dict().get(key)


class COINS(_Enum):
    BITCOIN = 'BITCOIN'
    TETHER = 'TETHER'
    ETHEREUM = 'ETHEREUM'
    TOMAN = 'TOMAN'
    RIPPLE = 'RIPPLE'
    BITCOIN_CASH = 'BITCOIN_CASH'
    LITE_COIN = 'LITE_COIN'
    EOS = 'EOS'
    STELLAR = 'STELLAR'
    TRON = 'TRON'
    PAXG = 'PAXG'
    DASH = 'DASH'
    BINANCE_COIN = 'BINANCE_COIN'
    DOGE = 'DOGE'
    CARDANO = 'CARDANO'
    ATOM = 'ATOM'
    MATIC = 'MATIC'
    FANTOM = 'FANTOM'
    POLKADOT = 'POLKADOT'
    SHIBA = 'SHIBA'
    FIL = 'FIL'
    CAKE = 'CAKE'
    CHAIN_LINK = 'CHAIN_LINK'
    UNISWAP = 'UNISWAP'
    THORCHAIN = 'THORCHAIN'
    CHILIZ = 'CHILIZ'
    BIT_TORRENT = 'BIT_TORRENT'
    DECENTRALAND = 'DECENTRALAND'
    AXIE_INFINITY = 'AXIE_INFINITY'
    SANDBOX = 'SANDBOX'
    ENJIN_COIN = 'ENJIN_COIN'
    MY_NEIGHBOR_ALICE = 'MY_NEIGHBOR_ALICE'
    ELROND_EGOLD = 'ELROND_EGOLD'
    AVALANCHE = 'AVALANCHE'
    NEAR_PROTOCOL = 'NEAR_PROTOCOL'
    SOLANA = 'SOLANA'
    TEZOS = 'TEZOS'
    DAI = 'DAI'
    ETHEREUM_CLASSIC = 'ETHEREUM_CLASSIC'
    GALA = 'GALA'
    AAVE = 'AAVE'
    MAKER = 'MAKER'
    ONE_INCH_NETWORK = 'ONE_INCH_NETWORK'
    YFI = 'YFI'
    CELR = 'CELR'
    APE = 'APE'
    POLKASTARTER = 'POLKASTARTER'
    STEPN = 'STEPN'

    @classmethod
    def dict(cls):
        return {
            'BTC': cls.BITCOIN.name,
            'USDT': cls.TETHER.name,
            'ETH': cls.ETHEREUM.name,
            'TMN': cls.TOMAN.name,
            'XRP': cls.RIPPLE.name,
            'BCH': cls.BITCOIN_CASH.name,
            'LTC': cls.LITE_COIN.name,
            'EOS': cls.EOS.name,
            'XLM': cls.STELLAR.name,
            'TRX': cls.TRON.name,
            'PAXG': cls.PAXG.name,
            'DASH': cls.DASH.name,
            'BNB': cls.BINANCE_COIN.name,
            'DOGE': cls.DOGE.name,
            'ADA': cls.CARDANO.name,
            'ATOM': cls.ATOM.name,
            'MATIC': cls.MATIC.name,
            'FTM': cls.FANTOM.name,
            'DOT': cls.POLKADOT.name,
            'SHIB': cls.SHIBA.name,
            'FIL': cls.FIL.name,
            'CAKE': cls.CAKE.name,
            'LINK': cls.CHAIN_LINK.name,
            'UNI': cls.UNISWAP.name,
            'RUNE': cls.THORCHAIN.name,
            'CHZ': cls.CHILIZ.name,
            'BTT': cls.BIT_TORRENT.name,
            'MANA': cls.DECENTRALAND.name,
            'AXS': cls.AXIE_INFINITY.name,
            'SAND': cls.SANDBOX.name,
            'ENJ': cls.ENJIN_COIN.name,
            'ALICE': cls.MY_NEIGHBOR_ALICE.name,
            'EGLD': cls.ELROND_EGOLD.name,
            'AVAX': cls.AVALANCHE.name,
            'NEAR': cls.NEAR_PROTOCOL.name,
            'SOL': cls.SOLANA.name,
            'XTZ': cls.TEZOS.name,
            'DAI': cls.DAI.name,
            'ETC': cls.ETHEREUM_CLASSIC.name,
            'GALA': cls.GALA.name,
            'AAVE': cls.AAVE.name,
            'MAKER': cls.MAKER.name,
            '1INCH': cls.ONE_INCH_NETWORK.name,
            'YFI': cls.YFI.name,
            'CELR': cls.CELR.name,
            'APE': cls.APE.name,
            'POLS': cls.POLKASTARTER.name,
            'GMT': cls.STEPN.name
        }


class TYPES(_Enum):
    QUICK = 'QUICK'
    NORMAL = 'NORMAL'

    @classmethod
    def dict(cls):
        return {
            'LIMIT': cls.NORMAL.value,
            'MARKET': cls.QUICK.value
        }


class STATUS(_Enum):
    CREATED = 'CREATED'
    ORDERING = 'ORDERING'
    ORDERED = 'ORDERED'

    FAILED = 'FAILED'
    FINISHED = 'FINISHED'
    CANCELING = 'CANCELING'
    CANCELED = 'CANCELED'
