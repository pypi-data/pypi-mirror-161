from enum import Enum


class _NiceEnum(Enum):
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


class CURRENCIES:
    class PAXGTMN(_NiceEnum):
        symbol = 'PAXGTMN'
        baseAsset = 'PAXG'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'پکسوس گلد - تومان'
        faBaseAsset = 'پکسوس گلد'
        faQuoteAsset = 'تومان'
        stepSize = 6
        tickSize = 0
        minQty = 1e-06
        minNotional = 100000

    class PAXGUSDT(_NiceEnum):
        symbol = 'PAXGUSDT'
        baseAsset = 'PAXG'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'پکسوس گلد - تتر'
        faBaseAsset = 'پکسوس گلد'
        faQuoteAsset = 'تتر'
        stepSize = 6
        tickSize = 2
        minQty = 1e-06
        minNotional = 10

    class PAXGBTC(_NiceEnum):
        symbol = 'PAXGBTC'
        baseAsset = 'PAXG'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'پکسوس گلد - بیت کوین'
        faBaseAsset = 'پکسوس گلد'
        faQuoteAsset = 'بیت کوین'
        stepSize = 4
        tickSize = 5
        minQty = 0.0001
        minNotional = 0.0001

    class ONEINCHTMN(_NiceEnum):
        symbol = '1INCHTMN'
        baseAsset = '1INCH'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'وان اینچ - تومان'
        faBaseAsset = 'وان اینچ'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class ONEINCHUSDT(_NiceEnum):
        symbol = '1INCHUSDT'
        baseAsset = '1INCH'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'وان اینچ - تتر'
        faBaseAsset = 'وان اینچ'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 3
        minQty = 0.1
        minNotional = 10

    class ONEINCHBTC(_NiceEnum):
        symbol = '1INCHBTC'
        baseAsset = '1INCH'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'وان اینچ - بیت کوین'
        faBaseAsset = 'وان اینچ'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class YFITMN(_NiceEnum):
        symbol = 'YFITMN'
        baseAsset = 'YFI'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'یرن فایننس - تومان'
        faBaseAsset = 'یرن فایننس'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class YFIUSDT(_NiceEnum):
        symbol = 'YFIUSDT'
        baseAsset = 'YFI'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'یرن فایننس - تتر'
        faBaseAsset = 'یرن فایننس'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class YFIBTC(_NiceEnum):
        symbol = 'YFIBTC'
        baseAsset = 'YFI'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'یرن فایننس - بیت کوین'
        faBaseAsset = 'یرن فایننس'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class CELRTMN(_NiceEnum):
        symbol = 'CELRTMN'
        baseAsset = 'CELR'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'سلر - تومان'
        faBaseAsset = 'سلر'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class CELRUSDT(_NiceEnum):
        symbol = 'CELRUSDT'
        baseAsset = 'CELR'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'سلر - تتر'
        faBaseAsset = 'سلر'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class CELRBTC(_NiceEnum):
        symbol = 'CELRBTC'
        baseAsset = 'CELR'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'سلر - بیت کوین'
        faBaseAsset = 'سلر'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class APETMN(_NiceEnum):
        symbol = 'APETMN'
        baseAsset = 'APE'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'ایپ کوین - تومان'
        faBaseAsset = 'ایپ کوین'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class APEUSDT(_NiceEnum):
        symbol = 'APEUSDT'
        baseAsset = 'APE'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'ایپ کوین - تتر'
        faBaseAsset = 'ایپ کوین'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 3
        minQty = 0.01
        minNotional = 10

    class APEBTC(_NiceEnum):
        symbol = 'APEBTC'
        baseAsset = 'APE'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'ایپ کوین - بیت کوین'
        faBaseAsset = 'ایپ کوین'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class POLSTMN(_NiceEnum):
        symbol = 'POLSTMN'
        baseAsset = 'POLS'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'پولکا استارتر - تومان'
        faBaseAsset = 'پولکا استارتر'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class POLSUSDT(_NiceEnum):
        symbol = 'POLSUSDT'
        baseAsset = 'POLS'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'پولکا استارتر - تتر'
        faBaseAsset = 'پولکا استارتر'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class POLSBTC(_NiceEnum):
        symbol = 'POLSBTC'
        baseAsset = 'POLS'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'پولکا استارتر - بیت کوین'
        faBaseAsset = 'پولکا استارتر'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class DAITMN(_NiceEnum):
        symbol = 'DAITMN'
        baseAsset = 'DAI'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'دای - تومان'
        faBaseAsset = 'دای'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class AAVETMN(_NiceEnum):
        symbol = 'AAVETMN'
        baseAsset = 'AAVE'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'آوه - تومان'
        faBaseAsset = 'آوه'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class AAVEUSDT(_NiceEnum):
        symbol = 'AAVEUSDT'
        baseAsset = 'AAVE'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'آوه - تتر'
        faBaseAsset = 'آوه'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class AAVEBTC(_NiceEnum):
        symbol = 'AAVEBTC'
        baseAsset = 'AAVE'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'آوه - بیت کوین'
        faBaseAsset = 'آوه'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class GALATMN(_NiceEnum):
        symbol = 'GALATMN'
        baseAsset = 'GALA'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'گالا - تومان'
        faBaseAsset = 'گالا'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class GALAUSDT(_NiceEnum):
        symbol = 'GALAUSDT'
        baseAsset = 'GALA'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'گالا - تتر'
        faBaseAsset = 'گالا'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class GALABTC(_NiceEnum):
        symbol = 'GALABTC'
        baseAsset = 'GALA'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'گالا - بیت کوین'
        faBaseAsset = 'گالا'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class ETCTMN(_NiceEnum):
        symbol = 'ETCTMN'
        baseAsset = 'ETC'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'اتریوم کلاسیک - تومان'
        faBaseAsset = 'اتریوم کلاسیک'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class ETCUSDT(_NiceEnum):
        symbol = 'ETCUSDT'
        baseAsset = 'ETC'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'اتریوم کلاسیک - تتر'
        faBaseAsset = 'اتریوم کلاسیک'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class ETCBTC(_NiceEnum):
        symbol = 'ETCBTC'
        baseAsset = 'ETC'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'اتریوم کلاسیک - بیت کوین'
        faBaseAsset = 'اتریوم کلاسیک'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class MKRTMN(_NiceEnum):
        symbol = 'MKRTMN'
        baseAsset = 'MKR'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'میکر - تومان'
        faBaseAsset = 'میکر'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class MKRUSDT(_NiceEnum):
        symbol = 'MKRUSDT'
        baseAsset = 'MKR'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'میکر - تتر'
        faBaseAsset = 'میکر'
        faQuoteAsset = 'تتر'
        stepSize = 4
        tickSize = 2
        minQty = 0.0001
        minNotional = 10

    class MKRBTC(_NiceEnum):
        symbol = 'MKRBTC'
        baseAsset = 'MKR'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'میکر - بیت کوین'
        faBaseAsset = 'میکر'
        faQuoteAsset = 'بیت کوین'
        stepSize = 4
        tickSize = 5
        minQty = 0.0001
        minNotional = 0.0001

    class BTCTMN(_NiceEnum):
        symbol = 'BTCTMN'
        baseAsset = 'BTC'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'بیت کوین - تومان'
        faBaseAsset = 'بیت کوین'
        faQuoteAsset = 'تومان'
        stepSize = 6
        tickSize = 0
        minQty = 1e-06
        minNotional = 100000

    class BTCUSDT(_NiceEnum):
        symbol = 'BTCUSDT'
        baseAsset = 'BTC'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'بیت کوین - تتر'
        faBaseAsset = 'بیت کوین'
        faQuoteAsset = 'تتر'
        stepSize = 6
        tickSize = 2
        minQty = 1e-06
        minNotional = 10

    class ETHTMN(_NiceEnum):
        symbol = 'ETHTMN'
        baseAsset = 'ETH'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'اتریوم - تومان'
        faBaseAsset = 'اتریوم'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class ETHUSDT(_NiceEnum):
        symbol = 'ETHUSDT'
        baseAsset = 'ETH'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'اتریوم - تتر'
        faBaseAsset = 'اتریوم'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class ETHBTC(_NiceEnum):
        symbol = 'ETHBTC'
        baseAsset = 'ETH'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'اتریوم - بیت کوین'
        faBaseAsset = 'اتریوم'
        faQuoteAsset = 'بیت کوین'
        stepSize = 3
        tickSize = 6
        minQty = 0.001
        minNotional = 0.0001

    class DOGETMN(_NiceEnum):
        symbol = 'DOGETMN'
        baseAsset = 'DOGE'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'دوج کوین - تومان'
        faBaseAsset = 'دوج کوین'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class DOGEUSDT(_NiceEnum):
        symbol = 'DOGEUSDT'
        baseAsset = 'DOGE'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'دوج کوین - تتر'
        faBaseAsset = 'دوج کوین'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class DOGEBTC(_NiceEnum):
        symbol = 'DOGEBTC'
        baseAsset = 'DOGE'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'دوج کوین - بیت کوین'
        faBaseAsset = 'دوج کوین'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class BCHTMN(_NiceEnum):
        symbol = 'BCHTMN'
        baseAsset = 'BCH'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'بیت کوین کش - تومان'
        faBaseAsset = 'بیت کوین کش'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class BCHUSDT(_NiceEnum):
        symbol = 'BCHUSDT'
        baseAsset = 'BCH'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'بیت کوین کش - تتر'
        faBaseAsset = 'بیت کوین کش'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class BCHBTC(_NiceEnum):
        symbol = 'BCHBTC'
        baseAsset = 'BCH'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'بیت کوین کش - بیت کوین'
        faBaseAsset = 'بیت کوین کش'
        faQuoteAsset = 'بیت کوین'
        stepSize = 3
        tickSize = 6
        minQty = 0.001
        minNotional = 0.0001

    class LTCTMN(_NiceEnum):
        symbol = 'LTCTMN'
        baseAsset = 'LTC'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'لایت کوین - تومان'
        faBaseAsset = 'لایت کوین'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class LTCUSDT(_NiceEnum):
        symbol = 'LTCUSDT'
        baseAsset = 'LTC'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'لایت کوین - تتر'
        faBaseAsset = 'لایت کوین'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class LTCBTC(_NiceEnum):
        symbol = 'LTCBTC'
        baseAsset = 'LTC'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'لایت کوین - بیت کوین'
        faBaseAsset = 'لایت کوین'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class DASHTMN(_NiceEnum):
        symbol = 'DASHTMN'
        baseAsset = 'DASH'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'دش - تومان'
        faBaseAsset = 'دش'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class DASHUSDT(_NiceEnum):
        symbol = 'DASHUSDT'
        baseAsset = 'DASH'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'دش - تتر'
        faBaseAsset = 'دش'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class DASHBTC(_NiceEnum):
        symbol = 'DASHBTC'
        baseAsset = 'DASH'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'دش - بیت کوین'
        faBaseAsset = 'دش'
        faQuoteAsset = 'بیت کوین'
        stepSize = 3
        tickSize = 6
        minQty = 0.001
        minNotional = 0.0001

    class USDTTMN(_NiceEnum):
        symbol = 'USDTTMN'
        baseAsset = 'USDT'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'تتر - تومان'
        faBaseAsset = 'تتر'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class XRPTMN(_NiceEnum):
        symbol = 'XRPTMN'
        baseAsset = 'XRP'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'ریپل - تومان'
        faBaseAsset = 'ریپل'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class XRPUSDT(_NiceEnum):
        symbol = 'XRPUSDT'
        baseAsset = 'XRP'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'ریپل - تتر'
        faBaseAsset = 'ریپل'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class XRPBTC(_NiceEnum):
        symbol = 'XRPBTC'
        baseAsset = 'XRP'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'ریپل - بیت کوین'
        faBaseAsset = 'ریپل'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class XLMTMN(_NiceEnum):
        symbol = 'XLMTMN'
        baseAsset = 'XLM'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'استلار - تومان'
        faBaseAsset = 'استلار'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class XLMUSDT(_NiceEnum):
        symbol = 'XLMUSDT'
        baseAsset = 'XLM'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'استلار - تتر'
        faBaseAsset = 'استلار'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class XLMBTC(_NiceEnum):
        symbol = 'XLMBTC'
        baseAsset = 'XLM'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'استلار - بیت کوین'
        faBaseAsset = 'استلار'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class EOSTMN(_NiceEnum):
        symbol = 'EOSTMN'
        baseAsset = 'EOS'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'ایاس - تومان'
        faBaseAsset = 'ایاس'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class EOSUSDT(_NiceEnum):
        symbol = 'EOSUSDT'
        baseAsset = 'EOS'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'ایاس - تتر'
        faBaseAsset = 'ایاس'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 4
        minQty = 0.01
        minNotional = 10

    class EOSBTC(_NiceEnum):
        symbol = 'EOSBTC'
        baseAsset = 'EOS'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'ایاس - بیت کوین'
        faBaseAsset = 'ایاس'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 7
        minQty = 0.01
        minNotional = 0.0001

    class TRXTMN(_NiceEnum):
        symbol = 'TRXTMN'
        baseAsset = 'TRX'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'ترون - تومان'
        faBaseAsset = 'ترون'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class TRXUSDT(_NiceEnum):
        symbol = 'TRXUSDT'
        baseAsset = 'TRX'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'ترون - تتر'
        faBaseAsset = 'ترون'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class TRXBTC(_NiceEnum):
        symbol = 'TRXBTC'
        baseAsset = 'TRX'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'ترون - بیت کوین'
        faBaseAsset = 'ترون'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class ADATMN(_NiceEnum):
        symbol = 'ADATMN'
        baseAsset = 'ADA'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'کاردانو - تومان'
        faBaseAsset = 'کاردانو'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class ADAUSDT(_NiceEnum):
        symbol = 'ADAUSDT'
        baseAsset = 'ADA'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'کاردانو - تتر'
        faBaseAsset = 'کاردانو'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 3
        minQty = 0.1
        minNotional = 10

    class ADABTC(_NiceEnum):
        symbol = 'ADABTC'
        baseAsset = 'ADA'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'کاردانو - بیت کوین'
        faBaseAsset = 'کاردانو'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class BNBTMN(_NiceEnum):
        symbol = 'BNBTMN'
        baseAsset = 'BNB'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'بایننس کوین - تومان'
        faBaseAsset = 'بایننس کوین'
        faQuoteAsset = 'تومان'
        stepSize = 3
        tickSize = 0
        minQty = 0.001
        minNotional = 100000

    class BNBUSDT(_NiceEnum):
        symbol = 'BNBUSDT'
        baseAsset = 'BNB'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'بایننس کوین - تتر'
        faBaseAsset = 'بایننس کوین'
        faQuoteAsset = 'تتر'
        stepSize = 3
        tickSize = 4
        minQty = 0.001
        minNotional = 10

    class BNBBTC(_NiceEnum):
        symbol = 'BNBBTC'
        baseAsset = 'BNB'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'بایننس کوین - بیت کوین'
        faBaseAsset = 'بایننس کوین'
        faQuoteAsset = 'بیت کوین'
        stepSize = 3
        tickSize = 5
        minQty = 0.001
        minNotional = 0.0001

    class ATOMTMN(_NiceEnum):
        symbol = 'ATOMTMN'
        baseAsset = 'ATOM'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'اتم - تومان'
        faBaseAsset = 'اتم'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class ATOMUSDT(_NiceEnum):
        symbol = 'ATOMUSDT'
        baseAsset = 'ATOM'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'اتم - تتر'
        faBaseAsset = 'اتم'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class ATOMBTC(_NiceEnum):
        symbol = 'ATOMBTC'
        baseAsset = 'ATOM'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'اتم - بیت کوین'
        faBaseAsset = 'اتم'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class MATICTMN(_NiceEnum):
        symbol = 'MATICTMN'
        baseAsset = 'MATIC'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'متیک - تومان'
        faBaseAsset = 'متیک'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class MATICUSDT(_NiceEnum):
        symbol = 'MATICUSDT'
        baseAsset = 'MATIC'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'متیک - تتر'
        faBaseAsset = 'متیک'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 3
        minQty = 0.1
        minNotional = 10

    class MATICBTC(_NiceEnum):
        symbol = 'MATICBTC'
        baseAsset = 'MATIC'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'متیک - بیت کوین'
        faBaseAsset = 'متیک'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class FTMTMN(_NiceEnum):
        symbol = 'FTMTMN'
        baseAsset = 'FTM'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'فانتوم - تومان'
        faBaseAsset = 'فانتوم'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class FTMUSDT(_NiceEnum):
        symbol = 'FTMUSDT'
        baseAsset = 'FTM'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'فانتوم - تتر'
        faBaseAsset = 'فانتوم'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 4
        minQty = 0.01
        minNotional = 10

    class FTMBTC(_NiceEnum):
        symbol = 'FTMBTC'
        baseAsset = 'FTM'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'فانتوم - بیت کوین'
        faBaseAsset = 'فانتوم'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class DOTTMN(_NiceEnum):
        symbol = 'DOTTMN'
        baseAsset = 'DOT'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'پولکادات - تومان'
        faBaseAsset = 'پولکادات'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class DOTUSDT(_NiceEnum):
        symbol = 'DOTUSDT'
        baseAsset = 'DOT'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'پولکادات - تتر'
        faBaseAsset = 'پولکادات'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 3
        minQty = 0.01
        minNotional = 10

    class DOTBTC(_NiceEnum):
        symbol = 'DOTBTC'
        baseAsset = 'DOT'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'پولکادات - بیت کوین'
        faBaseAsset = 'پولکادات'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class SHIBTMN(_NiceEnum):
        symbol = 'SHIBTMN'
        baseAsset = 'SHIB'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'شیبا - تومان'
        faBaseAsset = 'شیبا'
        faQuoteAsset = 'تومان'
        stepSize = 0
        tickSize = 3
        minQty = 1
        minNotional = 100000

    class SHIBUSDT(_NiceEnum):
        symbol = 'SHIBUSDT'
        baseAsset = 'SHIB'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'شیبا - تتر'
        faBaseAsset = 'شیبا'
        faQuoteAsset = 'تتر'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 10

    class FILTMN(_NiceEnum):
        symbol = 'FILTMN'
        baseAsset = 'FIL'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'فایل کوین - تومان'
        faBaseAsset = 'فایل کوین'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class FILUSDT(_NiceEnum):
        symbol = 'FILUSDT'
        baseAsset = 'FIL'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'فایل کوین - تتر'
        faBaseAsset = 'فایل کوین'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class FILBTC(_NiceEnum):
        symbol = 'FILBTC'
        baseAsset = 'FIL'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'فایل کوین - بیت کوین'
        faBaseAsset = 'فایل کوین'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class CAKETMN(_NiceEnum):
        symbol = 'CAKETMN'
        baseAsset = 'CAKE'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'پن کیک سوآپ - تومان'
        faBaseAsset = 'پن کیک سوآپ'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class CAKEUSDT(_NiceEnum):
        symbol = 'CAKEUSDT'
        baseAsset = 'CAKE'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'پن کیک سوآپ - تتر'
        faBaseAsset = 'پن کیک سوآپ'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class CAKEBTC(_NiceEnum):
        symbol = 'CAKEBTC'
        baseAsset = 'CAKE'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'پن کیک سوآپ - بیت کوین'
        faBaseAsset = 'پن کیک سوآپ'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class LINKTMN(_NiceEnum):
        symbol = 'LINKTMN'
        baseAsset = 'LINK'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'چین لینک - تومان'
        faBaseAsset = 'چین لینک'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class LINKUSDT(_NiceEnum):
        symbol = 'LINKUSDT'
        baseAsset = 'LINK'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'چین لینک - تتر'
        faBaseAsset = 'چین لینک'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class LINKBTC(_NiceEnum):
        symbol = 'LINKBTC'
        baseAsset = 'LINK'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'چین لینک - بیت کوین'
        faBaseAsset = 'چین لینک'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class UNITMN(_NiceEnum):
        symbol = 'UNITMN'
        baseAsset = 'UNI'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'یونی سوآپ - تومان'
        faBaseAsset = 'یونی سوآپ'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class UNIUSDT(_NiceEnum):
        symbol = 'UNIUSDT'
        baseAsset = 'UNI'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'یونی سوآپ - تتر'
        faBaseAsset = 'یونی سوآپ'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class UNIBTC(_NiceEnum):
        symbol = 'UNIBTC'
        baseAsset = 'UNI'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'یونی سوآپ - بیت کوین'
        faBaseAsset = 'یونی سوآپ'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class RUNETMN(_NiceEnum):
        symbol = 'RUNETMN'
        baseAsset = 'RUNE'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'تورچین - تومان'
        faBaseAsset = 'تورچین'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class RUNEUSDT(_NiceEnum):
        symbol = 'RUNEUSDT'
        baseAsset = 'RUNE'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'تورچین - تتر'
        faBaseAsset = 'تورچین'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class RUNEBTC(_NiceEnum):
        symbol = 'RUNEBTC'
        baseAsset = 'RUNE'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'تورچین - بیت کوین'
        faBaseAsset = 'تورچین'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class CHZTMN(_NiceEnum):
        symbol = 'CHZTMN'
        baseAsset = 'CHZ'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'چیلیز - تومان'
        faBaseAsset = 'چیلیز'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class CHZUSDT(_NiceEnum):
        symbol = 'CHZUSDT'
        baseAsset = 'CHZ'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'چیلیز - تتر'
        faBaseAsset = 'چیلیز'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 5
        minQty = 0.1
        minNotional = 10

    class CHZBTC(_NiceEnum):
        symbol = 'CHZBTC'
        baseAsset = 'CHZ'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'چیلیز - بیت کوین'
        faBaseAsset = 'چیلیز'
        faQuoteAsset = 'بیت کوین'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 0.0001

    class BTTCTMN(_NiceEnum):
        symbol = 'BTTCTMN'
        baseAsset = 'BTTC'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'بیت تورنت(جدید) - تومان'
        faBaseAsset = 'بیت تورنت(جدید)'
        faQuoteAsset = 'تومان'
        stepSize = 0
        tickSize = 6
        minQty = 1
        minNotional = 100000

    class BTTCUSDT(_NiceEnum):
        symbol = 'BTTCUSDT'
        baseAsset = 'BTTC'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'بیت تورنت(جدید) - تتر'
        faBaseAsset = 'بیت تورنت(جدید)'
        faQuoteAsset = 'تتر'
        stepSize = 0
        tickSize = 8
        minQty = 1
        minNotional = 10

    class MANATMN(_NiceEnum):
        symbol = 'MANATMN'
        baseAsset = 'MANA'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'مانا - تومان'
        faBaseAsset = 'مانا'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class MANAUSDT(_NiceEnum):
        symbol = 'MANAUSDT'
        baseAsset = 'MANA'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'مانا - تتر'
        faBaseAsset = 'مانا'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 3
        minQty = 0.1
        minNotional = 10

    class MANABTC(_NiceEnum):
        symbol = 'MANABTC'
        baseAsset = 'MANA'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'مانا - بیت کوین'
        faBaseAsset = 'مانا'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class AXSTMN(_NiceEnum):
        symbol = 'AXSTMN'
        baseAsset = 'AXS'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'اکسی - تومان'
        faBaseAsset = 'اکسی'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class AXSUSDT(_NiceEnum):
        symbol = 'AXSUSDT'
        baseAsset = 'AXS'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'اکسی - تتر'
        faBaseAsset = 'اکسی'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class AXSBTC(_NiceEnum):
        symbol = 'AXSBTC'
        baseAsset = 'AXS'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'اکسی - بیت کوین'
        faBaseAsset = 'اکسی'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class SANDTMN(_NiceEnum):
        symbol = 'SANDTMN'
        baseAsset = 'SAND'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'سندباکس - تومان'
        faBaseAsset = 'سندباکس'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class SANDUSDT(_NiceEnum):
        symbol = 'SANDUSDT'
        baseAsset = 'SAND'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'سندباکس - تتر'
        faBaseAsset = 'سندباکس'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 3
        minQty = 0.1
        minNotional = 10

    class SANDBTC(_NiceEnum):
        symbol = 'SANDBTC'
        baseAsset = 'SAND'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'سندباکس - بیت کوین'
        faBaseAsset = 'سندباکس'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class ENJTMN(_NiceEnum):
        symbol = 'ENJTMN'
        baseAsset = 'ENJ'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'انجین - تومان'
        faBaseAsset = 'انجین'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class ENJUSDT(_NiceEnum):
        symbol = 'ENJUSDT'
        baseAsset = 'ENJ'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'انجین - تتر'
        faBaseAsset = 'انجین'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 3
        minQty = 0.1
        minNotional = 10

    class ENJBTC(_NiceEnum):
        symbol = 'ENJBTC'
        baseAsset = 'ENJ'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'انجین - بیت کوین'
        faBaseAsset = 'انجین'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class ALICETMN(_NiceEnum):
        symbol = 'ALICETMN'
        baseAsset = 'ALICE'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'آلیس - تومان'
        faBaseAsset = 'آلیس'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class ALICEUSDT(_NiceEnum):
        symbol = 'ALICEUSDT'
        baseAsset = 'ALICE'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'آلیس - تتر'
        faBaseAsset = 'آلیس'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class ALICEBTC(_NiceEnum):
        symbol = 'ALICEBTC'
        baseAsset = 'ALICE'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'آلیس - بیت کوین'
        faBaseAsset = 'آلیس'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class EGLDTMN(_NiceEnum):
        symbol = 'EGLDTMN'
        baseAsset = 'EGLD'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'الروند - تومان'
        faBaseAsset = 'الروند'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class EGLDUSDT(_NiceEnum):
        symbol = 'EGLDUSDT'
        baseAsset = 'EGLD'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'الروند - تتر'
        faBaseAsset = 'الروند'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class EGLDBTC(_NiceEnum):
        symbol = 'EGLDBTC'
        baseAsset = 'EGLD'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'الروند - بیت کوین'
        faBaseAsset = 'الروند'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class AVAXTMN(_NiceEnum):
        symbol = 'AVAXTMN'
        baseAsset = 'AVAX'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'اوالانچ - تومان'
        faBaseAsset = 'اوالانچ'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class AVAXUSDT(_NiceEnum):
        symbol = 'AVAXUSDT'
        baseAsset = 'AVAX'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'اوالانچ - تتر'
        faBaseAsset = 'اوالانچ'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class AVAXBTC(_NiceEnum):
        symbol = 'AVAXBTC'
        baseAsset = 'AVAX'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'اوالانچ - بیت کوین'
        faBaseAsset = 'اوالانچ'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class NEARTMN(_NiceEnum):
        symbol = 'NEARTMN'
        baseAsset = 'NEAR'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'نیر - تومان'
        faBaseAsset = 'نیر'
        faQuoteAsset = 'تومان'
        stepSize = 2
        tickSize = 0
        minQty = 0.01
        minNotional = 100000

    class NEARUSDT(_NiceEnum):
        symbol = 'NEARUSDT'
        baseAsset = 'NEAR'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'نیر - تتر'
        faBaseAsset = 'نیر'
        faQuoteAsset = 'تتر'
        stepSize = 2
        tickSize = 2
        minQty = 0.01
        minNotional = 10

    class NEARBTC(_NiceEnum):
        symbol = 'NEARBTC'
        baseAsset = 'NEAR'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'نیر - بیت کوین'
        faBaseAsset = 'نیر'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001

    class XTZTMN(_NiceEnum):
        symbol = 'XTZTMN'
        baseAsset = 'XTZ'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'تزوس - تومان'
        faBaseAsset = 'تزوس'
        faQuoteAsset = 'تومان'
        stepSize = 1
        tickSize = 0
        minQty = 0.1
        minNotional = 100000

    class XTZUSDT(_NiceEnum):
        symbol = 'XTZUSDT'
        baseAsset = 'XTZ'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'تزوس - تتر'
        faBaseAsset = 'تزوس'
        faQuoteAsset = 'تتر'
        stepSize = 1
        tickSize = 3
        minQty = 0.1
        minNotional = 10

    class XTZBTC(_NiceEnum):
        symbol = 'XTZBTC'
        baseAsset = 'XTZ'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'تزوس - بیت کوین'
        faBaseAsset = 'تزوس'
        faQuoteAsset = 'بیت کوین'
        stepSize = 1
        tickSize = 7
        minQty = 0.1
        minNotional = 0.0001

    class SOLTMN(_NiceEnum):
        symbol = 'SOLTMN'
        baseAsset = 'SOL'
        baseAssetPrecision = 8
        quoteAsset = 'TMN'
        quotePrecision = 0
        faName = 'سولانا - تومان'
        faBaseAsset = 'سولانا'
        faQuoteAsset = 'تومان'
        stepSize = 5
        tickSize = 0
        minQty = 1e-05
        minNotional = 100000

    class SOLUSDT(_NiceEnum):
        symbol = 'SOLUSDT'
        baseAsset = 'SOL'
        baseAssetPrecision = 8
        quoteAsset = 'USDT'
        quotePrecision = 8
        faName = 'سولانا - تتر'
        faBaseAsset = 'سولانا'
        faQuoteAsset = 'تتر'
        stepSize = 5
        tickSize = 2
        minQty = 1e-05
        minNotional = 10

    class SOLBTC(_NiceEnum):
        symbol = 'SOLBTC'
        baseAsset = 'SOL'
        baseAssetPrecision = 8
        quoteAsset = 'BTC'
        quotePrecision = 8
        faName = 'سولانا - بیت کوین'
        faBaseAsset = 'سولانا'
        faQuoteAsset = 'بیت کوین'
        stepSize = 2
        tickSize = 6
        minQty = 0.01
        minNotional = 0.0001
