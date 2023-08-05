"""This is the Norgate Data Zipline interface
"""

__author__ = "NorgateData Pty Ltd"

__all__ = [
    "register_norgatedata_equities_bundle",
    "register_norgatedata_futures_bundle",
    "zipline_futures_root_symbols_dict",
    "translate_futures_symbol",
    "__version__",
    "__author__",
]
import sys
from zipline.data.bundles import register
import pandas as pd
import zipline as zl
if zl.__version__ < '2.2.0':
    from trading_calendars import get_calendar
else:
    from exchange_calendars import get_calendar
import norgatedata
from numpy import empty, where
import re
from zipline.utils.cli import maybe_show_progress
import logbook
from os import environ, cpu_count
import requests
from .version import __version__
from pandas.tseries.offsets import BDay
import multiprocessing as mp

logbook.StreamHandler(sys.stdout).push_application()  # required for Jupyter to output
logger = logbook.Logger("Norgate Data")

norgatedata.norgatehelper.version_checker(__version__, "zipline-norgatedata")

# Translate Norgate symbols into Zipline symbols that are hardcoded in the Zipline package,
# plus avoid overlaps
_symbol_translate = {
    "6A": "AD",  # AUD
    "6B": "BP",  # GBP
    "6C": "CD",  # CAD
    "6E": "EC",  # EUR
    "6J": "JY",  # JPY
    "6M": "ME",  # MXN
    "6N": "NZ",  # ZND
    "6S": "SF",  # CHF
    "EMD": "MI",  # E-Mini S&P 400
    "EH": "ET",  # Ethanol
    "FCE": "CA",  # CAC 40
    "FBTP": "BT",  # Euro-BTP
    "FBTP9": "B9",  # Euro-BTP
    "FDAX": "DA",  # DAX (Last)
    "FDAX9": "D9",  # DAX (Last)
    "FESX9": "E9",  # Euro STOXX 50 (Last)
    "FGBL": "BL",  # Euro-Bund
    "FGBL9": "G9",  # Euro-Bund (Last)
    "FGBM": "BM",  # Euro-Bobl
    "FGBM9": "M9",  # Euro-Bobl (Last)
    "FGBS": "BS",  # Euro-Schatz
    "FGBS9": "S9",  # Euro-Schatz
    "FGBX9": "X9",  # Euro-Buxl (Last)
    "FSMI": "SX",  # Swiss Market Index
    "FTDX": "FD",  # TecDAX
    "GF": "FC",  # Feeder Cattle
    "HE": "LH",  # Lean Hogs
    "LEU": "EU",  # Euribor (Official Close)
    "LEU9": "L9",  # Euribor (Official Close)
    "LFT9": "F9",  # FTSE 100 (OOfficial Close)
    "RB": "XB",  # RBOB Gasoline
    "RTY": "RM",  # E-mini Russell 2000
    "SCN4": "S4",  # FTSE China A50 (Day session)
    "SIN": "SN",  # SGX Nifty 50
    "SNK": "SK",  # Nikkei 225 (SGX)
    "SNK4": "K4",  # Nikkei 225 (SGX) (Day session)
    "SP1": "S1",  # S&P 500 (Floor)
    "SSG4": "S4",  # MSCI Singpaore (Day session)
    # "STW4": "T4",  # MSCI Taiwan (Day session) - contract retired - see HTW4
    "YAP4": "A4",  # SPI 200 (Day session)
    "YG": "XG",  # Mini-Gold
    "YI": "YS",  # Silver Mini
    "YIB": "IB",  # ASX 30 day Interbank Cash Rate
    "YIB4": "B4",  # ASX 30 day Interbank Cash Rate (Day)
    "YIR": "IR",  # ASX 90 Day Bank Accepted Bills
    "YIR": "R4",  # ASX 90 Day Bank Accepted Bills (Day)
    "YXT4": "X4",  # ASX 10 Year Treasury Bond (Day)
    "YYT4": "Y4",  # ASX 3 Year Treasury Bond (Day)
    "ZC": "CN",  # Corn
    "ZF": "FV",  # 5-year US T-Note
    "ZL": "BO",  # Soybean Oil
    "ZM": "SM",  # Soybean Meal
    "ZN": "TY",  # 10-Year US T-Note
    "ZO": "OA",  # Oats
    "ZQ": "FF",  # 30 Day Fed Funds
    "ZR": "RR",  # Rough Rice
    "ZS": "SY",  # Soybean
    "ZT": "TU",  # 2-year US T-Note
    "ZW": "WC",  # Chicago SRW Wheat
    "LSS": "SS",  # Short Sterling (LIFFE)
    "BTC": "BC",  # Bitcoin
    "LES": "SW",  # Euro Swiss
    "SXF": "TS",  # S&P/TSX 60
    "YAP10": "YN",  # S&P/ASX 200 (N) (L)
    "SSG": "SG",  # MSCI Singapore
    "SSG4": "SD",  # MSCI Singapore Day
    "EUA": "EA", # European Union emission Allowances
    "FOAT": "FO", # French govt bond (OAT)
    "FOAT4": "O4", # French govt bond (OAT) - day
    "FOAT9": "O9", # French govt bond (OAT) - Official Close
    "HTW": "TW",  # MSCI Taiwan 
    "HTW4": "T4",  # MSCI Taiwan (Day session)

}


def normalize_daily_start_end_session(calendar_name, start_session, end_session):
    if zl.__version__ < '2.2.0':
        cal = get_calendar(calendar_name)
    else:
        cal = get_calendar(calendar_name,start=start_session.strftime("%Y-%m-%d"))
    if not (cal.is_session(start_session)):
        # use next close instead of next open due to futures markets that start on Sundays
        # and we only want daily data
        start_session = cal.next_close(start_session).floor(freq="D")
    if not (cal.is_session(end_session)):
        end_session = cal.previous_close(end_session).floor(freq="D")
    return start_session, end_session

def define_non_US_country_code(exchanges):
    aulist = ('ASX','AU IDX')
    for exchange in aulist:
        #if exchanges.index.contains(exchange):
        if exchange in exchanges.index:
            exchanges.at[exchange,'country_code'] = 'AU'
    calist = ('TSX','TSX Venture','TSX Venture NEX','CSE','NEO','CA IDX')
    for exchange in calist:
        if exchange in exchanges.index:
            exchanges.at[exchange,'country_code'] = 'CA'

def create_norgatedata_equities_bundle(
    bundlename,
    stock_price_adjustment_setting,
    start_session,
    end_session,
    symbol_list=None,
    watchlists=None,
    excluded_symbol_list=None,
):
    def ingest(
        environ,
        asset_db_writer,
        minute_bar_writer,
        daily_bar_writer,
        adjustment_writer,
        calendar,
        start_session,
        end_session,
        cache,
        show_progress,
        output_dir,
    ):
        logger.info(
            "Ingesting equities bundle "
            + bundlename
            + " with start date "
            + start_session.strftime("%Y-%m-%d")
        )
        symbols = determine_symbols(
            start_session, end_session, symbol_list, watchlists, excluded_symbol_list
        )
        dtype = [
            ("start_date", "datetime64[ns]"),
            ("end_date", "datetime64[ns]"),
            ("auto_close_date", "datetime64[ns]"),
            ("symbol", "object"),
            ("asset_name", "object"),
            ("exchange", "object"),
            ("exchange_full", "object"),
            ("asset_type", "object"),
            ("norgate_data_symbol", "object"),
            ("norgate_data_assetid", "int64"),
            ("first_traded", "datetime64[ns]"),
        ]
        metadata = pd.DataFrame(empty(len(symbols), dtype=dtype))
        sessions = calendar.sessions_in_range(start_session, end_session)
        daily_bar_writer.write(
            _pricing_iter_equities(
                symbols,
                metadata,
                sessions,
                show_progress,
                stock_price_adjustment_setting,
                start_session,
                end_session,
            ),
            show_progress=show_progress,
        )
        exchangenames = pd.unique(metadata["exchange"])
        exchanges = pd.DataFrame(
            data={"country_code": "US", "canonical_name": exchangenames},
            index=exchangenames,
        )
        exchanges.index.name = "exchange"
        define_non_US_country_code(exchanges)
        asset_db_writer.write(equities=metadata, exchanges=exchanges)
        # Write empty splits and divs - they are already incorporated in Norgate Data
        divs_splits = {
            "divs": pd.DataFrame(
                columns=[
                    "sid",
                    "amount",
                    "ex_date",
                    "record_date",
                    "declared_date",
                    "pay_date",
                ]
            ),
            "splits": pd.DataFrame(columns=["sid", "ratio", "effective_date"]),
        }
        adjustment_writer.write(
            splits=divs_splits["splits"], dividends=divs_splits["divs"]
        )
        logger.info(
            "Ingestion of equities bundle "
            + bundlename
            + " completed"
            + " with "
            + str(len(symbols))
            + " securities"
        )

    return ingest


def Repeat(x):
    _size = len(x)
    repeated = []
    for i in range(_size):
        k = i + 1
        for j in range(k, _size):
            if x[i] == x[j] and x[i] not in repeated:
                repeated.append(x[i])
    return repeated


def create_norgatedata_futures_bundle(
    bundlename,
    start_session,
    end_session,
    symbol_list=None,
    watchlists=None,
    session_symbols=None,
    excluded_symbol_list=None,
    calendar=None,
):
    def ingest(
        environ,
        asset_db_writer,
        minute_bar_writer,
        daily_bar_writer,
        adjustment_writer,
        calendar,
        start_session,
        end_session,
        cache,
        show_progress,
        output_dir,
    ):
        logger.info(
            "Ingesting futures bundle "
            + bundlename
            + " with start date "
            + start_session.strftime("%Y-%m-%d")
        )
        symbols, root_symbols = determine_futures_symbols(
            start_session,
            end_session,
            symbol_list=symbol_list,
            session_symbols=session_symbols,
            watchlists=watchlists,
            excluded_symbol_list=excluded_symbol_list,
        )
        dtype = [
            ("start_date", "datetime64[ns]"),
            ("end_date", "datetime64[ns]"),
            ("auto_close_date", "datetime64[ns]"),
            ("symbol", "object"),
            ("root_symbol", "object"),
            ("asset_name", "object"),
            ("exchange", "object"),
            ("exchange_full", "object"),
            ("tick_size", "float64"),
            ("notice_date", "datetime64[ns]"),
            ("expiration_date", "datetime64[ns]"),
            ("multiplier", "float64"),
            ("asset_type", "object"),
            ("norgate_data_symbol", "object"),
            ("norgate_data_assetid", "int64"),
            ("first_traded", "datetime64[ns]"),
        ]
        metadata = pd.DataFrame(empty(len(symbols), dtype=dtype))
        sessions = calendar.sessions_in_range(start_session, end_session)
        daily_bar_writer.write(
            _pricing_iter_futures(
                symbols, metadata, sessions, show_progress, start_session, end_session
            ),
            show_progress=show_progress,
        )
        exchangenames = pd.unique(metadata["exchange"])
        exchanges = pd.DataFrame(
            data={"country_code": "US", "canonical_name": exchangenames},
            index=exchangenames,
        )
        exchanges.index.name = "exchange"
        #pd.set_option('display.max_rows', None)
        #pd.set_option('display.max_columns', None)
        #pd.set_option('display.width', None)
        #pd.set_option('display.max_colwidth', -1)
        # Check metadata for duplicate symbols
        symbollist_check  = [i for i in list(metadata["symbol"]) if i] # obtain non-None symbols...
        dupes = set([x for x in symbollist_check if symbollist_check.count(x) > 1])
        if len(dupes) > 0:
            logger.error("There are duplicate symbols in the metadata - this is probably due to a duplicated futures root symbol and will cause Zipline to abort.")
            logger.error("Duplicate symbols are  : " + str(dupes))
            raise Exception('Duplicate symbols in ingest')
        #metadata.asset_type = "futures"  # test to see if this fixes things
        futures_metadata = metadata[metadata.asset_type == "futures"].copy()
        exchangenames = pd.unique(futures_metadata["exchange"])
        futures_exchanges = pd.DataFrame(
            data={"country_code": "US", "canonical_name": exchangenames},
            index=exchangenames,
        )
        futures_exchanges.index.name = "exchange"

        equities_metadata = metadata[metadata.asset_type == "equities"].copy()
        exchangenames = pd.unique(equities_metadata["exchange"])
        equities_exchanges = pd.DataFrame(
            data={"country_code": "US", "canonical_name": exchangenames},
            index=exchangenames,
        )
        equities_exchanges.index.name = "exchange"

        asset_db_writer.write(
            futures=futures_metadata, root_symbols=root_symbols, exchanges=futures_exchanges
        )
        asset_db_writer.write(equities=equities_metadata, exchanges=equities_exchanges)

        # Write empty splits and divs - they are already n/a for futures
        divs_splits = {
            "divs": pd.DataFrame(
                columns=[
                    "sid",
                    "amount",
                    "ex_date",
                    "record_date",
                    "declared_date",
                    "pay_date",
                ]
            ),
            "splits": pd.DataFrame(columns=["sid", "ratio", "effective_date"]),
        }
        adjustment_writer.write(
            splits=divs_splits["splits"], dividends=divs_splits["divs"]
        )
        logger.info(
            "Ingesting of futures bundle "
            + bundlename
            + " completed"
            + " with "
            + str(len(symbols))
            + " securities"
        )

    return ingest

def create_norgatedata_futures_bundle_130(
    bundlename,
    start_session,
    end_session,
    symbol_list=None,
    watchlists=None,
    session_symbols=None,
    excluded_symbol_list=None,
):
    def ingest(
        environ,
        asset_db_writer,
        minute_bar_writer,
        daily_bar_writer,
        adjustment_writer,
        calendar,
        start_session,
        end_session,
        cache,
        show_progress,
        output_dir,
    ):
        logger.info(
            "Ingesting futures bundle "
            + bundlename
            + " with start date "
            + start_session.strftime("%Y-%m-%d")
        )
        symbols, root_symbols = determine_futures_symbols(
            start_session,
            symbol_list=symbol_list,
            session_symbols=session_symbols,
            watchlists=watchlists,
            excluded_symbol_list=excluded_symbol_list,
        )
        dtype = [
            ("start_date", "datetime64[ns]"),
            ("end_date", "datetime64[ns]"),
            ("auto_close_date", "datetime64[ns]"),
            ("symbol", "object"),
            ("root_symbol", "object"),
            ("asset_name", "object"),
            ("exchange", "object"),
            ("exchange_full", "object"),
            ("tick_size", "float64"),
            ("notice_date", "datetime64[ns]"),
            ("expiration_date", "datetime64[ns]"),
            ("multiplier", "float64"),
            ("asset_type", "object"),
            ("norgate_data_symbol", "object"),
            ("norgate_data_assetid", "int64"),
            ("first_traded", "datetime64[ns]"),
        ]
        metadata = pd.DataFrame(empty(len(symbols), dtype=dtype))
        sessions = calendar.sessions_in_range(start_session, end_session)
        daily_bar_writer.write(
            _pricing_iter_futures(
                symbols, metadata, sessions, show_progress, start_session, end_session
            ),
            show_progress=show_progress,
        )
        exchangenames = pd.unique(metadata["exchange"])
        exchanges = pd.DataFrame(
            data={"country_code": "US", "canonical_name": exchangenames},
            index=exchangenames,
        )
        exchanges.index.name = "exchange"
        # Check metadata for duplicate symbols
        if len(metadata) != len(set(metadata["symbol"])):
            separator = ","
            logger.error(
                "There are duplicate symbols in the metadata - this is probably due to a duplicated futures root symbol and will cause Zipline to abort.  Duplicate symbols are  : "
                + separator.join(Repeat(metadata["symbol"]))
            )
        metadata.asset_type = "futures"  # test to see if this fixes things
        futures_metadata = metadata[metadata.asset_type == "futures"].copy()
        exchangenames = pd.unique(futures_metadata["exchange"])
        futures_exchanges = pd.DataFrame(
            data={"country_code": "US", "canonical_name": exchangenames},
            index=exchangenames,
        )
        futures_exchanges.index.name = "exchange"

        equities_metadata = metadata[metadata.asset_type == "equities"].copy()
        exchangenames = pd.unique(equities_metadata["exchange"])
        equities_exchanges = pd.DataFrame(
            data={"country_code": "US", "canonical_name": exchangenames},
            index=exchangenames,
        )
        equities_exchanges.index.name = "exchange"

        asset_db_writer.write(
            futures=metadata, root_symbols=root_symbols, exchanges=exchanges
        )
        # `asset_db_writer.write(equities=equities_metadata, exchanges=equities_exchanges)
        # Write empty splits and divs - they are already n/a for futures
        divs_splits = {
            "divs": pd.DataFrame(
                columns=[
                    "sid",
                    "amount",
                    "ex_date",
                    "record_date",
                    "declared_date",
                    "pay_date",
                ]
            ),
            "splits": pd.DataFrame(columns=["sid", "ratio", "effective_date"]),
        }
        adjustment_writer.write(
            splits=divs_splits["splits"], dividends=divs_splits["divs"]
        )
        logger.info(
            "Ingesting of futures bundle "
            + bundlename
            + " completed"
            + " with "
            + str(len(symbols))
            + " securities"
        )

    return ingest

def determine_symbols(
    startdate, enddate, symbol_list=None, watchlists=None, excluded_symbol_list=None
):
    if watchlists is None and symbol_list is None:
        logger.error("No watchlists or symbol specified")
    symbols = []
    if symbol_list is not None:
        for symbol in symbol_list:
            if norgatedata.assetid(symbol) > 0:
                symbols.append(symbol)
    if watchlists is not None:
        for watchlistname in watchlists:
            watchlistsymbols = norgatedata.watchlist_symbols(watchlistname)
            logger.info(
                "Found " + str(len(watchlistsymbols)) + " symbols in " + watchlistname
            )
            symbols.extend(watchlistsymbols)
    symbols = list(set(symbols))  # Remove dupes
    symbols.sort()
    logger.info("Obtaining metadata for " + str(len(symbols)) + " securities...")
    if (1 == 0):
        for symbol in reversed(
            symbols
        ):  # Do in reversed order, because we will be deleting some symbols and this
            # messes up iteration
            if excluded_symbol_list is not None and symbol in excluded_symbol_list:
                symbols.remove(symbol)
                continue
            fqd = norgatedata.first_quoted_date(symbol)
            if fqd is None or fqd == "9999-12-31":
                symbols.remove(symbol)
                continue
            fqd = pd.Timestamp(fqd, tz="utc")
            if fqd > enddate:
                symbols.remove(symbol)
                continue
            lqd = norgatedata.last_quoted_date(symbol)
            if not (lqd is None or lqd == "9999-12-31"):
                lqd = pd.Timestamp(lqd, tz="utc")
                if lqd < startdate:
                    symbols.remove(symbol)
    
    revisedsymbols = []
    for symbol in symbols:  
        # messes up iteration
        if excluded_symbol_list is not None and symbol in excluded_symbol_list:
            continue
        fqd = norgatedata.first_quoted_date(symbol)
        if fqd is None or fqd == "9999-12-31":
            continue
        fqd = pd.Timestamp(fqd, tz="utc")
        if fqd > enddate:
            continue
        lqd = norgatedata.last_quoted_date(symbol)
        if not (lqd is None or lqd == "9999-12-31"):
            lqd = pd.Timestamp(lqd, tz="utc")
            if lqd < startdate:
                continue
        revisedsymbols.append(symbol)
    revisedsymbols.sort()
    logger.info(
        "Metadata process complete.  Revised security count: " + str(len(revisedsymbols))
    )
    return revisedsymbols

def determine_futures_symbols(
    startdate,
    enddate,
    symbol_list=None,
    watchlists=None,
    session_symbols=None,
    excluded_symbol_list=None,
):
    if symbol_list is None and watchlists is None and session_symbols is None:
        logger.error("No symbols, watchlists or session symbols specified")
        raise ValueError
    symbols = []
    root_symbols = set([])
    exchanges = dict()
    marketnames = dict()
    sectors = dict()
    if symbol_list is not None:
        for symbol in symbol_list:
            if norgatedata.assetid(symbol) > 0:
                symbols.append(symbol)
    if watchlists is not None:
        for watchlistname in watchlists:
            watchlistsymbols = norgatedata.watchlist_symbols(watchlistname)
            logger.info(
                "Found " + str(len(watchlistsymbols)) + " symbols in " + watchlistname
            )
            symbols.extend(watchlistsymbols)
    if session_symbols is not None:
        for session_symbol in session_symbols:
            contractsymbols = norgatedata.futures_market_session_contracts(
                session_symbol
            )
            logger.info(
                "Found "
                + str(len(contractsymbols))
                + " futures contracts in "
                + session_symbol
                + ": "
                + norgatedata.futures_market_session_name(session_symbol)
            )
            symbols.extend(contractsymbols)
    symbols.sort()
    if len(symbols) != len(set(symbols)):
        logger.info("Duplicate symbols found... removing dupes ")
        symbols = list(set(symbols))  # Remove dupes
    logger.info("Obtaining metadata for " + str(len(symbols)) + " securities...")
    revisedsymbols = []
    for symbol in symbols:
        if excluded_symbol_list is not None and symbol in excluded_symbol_list:
            continue
        fqd = norgatedata.first_quoted_date(symbol)
        if fqd is None or fqd == "9999-12-31":
            continue
        fqd = pd.Timestamp(fqd, tz="utc")
        if fqd > enddate:
            continue
        lqd = norgatedata.last_quoted_date(symbol)
        if lqd is not None:
            lqdtimestamp = pd.Timestamp(lqd, tz="utc")
            if lqdtimestamp < startdate:
                continue
        if norgatedata.base_type(symbol) == "Futures Market":
            if (lqd is None or lqd == "9999-12-31") and not symbol.startswith('&'):
                logger.info("Newly listed futures contract " + symbol + " ignored due to incomplete metadata")
                continue
            session_symbol = norgatedata.futures_market_session_symbol(symbol)
            root_symbol = translate_futures_symbol(session_symbol)
            if len(root_symbol) > 0 and not root_symbol in root_symbols:
                root_symbols.add(root_symbol)
                exchange = norgatedata.exchange_name(symbol)
                exchanges[root_symbol] = exchange
                marketname = norgatedata.futures_market_session_name(symbol)
                marketnames[root_symbol] = marketname
                sector = norgatedata.classification(
                    symbol, "NorgateDataFuturesClassification", "Name"
                )
                sectors[root_symbol] = sector
                if session_symbol == root_symbol:
                    logger.info(
                        "Zipline Futures Root added: "
                        + root_symbol
                        + " ("
                        + marketname
                        + ")"
                    )
                else:
                    logger.info(
                        "Zipline Futures Root added: "
                        + root_symbol
                        + " ("
                        + marketname
                        + ") (translated from Norgate session symbol "
                        + session_symbol
                        + ")"
                    )
        revisedsymbols.append(symbol)

    revisedsymbols.sort()
    root_symbols = list(root_symbols)
    root_symbols = pd.DataFrame(root_symbols, columns=["root_symbol"])
    root_symbols["root_symbol_id"] = root_symbols.index.values
    marketnames = pd.Series(marketnames)
    exchanges = pd.Series(exchanges)
    sectors = pd.Series(sectors)
    root_symbols["description"] = marketnames[root_symbols["root_symbol"]].tolist()
    root_symbols["exchange"] = exchanges[root_symbols["root_symbol"]].tolist()
    root_symbols["sector"] = sectors[root_symbols["root_symbol"]].tolist()
    logger.info(
        "Metadata process complete.  Revised security count: " + str(len(symbols))
    )
    return revisedsymbols, root_symbols

def _pricing_iter_equities(
    symbols,
    metadata,
    sessions,
    show_progress,
    stock_price_adjustment_setting,
    start_session,
    end_session,
):

    with maybe_show_progress(
        symbols, show_progress, label="Loading Norgate equities:", 
        item_show_func=lambda a:_progress_symbol(a),
    ) as it:
        for sid, symbol in enumerate(it):
            # 1990 is the maximum here - anything before is not defined as a
            # session apparently (!)
            # Padding must be all markte days, otherwise it will bork zipline's
            # expection that there's a bar for every day
            asset_name = norgatedata.security_name(symbol)
            exchange = norgatedata.exchange_name(symbol)
            exchange_full = norgatedata.exchange_name_full(symbol)
            df = norgatedata.price_timeseries(
                symbol,
                timeseriesformat="pandas-dataframe-zipline",
                start_date=start_session,
                end_date=end_session,
                stock_price_adjustment_setting=stock_price_adjustment_setting,
                padding_setting=norgatedata.PaddingType.ALLMARKETDAYS,  # Must do this - Zipline can only market day padded data
                fields=["Open", "High", "Low", "Close", "Volume"],
                datetimeformat="datetime64nsutc",
                timezone="UTC",
            )

            start_date = df.index[0]
            end_date = df.index[-1]

            # Add missing columns
            if not "volume" in df.columns:
                df["volume"] = 0
            # Zipline can't handle volumes above 4294967295, so for indices, we'll divide by 1000.
            # Many indices including S&P 500, Russell 3000 etc. have this level of volume
            if norgatedata.subtype1(symbol) == "Index" and "volume" in df.columns:
                df.loc[:, "volume"] /= 1000
            # Zipline can't handle crazy volumes for stocks where there have been lots of splits
            # Turn adjusted volume data into max UINT32 of 4294967295
            if "volume" in df.columns:
                df["volume"] = where(
                    df["volume"] > 4294967295, 4294967295, df["volume"]
                )
            slqd = norgatedata.second_last_quoted_date(
                symbol, datetimeformat="pandas-timestamp"
            )
            if slqd is None:
                ac_date = end_date + BDay(1) # Set bogus autoclose date after end date
            else:
                ac_date = slqd
            norgate_data_symbol = symbol
            norgate_data_assetid = norgatedata.assetid(symbol)
            asset_type = "equities"

            # Pad dates
            all_dates = sessions.snap("D")
            valid_dates = all_dates.slice_indexer(start=start_date, end=end_date)
            df = df.reindex(all_dates[valid_dates])  
            zerovalues = {"volume": 0}
            df.fillna(zerovalues, inplace=True)
            df["close"].fillna(method="ffill", inplace=True)  # forward fill close
            df = df.fillna(
                method="bfill", axis=1, limit=3
            )  # back fill close into OHL.  (For some reason, inplace=True doesn't work here with Pandas 0.18)
            metadata.iloc[sid] = (
                start_date,
                end_date,
                ac_date,
                symbol,
                asset_name,
                exchange,
                exchange_full,
                asset_type,
                norgate_data_symbol,
                norgate_data_assetid,
                start_date,
            )
            yield sid, df


################################################
def translate_futures_symbol(symbol):
    newsymbol = symbol
    if symbol[0] == "&":  # Continuous futures, strip leading &
        newsymbol = symbol[1:]
    if not symbol[0].isalnum():
        return newsymbol
    match = re.search("^([0-9A-Z]+)-(\d\d)(\d\d)([A-Z])", newsymbol)
    if match:
        newsymbol = match.group(1)
    if newsymbol in _symbol_translate:
        newsymbol = _symbol_translate[newsymbol]
    elif len(symbol) >= 3:
        newsymbol = newsymbol[0:2]
    if match:
        newsymbol += match.group(4) + match.group(3)
    return newsymbol

def _progress_symbol(a):
    if a is None: 
        return ""
    else:
        return a

def _pricing_iter_futures(
    symbols, metadata, sessions, show_progress, start_session, end_session
):
    with maybe_show_progress(
        symbols, show_progress, label="Loading Norgate futures:", item_show_func=lambda a:_progress_symbol(a),
    ) as it:
        for sid, symbol in enumerate(it):
            # 2000 is the maximum here - anything before is not defined as a
            # session apparently (!) - probably the calendars need work in
            # zipline
            # Padding must be all market days, otherwise it will bork zipline's
            # expection that there's a bar for every day
            # Open interest is here even though zipline can't yet use it
            df = norgatedata.price_timeseries(
                symbol,
                timeseriesformat="pandas-dataframe-zipline",
                start_date="1970-01-01",
                padding_setting=norgatedata.PaddingType.ALLMARKETDAYS,
                stock_price_adjustment_setting=norgatedata.StockPriceAdjustmentType.NONE,
                datetimeformat="datetime64nsutc",
                timezone="UTC",
            )
            # Add missing columns
            if not "volume" in df.columns:
                df["volume"] = 0
            if not "open interest" in df.columns:
                df["open interest"] = 0
            # Zipline can't handle volumes above 4294967295, so for indices, we'll divide by 1000.
            # Many indices including S&P 500, Russell 3000 etc. have this level of volume
            if norgatedata.subtype1(symbol) == "Index":
                df.loc[:, "volume"] /= 1000
            # Zipline can't handle crazy volumes for stocks where there have been lots of splits
            # Turn adjusted volume data into max UINT32 of 4294967295
            df["volume"] = where(df["volume"] > 4294967295, 4294967295, df["volume"])
            asset_name = norgatedata.security_name(symbol)
            exchange = norgatedata.exchange_name(symbol)
            exchange_full = norgatedata.exchange_name_full(symbol)
            norgate_data_symbol = symbol
            norgate_data_assetid = norgatedata.assetid(symbol)
            notice_date = norgatedata.first_notice_date(
                symbol, datetimeformat="pandas-timestamp"
            )

            expiration_date = norgatedata.last_quoted_date(
                symbol, datetimeformat="pandas-timestamp"
            )
            if norgatedata.base_type(symbol) == "Futures Market":
                tick_size = norgatedata.tick_size(symbol)
                multiplier = norgatedata.point_value(symbol)
                root_symbol = translate_futures_symbol(
                    norgatedata.futures_market_session_symbol(symbol)
                )
                symbol = translate_futures_symbol(symbol)
                asset_type = "futures"
            else:
                tick_size = 0.0001
                multiplier = 1
                root_symbol = symbol
                asset_type = "equities"
            if df is None or len(df.index) == 0:
                logger.info(
                    "Futures contract found with no price data: " + symbol + "(perhaps it has just been listed and the exchange has not yet sent down trading prices)... skipping"
                )
                continue
            start_date = None
            end_date = None
            ac_date = None

            if len(df.index) > 0:
                start_date = df.index[0]
                end_date = df.index[-1]

            if notice_date is not None:
                # ac_date = df.index[df.index.searchsorted(pd.Timestamp(notice_date)) - 1] # Day prior to FND.  This method was used prior to 20200713
                if df.index[-1] >= pd.Timestamp(notice_date):
                    if len(df.index) > 2:
                        ac_date = df.index[
                            df.index.searchsorted(pd.Timestamp(notice_date)) - 2
                        ]  # 2 days prior to FND
                    else:
                        ac_date = pd.Timestamp(notice_date) - BDay(2)
                else:
                    ac_date = pd.Timestamp(notice_date) - BDay(2)
            elif expiration_date is not None:
                # ac_date = pd.Timestamp(expiration_date, tz="utc") # This method was used prior to 20200713
                if df.index[-1] >= pd.Timestamp(expiration_date): # Last value is on or after expiration date
                    if len(df.index) > 2:
                        ac_date = df.index[
                            df.index.searchsorted(pd.Timestamp(expiration_date)) - 2
                        ]  # second last trading date, as determined by the data
                    else:
                        ac_date = pd.Timestamp(notice_date) - BDay(2) # Corner case - perhaps we are ingesting around a boundary of expiration
                else:
                    ac_date = pd.Timestamp(expiration_date) - BDay(2)

            if ac_date is None: # Every futures contract needs an autoclose date of some sort
                expiration_date = end_date + BDay(1) # Set a bogus date
                ac_date = pd.Timestamp(expiration_date) - BDay(2)

            if notice_date is None:
                notice_date = expiration_date + BDay(1)  # Put a notice date 1 day after expiration

            all_dates = sessions.snap("D")
            valid_dates = all_dates.slice_indexer(start=start_date, end=end_date)

            # Check if the first date from valid_dates exists in df - if not, we have to pad this ourselves so that the forward fill works in the future
            if (
                len(all_dates[valid_dates]) > 0
                and all_dates[valid_dates][0] not in df.index
            ):
                # Create a reindexed DF with one row that is forward filled
                single_date_slice = all_dates.slice_indexer(
                    start=all_dates[valid_dates][0], end=all_dates[valid_dates][0]
                )
                single_date_df = df.reindex(
                    all_dates[single_date_slice], method="ffill"
                )
                # Now set OHL to Close, vol to zero
                single_date_df["open"] = single_date_df["close"]
                single_date_df["high"] = single_date_df["close"]
                single_date_df["low"] = single_date_df["close"]
                single_date_df["volume"] = 0
                df = df.append(single_date_df).sort_index()
            df = df.reindex(all_dates[valid_dates])
            zerovalues = {"volume": 0}
            df.fillna(zerovalues, inplace=True)
            df["close"].fillna(method="ffill", inplace=True)
            df["open interest"].fillna(method="ffill", inplace=True)
            df = df.fillna(
                method="bfill", axis=1, limit=3
            )  # For some reason, inplace=True doesn't work here with Pandas 0.18

            if len(df.index) > 0:
                start_date = df.index[0]
            else:
                start_date = None
            metadata.iloc[sid] = (
                start_date,
                end_date,
                ac_date,
                symbol,
                root_symbol,
                asset_name,
                exchange,
                exchange_full,
                tick_size,
                notice_date,
                expiration_date,
                multiplier,
                asset_type,
                norgate_data_symbol,
                norgate_data_assetid,
                start_date,
            )
            yield sid, df


def register_norgatedata_equities_bundle(
    bundlename,
    stock_price_adjustment_setting=norgatedata.StockPriceAdjustmentType.TOTALRETURN,
    start_session="1990-01-01",
    end_session="now",
    calendar_name="NYSE",
    symbol_list=None,
    watchlists=None,
    excluded_symbol_list=None,
):
    if not isinstance(start_session, pd.Timestamp):
        start_session = norgatedata.norgatehelper.decode_date(
            start_session, datetimeformat="pandas-timestamp"
        )
    if not isinstance(end_session, pd.Timestamp):
        end_session = norgatedata.norgatehelper.decode_date(
            end_session, datetimeformat="pandas-timestamp"
        )
    start_session, end_session = normalize_daily_start_end_session(
        calendar_name, start_session, end_session
    )
    register(
        bundlename,
        create_norgatedata_equities_bundle(
            bundlename,
            stock_price_adjustment_setting,
            start_session,
            end_session,
            symbol_list=symbol_list,
            watchlists=watchlists,
            excluded_symbol_list=excluded_symbol_list,
        ),
        start_session=start_session,
        end_session=end_session,
        calendar_name=calendar_name,
    )


def register_norgatedata_futures_bundle(
    bundlename,
    start_session="1990-01-01",
    end_session="now",
    calendar_name="us_futures",
    symbol_list=None,
    session_symbols=None,
    watchlists=None,
    excluded_symbol_list=None,
):
    if not isinstance(start_session, pd.Timestamp):
        start_session = norgatedata.norgatehelper.decode_date(
            start_session, datetimeformat="pandas-timestamp"
        )
    if not isinstance(end_session, pd.Timestamp):
        end_session = norgatedata.norgatehelper.decode_date(
            end_session, datetimeformat="pandas-timestamp"
        )
    start_session, end_session = normalize_daily_start_end_session(
        calendar_name, start_session, end_session
    )
    register(
        bundlename,
        create_norgatedata_futures_bundle(
            bundlename,
            start_session,
            end_session,
            symbol_list=symbol_list,
            watchlists=watchlists,
            session_symbols=session_symbols,
            excluded_symbol_list=excluded_symbol_list,
        ),
        start_session=start_session,
        end_session=end_session,
        calendar_name=calendar_name,
    )


def zipline_futures_root_symbols_dict():
    zipline_markets = {}
    session_symbols = norgatedata.futures_market_session_symbols()
    for session_symbol in session_symbols:
        zipline_symbol = translate_futures_symbol(session_symbol)
        name = norgatedata.futures_market_session_name(session_symbol)
        if zipline_symbol in zipline_markets:
            logger.error(
                "Zipline already has a session symbol of "
                + zipline_symbol
                + ":"
                + zipline_markets[zipline_symbol]
                + ".  "
                + name
                + ", derived from norgate session symbol "
                + session_symbol
                + " is a duplicate "
            )
        zipline_markets[zipline_symbol] = name
    return zipline_markets

logger.info("Zipline v" + zl.__version__ + " detected")
logger.info("Zipline_norgatedata package v" + __version__ + ": Init complete")
