from zipline.pipeline.filters import Filter
from zipline.pipeline.factors import Factor
from zipline.api import sid
from zipline.utils.numpy_utils import bool_dtype, repeat_first_axis

from functools import partial
from pprint import pprint  # for debug only - remove for release
import numpy as np
import norgatedata
import pandas as pd
import logbook

from queue import Queue
from threading import Thread

try:
    from multiprocessing import Process
except ImportError:
    _has_multiprocessing = False
else:
    _has_multiprocessing = True
from time import time

logger = logbook.Logger("Norgate Data")


class NorgateDataIndexConstituent(Filter):
    """
    A Filter that computes True or False for whether a given asset was part of the index on a given day
    Parameters

    """

    window_length = 0
    inputs = []

    def __new__(cls, indexname):
        return super(NorgateDataIndexConstituent, cls).__new__(cls, indexname=indexname)

    def _init(self, indexname, *args, **kwargs):
        self._indexname = indexname
        return super(NorgateDataIndexConstituent, self)._init(*args, **kwargs)

    @classmethod
    def _static_identity(cls, indexname, *args, **kwargs):
        return (
            super(NorgateDataIndexConstituent, cls)._static_identity(*args, **kwargs),
            indexname,
        )

    def _compute(self, arrays, dates, assets, mask):
        logger.info(
            "Populating "
            + self.__class__.__name__
            + " pipeline populating with "
            + self._indexname
            + " on "
            + str(assets.size)
            + " securities from "
            + str(dates[0].strftime("%Y-%m-%d"))
            + " to "
            + str(dates[-1].strftime("%Y-%m-%d"))
            + "...."
        )
        norgatetimeseriesfunction = partial(
            norgatedata.index_constituent_timeseries, indexname=self._indexname
        )
        result = ConvertNorgateBoolTimeSeriesToFilter(
            assets, norgatetimeseriesfunction, dates, mask
        )
        logger.info(
            "Pipeline "
            + self.__class__.__name__
            + " with "
            + self._indexname
            + ": Done"
        )
        return result


class NorgateDataMajorExchangeListed(Filter):
    """
    A Filter that computes True or False for whether a given asset was listed on a major exchange (True) or OTC (false)
    """

    window_length = 0
    inputs = []

    def __new__(cls):
        return super(NorgateDataMajorExchangeListed, cls).__new__(cls)

    def _init(self, *args, **kwargs):
        return super(NorgateDataMajorExchangeListed, self)._init(*args, **kwargs)

    @classmethod
    def _static_identity(cls, *args, **kwargs):
        return super(NorgateDataMajorExchangeListed, cls)._static_identity(
            *args, **kwargs
        )

    def _compute(self, arrays, dates, assets, mask):
        logger.info(
            "Pipeline "
            + self.__class__.__name__
            + " populating on "
            + str(assets.size)
            + " securities"
        )
        norgatetimeseriesfunction = norgatedata.major_exchange_listed_timeseries
        result = ConvertNorgateBoolTimeSeriesToFilter(
            assets, norgatetimeseriesfunction, dates, mask
        )
        logger.info("Pipeline " + self.__class__.__name__ + ": Done")
        return result

    # def graph_repr(self):
    #    return "SingleAsset:\l  asset: {!r}\l".format(self._indexname)


class NorgateDataCapitalEvent(Filter):
    """
    A Filter that computes True or False for whether a given asset had a capital event (eg. split) that was entitled today (and will take effect tomorrow)
    Parameters

    """

    window_length = 1
    inputs = []
    window_safe = True
    dependencies = {}

    def __new__(cls):
        return super(NorgateDataCapitalEvent, cls).__new__(cls)

    def _init(self, *args, **kwargs):
        return super(NorgateDataCapitalEvent, self)._init(*args, **kwargs)

    @classmethod
    def _static_identity(cls, *args, **kwargs):
        return super(NorgateDataCapitalEvent, cls)._static_identity(*args, **kwargs)

    def _compute(self, arrays, dates, assets, mask):
        logger.info(
            "Pipeline "
            + self.__class__.__name__
            + " populating on "
            + str(assets.size)
            + " securities"
        )
        norgatetimeseriesfunction = norgatedata.capital_event_timeseries
        result = ConvertNorgateBoolTimeSeriesToFilter(
            assets, norgatetimeseriesfunction, dates, mask
        )
        logger.info("Pipeline " + self.__class__.__name__ + ": Done")
        return result

    # def graph_repr(self):
    #    return "SingleAsset:\l  asset: {!r}\l".format(self._indexname)


class NorgateDataPaddingStatus(Filter):
    """
    A Filter that computes True or False for whether a given asset was date padded on a given date
    Parameters

    """

    window_length = 1
    inputs = []
    window_safe = True
    dependencies = {}

    def __new__(cls):
        return super(NorgateDataPaddingStatus, cls).__new__(cls)

    def _init(self, *args, **kwargs):
        return super(NorgateDataPaddingStatus, self)._init(*args, **kwargs)

    @classmethod
    def _static_identity(cls, *args, **kwargs):
        return super(NorgateDataPaddingStatus, cls)._static_identity(*args, **kwargs)

    def _compute(self, arrays, dates, assets, mask):
        logger.info(
            "Pipeline "
            + self.__class__.__name__
            + " populating on "
            + str(assets.size)
            + " securities"
        )
        norgatetimeseriesfunction = norgatedata.padding_status_timeseries
        result = ConvertNorgateBoolTimeSeriesToFilter(
            assets, norgatetimeseriesfunction, dates, mask
        )
        logger.info("Pipeline " + self.__class__.__name__ + ": Done")
        return result

    # def graph_repr(self):
    #    return "SingleAsset:\l  asset: {!r}\l".format(self._indexname)


class NorgateDataUnadjustedClose(Factor):
    """
    A Filter that returns the unadjusted close of the security

    """

    window_length = 1
    dtype = np.float
    inputs = []
    window_safe = True

    def _compute(self, arrays, dates, assets, mask):
        logger.info(
            "Pipeline "
            + self.__class__.__name__
            + " populating on "
            + str(assets.size)
            + " securities"
        )
        norgatetimeseriesfunction = norgatedata.unadjusted_close_timeseries
        result = ConvertNorgateFloatTimeSeriesToFactor(
            assets, norgatetimeseriesfunction, dates, mask
        )
        logger.info("Pipeline " + self.__class__.__name__ + ": Done")
        return result


class NorgateDataDividendYield(Factor):
    """
    A Filter that computes the dividend yield of a stock based upon a 12 month rolling window, with some smarts to handle variations in dates
    """

    window_length = 1
    dtype = np.float
    inputs = []
    window_safe = True

    def _compute(self, arrays, dates, assets, mask):
        logger.info(
            "Pipeline "
            + self.__class__.__name__
            + " populating on "
            + str(assets.size)
            + " securities"
        )
        norgatetimeseriesfunction = norgatedata.dividend_yield_timeseries
        result = ConvertNorgateFloatTimeSeriesToFactor(
            assets, norgatetimeseriesfunction, dates, mask
        )
        logger.info("Pipeline " + self.__class__.__name__ + ": Done")
        return result


def PopulateFilterQueueWorker(q):
    while True:
        args = q.get()
        PopulateFilter(*args)
        q.task_done()


def PopulateFilter(
    symbol,
    norgatetimeseriesfunction,
    start_date,
    end_date,
    assetindexcounter,
    dates,
    out,
):
    timeseries = norgatetimeseriesfunction(
        symbol=symbol,
        padding_setting=norgatedata.PaddingType.ALLMARKETDAYS,
        timeseriesformat="pandas-dataframe",
        start_date=start_date,
        end_date=end_date,
        datetimeformat="datetime64nsutc",
        timezone="UTC",
    )
    timeseries = timeseries.reindex(dates, fill_value=0)
    out[:, assetindexcounter] = timeseries.iloc[:, 0] == 1


def ConvertNorgateBoolTimeSeriesToFilter(
    assets, norgatetimeseriesfunction, dates, mask
):
    start_date = dates[0]
    end_date = dates[-1]
    out = np.full_like(mask, False, order="K")  # Fill with false
    assetindexcounter = 0
    for zipline_assetid in assets:
        symbol = sid(zipline_assetid).symbol
        PopulateFilter(
            symbol,
            norgatetimeseriesfunction,
            start_date,
            end_date,
            assetindexcounter,
            dates,
            out,
        )
        assetindexcounter += 1
    # Testing of threading... only about 10% for unknown side effects
    # assetindexcounter = 0
    # out = np.full_like(mask,False,order='K') # Fill with false
    # q = Queue(maxsize=0)
    # num_threads = 8
    # Setup workers
    # for i in range(num_threads):
    #    worker = Thread(target=PopulateFilterQueueWorker, args=(q,))
    #    worker.setDaemon(True)
    #    worker.start()
    # for zipline_assetid in assets:
    #    symbol = sid(zipline_assetid).symbol
    #    q.put((symbol,norgatetimeseriesfunction,start_date,end_date,assetindexcounter,dates,out))
    #    assetindexcounter+=1
    # q.join()

    return out


def PopulateFactor(
    symbol,
    norgatetimeseriesfunction,
    start_date,
    end_date,
    assetindexcounter,
    dates,
    out,
):
    timeseries = norgatetimeseriesfunction(
        symbol=symbol,
        padding_setting=norgatedata.PaddingType.ALLMARKETDAYS,
        timeseriesformat="pandas-dataframe",
        start_date=start_date,
        end_date=end_date,
        datetimeformat="datetime64nsutc",
        timezone="UTC",
    )
    out[:, assetindexcounter] = timeseries.reindex(
        dates, fill_value=0, copy=False
    ).values[:, 0]


def ConvertNorgateFloatTimeSeriesToFactor(
    assets, norgatetimeseriesfunction, dates, mask
):
    start_date = dates[0].to_pydatetime()
    end_date = dates[-1].to_pydatetime()
    out = np.full_like(mask, np.nan, dtype=np.float, order="K")  # Fill with NaN
    assetindexcounter = 0
    for zipline_assetid in assets:
        symbol = sid(zipline_assetid).symbol
        PopulateFactor(
            symbol,
            norgatetimeseriesfunction,
            start_date,
            end_date,
            assetindexcounter,
            dates,
            out,
        )
        assetindexcounter += 1
    return out
