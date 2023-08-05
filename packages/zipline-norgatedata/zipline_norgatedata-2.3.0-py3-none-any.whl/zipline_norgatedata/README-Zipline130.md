![alt text](https://norgatedata.com/assets/images/norgate-data-logo-400x188.svg "Norgate Data") ![alt text](https://media.quantopian.com/logos/open_source/zipline-logo-03_.png "Zipline")

Integrates financial market data provided by [Norgate Data](https://norgatedata.com/) with [Zipline](https://zipline.io/), a Pythonic algorithmic trading library for backtesting.

Key features of this extension
 * Simple bundle creation
 * Survivorship bias-free bundles
 * Incorporates time series data such as historical index membership and dividend yield into Zipline's Pipeline mechanism
 * No modifications to the Zipline code base (except to fix problems with installation and obsolete calls that crash Zipline)

# Installation

```sh
pip install zipline-norgatedata
```

# Upgrades

To receive upgrades/updates

```sh
pip install zipline-norgatedata --upgrade
```

# Requirements

* Zipline 1.3.0
* Python 3.5 only (this is a limitation of Zipline)
* Microsoft Windows
* An active [Norgate Data](https://norgatedata.com/) subscription
* Norgate Data Updater software installed and running
* Writable local user folder named .norgatedata (or defined in environment variable NORGATEDATA_ROOT) - defaults to C:\\Users\\Your username\\.norgatedata
* Python packages: Pandas, Numpy, Logbook

Note: The "Norgate Data Updater" application (NDU) is a Windows-only application. NDU must be running for this Python package to work.

# Assumptions
- Stocks are automatically set an auto_close_date of the last quoted date 
- Futures are automatically set an auto_close_date to the earlier of following: Last trading date (for cash settled futures, and physically delivered futures that only allow delivery after the last trading date), or 1 trading day prior to first notice date for futures that have a first notice date prior to the last trading date.

# Bundle Creation 

Navigate to your Zipline local settings folder.  This is typically located at **c:\\users\\<your username>\\.zipline**

Add the following lines at the top of your Zipline local settings file - extension.py:
**Note:  This is _NOT_ the extension.py file inside the Anaconda3\\envs\\<your environment>\\lib\\site-packages\\zipline**

```py
from norgatedata import StockPriceAdjustmentType
from zipline_norgatedata import (
    register_norgatedata_equities_bundle,
    register_norgatedata_futures_bundle )
```

Then create as many bundles definitions as you desire.  These bundles will use either a given symbol list, one or more watchlists from your Norgate Data Watchlist Library and (for futures markets) all contracts belonging to a given set of [futures market session symbols](https://norgatedata.com/data-content-tables.php#futures).

Here are some examples with varying parameters.  You should adapt these to your requirements.

register_norgatedata_equities_bundle has the following default parameters:
    stock_price_adjustment_setting = StockPriceAdjustmentType.TOTALRETURN,
    end_session = 'now',
	calendar_name = 'NYSE',

register_norgatedata_futures_bundle has the following default parameters:
    end_session = 'now',
    calendar_name = 'us_futures'

```py

# EQUITIES BUNDLES

# Single stock bundle - AAPL from 1990 though 2018
register_norgatedata_equities_bundle(
    bundlename = 'norgatedata-aapl',
    symbol_list = ['AAPL'], 
    start_session = '1990-01-01',
    end_session = '2018-12-31'
)

# FANG stocks (Facebook, Amazon, Netflix, Google) - 2012-05-18 until now
register_norgatedata_equities_bundle(
    bundlename = 'norgatedata-fang',
    symbol_list = ['FB','AMZN','NFLX','GOOGL'], 
    start_session = '2012-05-18',  # This is that FB first traded
)

# A small set of selected ETFs
register_norgatedata_equities_bundle(
    bundlename = 'norgatedata-selected-etfs',
    symbol_list = ['SPY','GLD','USO'],
    start_session = '2006-04-10', # This is the USO first trading date
)

# S&P 500 Bundle for backtesting including all current & past constituents back to 1990
# and the S&P 500 Total Return index (useful for benchmarking and/or index trend filtering)
# (around 1800 securities)
register_norgatedata_equities_bundle(
    bundlename = 'norgatedata-sp500',
    symbol_list = ['$SPXTR'],
    watchlists = ['S&P 500 Current & Past'],
    start_session = '1990-01-01',
)

# Russell 3000 bundle containing all ccurrent & past constituents back to 1990
# and the Russell 3000 Total Return Index (useful for benchmarking and/or index trend filtering)
# (about 11000 securities)

register_norgatedata_equities_bundle(
    bundlename = 'norgatedata-russell3000',
    watchlists = ['Russell 3000 Current & Past'],
    symbol_list = ['$RUATR'],
    start_session = '1990-01-01' ,
)

# FUTURES BUNDLES

# Example bundle for all of the individual contracts from three futures markets:
# E-mini S&P 500, E-mini Nasdaq 100, E-mini Russell 2000
register_norgatedata_futures_bundle(
    bundlename = 'norgatedata-selected-index-futures',
    session_symbols = ['ES','NQ','RTY'],
    start_session = '2000-01-01',
)

# Same as above, but also adds the S&P 500 Total Return index ($SPXTR) for reference
register_norgatedata_futures_bundle(
    bundlename = 'norgatedata-selected-index-futures-and-index',
    session_symbols = ['ES','NQ','RTY'],
    symbol_list = ['$SPXTR']
    start_session = '2000-01-01',
)

# Bundle of futures used in Andreas Clenow's Trading Evolved book
# (contains 6000+ individual futures contracts/deliveries)
bundlename = 'norgatedata-tradingevolved-futures'
session_symbols = [
	'6A', # AUD
	'6B', # GBP
	'6C', # CAD
	'6E', # EUR
	'DX', # USDX
	'6J', # JPY
	'6N', # NZD
	'6S', # CHF
	'LBS', # Lumber
	'ZC', # Corn
	'CT', # Cotton
	'GF', # Feeder Cattle
	'KC', # Coffee
	'LRC', # Robusta Coffee
	'LSU', # White Sugar
	'ZO', # Oats
	'ZS', # Soybeans
	'SB', # Sugar
	'ZM', # Soybean Meal
	'ZW', # Wheat
	'CL', # Crude Oil
	'GC', # Gold
	'HG', # Copper
	'HO', # NY Harbor ULSD 
	'GAS', # Gas Oil
	'NG', # Henry Hub Natural Gas
	'PA', # Palladium
	'PL', # Platinum
	'RB', # RBOB Gasoline
	'SI', # Silver
	'ES', # E-mini S&P 500
	'NKD', # Nikkei 225 Dollar
	'NQ', # E-mini Nasdaq-100
	'STW', # MSCI Taiwan 
	'VX', # Cboe Volatility Index
	'YM', # E-mini Dow
	'GE', # Eurodollar
	'ZF', # 5-Year US T-Note
	'ZT', # 2-Year US T-Note
	'ZN', # 10-Year US T-Note
	'ZB', # 30-Year US T-Bond        
]
start_session = '2000-01-01',

register_norgatedata_futures_bundle(bundlename,start_session,session_symbols = session_symbols )


```

To ingest a bundle:

```sh
zipline ingest -b <bundlename>
```


# Pipelines - accessing timeseries data

Timeseries data has been exposed into Zipline's Pipeline interface.   During a backtest, the Pipelines will be calculated against all securities in the bundle.

The following Filter (i.e. boolean) pipelines are available:
 - [NorgateDataIndexConstituent](https://norgatedata.com/data-content-tables.php#ushics)
 - [NorgateDataMajorExchangeListed](https://norgatedata.com/data-content-tables.php#usmajorexchangelisted)
 - [NorgateDataCapitalEvent](https://norgatedata.com/data-content-tables.php#capitalevent)
 - [NorgateDataPaddingStatus](https://norgatedata.com/data-content-tables.php#padding)

The following Factor (i.e. float) pipelines are available:
 - NorgateDataUnadjustedClose
 - [NorgateDataDividendYield](https://norgatedata.com/data-content-tables.php#dividendyield)

 To incorporate these into your trading model, you need to import the relevant packages/methods:
 
```py
from zipline.pipeline import Pipeline
from zipline_norgatedata.pipelines import (
    NorgateDataIndexConstituent, NorgateDataDividendYield )
from zipline.api import order_target_percent
```

It is recommended you put your pipeline construction in its own function:

 ```py
def make_pipeline():
    indexconstituent = NorgateDataIndexConstituent('S&P 1500')
    divyield = NorgateDataDividendYield()
    return Pipeline(
        columns={
             'NorgateDataIndexConstituent':indexconstituent,
             'NorgateDividendYield':divyield },
        screen = indexconstituent)
```

Incorporate this into your trading system by attaching it to your initialize method.  Note, for better efficiency, use chunks=9999 or however many bars you are likely to need.  
This will save unnecessary access to the Norgate Data database.

```py

 def initialize(context):
    attach_pipeline(make_pipeline(), 'norgatedata_pipeline', chunks=9999,eager=True)
    # ...
```

Now you can access the contents of the pipeline in before_trading_start and/or handle_data by using Zipline's pipline_output method.  You can exit positions not already in the 

```py
def before_trading_start(context, data):
    context.pipeline_data = pipeline_output('norgatedata_pipeline')
    # ... your code here ...
    # For example, you could 

def handle_data(context, data):
    context.pipeline_data = pipeline_output('norgatedata_pipeline')
    current_constituents = context.pipeline_data.index
    
    # ... your code here ...

    # Exit positions not in the index today
    for asset in context.portfolio.positions:   
        if asset not in current_constituents:
            order_target_percent(asset,0.0)

    # ... your code here ...
```

# Worked example backtesting S&P 500 Constituents back to 1990

This example comprises a backtest on the S&P 500, with a basic trend filter that is applied on the S&P 500 index ($SPX).  The total return version of the index is also ingested ($SPXTR) for comparison purposes.

Create a bundle definition in extensions.py as follows:

```py
from zipline_norgatedata import register_norgatedata_equities_bundle

register_norgatedata_equities_bundle(
    bundlename = 'norgatedata-sp500-backtest',
    symbol_list = ['$SPX','$SPXTR'],
    watchlists = ['S&P 500 Current & Past'],
    start_session = '1990-01-01',
)
```

Now, ingest that bundle into zipline:

```sh
zipline ingest -b norgatedata-sp500-backtest
```

Inside your trading system file, you'd incorporate the following code snippets:

```py
from zipline.pipeline import Pipeline
from zipline_norgatedata.pipelines import (
    NorgateDataIndexConstituent, 
    NorgateDataDividendYield)

...

def make_pipeline():
    indexconstituent = NorgateDataIndexConstituent('S&P 500')
    return Pipeline(
        columns={
             'NorgateDataIndexConstituent':indexconstituent,
        },
        screen = indexconstituent)

 def initialize(context):
    attach_pipeline(make_pipeline(), 'norgatedata_pipeline', chunks=9999,eager=True)
    # ... your code here ...

def before_trading_start(context, data):
    context.pipeline_data = pipeline_output('norgatedata_pipeline')
    # ... your code here ...

def handle_data(context, data):
    context.pipeline_data = pipeline_output('norgatedata_pipeline')
    current_constituents = context.pipeline_data.index
    
    # ... your code here ...

    # Exit positions not in the index today
    for asset in context.portfolio.positions:   
        if asset not in context.assets:
            order_target_percent(asset,0.0)

    # ...
```


# Worked example backtesting E-Mini S&P 500 futures

This example created a continuous contract of the E-Mini S&P 500 futures that trade on CME on volume.

Create a bundle definition in extensions.py as follows:

```py
from zipline_norgatedata import register_norgatedata_futures_bundle

bundlename = 'norgatedata-es-futures'
session_symbols = ['ES']
start_session = '2000-01-01'
register_norgatedata_futures_bundle(bundlename,start_session,session_symbols = session_symbols )

```

Now, ingest that bundle into zipline:

```sh
zipline ingest -b norgatedata-es-futures
```

Inside your trading system file, you'd incorporate the following code snippets:

```py
 def initialize(context):

    # Obtain market(s)s directly from the bundle
    af =  context.asset_finder
    markets = set([]) # a set eliminates dupes
    allcontracts = af.retrieve_futures_contracts(af.sids)
    for contract in allcontracts:
        markets.add(allcontracts[contract].root_symbol)
           
    markets = list(markets)
    markets.sort()
  
    # Make a list of all continuations
    context.universe = [
        continuous_future(market, offset=0, roll='volume', adjustment='mul')
            for market in markets
    ]
    # ... your code here ...

def handle_data(context, data):
    # Get continuation data
    hist = data.history(
        context.universe, 
        fields=['close','volume'], 
        frequency='1d', 
        bar_count=250,  # Adjust to whatever lookback period you need
    )

    # Now use hist in your calculations 

    # Make a dictionary of open positions, based on the root symbol
    open_pos = {
        pos.root_symbol: pos 
        for pos in context.portfolio.positions
    } 

    contracts_to_trade = 5
    
    for continuation in context.universe:
        # ...
        contract = data.current(continuation, 'contract')
        # ...
        

        # Add your condtions here to determine if there is an entry then...
        order_target(contract,  contracts_to_trade)

        # Add your conditions to determine if there is an exit of a position then...
        order_target(contract, -1 * contracts_to_trade)

    # Finally, if there are open positions check for rolls
    if len(open_pos) > 0:   
        roll_futures(context, data)           

```

# Metadata

The following fields are available in the metadata dataframe: start_date, end_date, ac_date, symbol, asset_name, exchange, exchange_full, asset_type, norgate_data_symbol, norgate_data_assetid.  

# Norgate Data Futures Market Session symbols

To obtain just the futures market sessions symbols, you can use the norgatedata package and adapt the following code:
```py
import norgatedata
for session_symbol in norgatedata.futures_market_session_symbols():
    print (session_symbol + " " + norgatedata.futures_market_session_name(session_symbol)) 
```
# Zipline Futures root symbols

To show the translated 2 character root symbols for each futures market session, and a description of each market you can run a tiny script (or adapt this):

```py
import zipline_norgatedata
root_symbols_dict = zipline_norgatedata.zipline_futures_root_symbols_dict()
print (root_symbols_dict)
```

# Zipline installation best practice

- Zipline can be difficult to install if you do it in the wrong order.  Here's how we did it:

  1.  Install the latest [Anaconda Distribution](https://www.anaconda.com/distribution/) 
  2.  If using Conda v4.7 from an older Anaconda distribution, upgrade it to v4.8.  If installing Anaconda after July 2020 you can skip this.
  3.  Start Ananconda and Create a fresh Python 3.5 environment (Click Environments, then click Create, give it a name such as zip35, select Python 3.5 and click Create)
  4.  Run a terminal in the new environment, and use conda to install zipline 
      ```
      conda install zipline -c Quantopian
      ```
      and any other packages you want such as jupyter,  matplotlib etc.  
      ```
      conda install jupyter matplotlib
      ```
      Note, if you want Pyfolio (you probably will at some point), you should install this using Pip, as there is a very old version on Anaconda:
      ```
      pip install pyfolio
      ```
  5.  Install norgatedata and  zipline-norgatedata using pip 
      ```
      pip install norgatedata zipline-norgatedata
      ```
  6.  Upgrade logbook
      The version of logbook (v0.12) installed as a dependency when you zipline has some incompatilities.  Upgrade it to a fresher (v0.15+) version.  You'll need to do this if you get an RLock error.
      ```
      pip install logbook --upgrade
      ```
  7.  Patch the zipline package (see ***Zipline 1.3.0 Benchmark Patch*** below) to resolve backtest failure) within your new environment
  8.  Start a command prompt/terminal in your zipline environment you created, and simply run ```zipline bundles``` to ensure that it work (this also creates the .zipline folder too)
  9.  If you are backtesting futures data and create your own continuous futures from within your backtesting, you'll need to patch Zipline.  (see ***Zipline 1.3.0 Patches to resolve KeyError on Continuous Futures backtesting***)
  10.  If you want to backtest data prior to 1990 (Stocks) or 2000 (Futures) see ***Backtesting prior to in-built Zipline/trading-calendar limits***


# Zipline Limitations/Quirks

- Zipline 1.3.0 is only compatible with Python 3.5.  Hopefully they'll update it one day....
- Zipline has not been not had an official release since v1.3.0 (July 2018).  For reasons unknown, even though many fixes and changes have been implemented to the source code, no release has been made.
- Zipline is hard-coded to handle equities data from 1990 onwards only
- Zipline is hard-coded handle futures data from 2000 onwards.
- Zipline has unnecessarily complicated futures contracts by restricting symbols to 2 characters.  This is not a conventional followed by exchanges.  We hope they see the light and allow variable futures root symbol lengths (up to 5 characters).  In the meantime, you can get a list of futures market sessions covered and translated to their 2 character limit with: zipline_futures_root_symbols()
- Zipline doesn't define all futures markets and doesn't provide any runtime extensibility in this area - you will need to add them to <your_environment>\lib\site-packages\zipline\finance\constants.py if they are not defined.  Be sure to backup this file as it will be overwritten any time you update zipline.
- Zipline assumes that there are bars for every day of trading.  If a security doesn't trade for a given day (e.g. it was halted/suspended, or simply nobody wanted to trade it), it will be padded with the previous close repeated in the OHLC fields, with volume set to zero.  Consider how this might affect your trading calculations.  
- Index volumes cannot be accurately ingested due to Zipline trying to convert large volumes to UINTs which are out-of-bounds for UINT32.  Index volumes will be divided by 1000.
- Any stock whose adjusted volume exceeds the upper bound of UINT32 will be set to the maximum UINT32 value (4294967295).  This only occurs for stocks with a lot of splis and/or very large special dsitributions.
- Some stocks have adjusted volume values that fall below the boundaries used by winsorize_uint32 (e.g. volume of 8.225255e-05).  You'll see a warning when those stocks are ingested "UserWarning: Ignoring 12911 values because they are out of bounds for uint32".   These are  There's not much we can do here.  For now, just ignore those warnings.
- Suprisingly, Zipline benchmarks do not work from securities ingested into your bundle.   Rather, the benchmark uses hardcoded logic that attempts to download the security SPY from an IEX API (which is now retired).  See the "Zipline 1.3.0 Benchmark patch" below to fix/bypass this issue.
- Ingestion times could be improved significantly with multiprocessing (this requires Zipline enhancements)

If you are brave you could try with the latest Zipline source code (make sure you install the release version first, to solve dependencies):
```
conda install -c quantopian/label/ci zipline
```
Note:  You'll need to re-ingest any previously ingested bundles, as the underlying database schema used in Zipline is different.



# Zipline 1.3.0 Benchmark Patch to resolve backtest failure 

Strangely, by default, Zipline attempts to obtain benchmark data for for the symbol SPY from IEX (even if you define another symbol as the benchmark).  The public IEX API was retired in June 2019 so this causes all backtests to fail.

This will show this lovely error JSONDecodeError message similar to the following:
```
[2019-09-02 00:38:53.586933] INFO: Loader: Downloading benchmark data for 'SPY' from 1989-12-29 00:00:00+00:00 to 2019-08-30 00:00:00+00:00
Traceback (most recent call last): 
  File "C:\Users\pyuser\Anaconda3\envs\zip35\Scripts\zipline-script.py", line 11, in <module>
    load_entry_point('zipline==1.3.0+383.g069e97b2', 'console_scripts', 'zipline')()
  File "C:\Users\pyuser\Anaconda3\envs\zip35\lib\site-packages\click\core.py", line 722, in __call__
    return self.main(*args, **kwargs)
...
  File "C:\Users\pyuser\Anaconda3\envs\zip35\lib\json\decoder.py", line 357, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

A workaround is to simply return a benchmark that shows no return.  To do this you'll need to edit your Zipline libraries as follows:

* Firstly, navigate to the exact path of your Python environment installation (from the error message above, the environment path is C:\Users\pyuser\Anaconda3\envs\zip35 )
* Then navigate to Lib\site-packages\zipline\data  (i.e. full path for an environment named zip35 would be "C:\Users\\<your username>\Anaconda3\envs\zip35\Lib\site-packages\zipline\data")
* Edit the file benchmarks.py and replace all of the contents with the following:

```py
import pandas as pd
from trading_calendars import get_calendar

# Modified to avoid downloading data from obsolete IEX interface
def get_benchmark_returns(symbol):
    cal = get_calendar('NYSE')
    first_date = pd.Timestamp('1896-01-01', tz='utc')
    last_date = pd.Timestamp.today(tz='utc')
    dates = cal.sessions_in_range(first_date, last_date)
    data = pd.DataFrame(0.0, index=dates, columns=['close'])
    data = data['close']
    return data.sort_index().iloc[1:]

```

* Edit the file loader.py
* search for the method ensure_benchmark_data, and comment out the following four lines as shown (around line 200):

```py
    #data = _load_cached_data(filename, first_date, last_date, now, 'benchmark',
    #                         environ)
    #if data is not None:
    #    return data
```

Thanks to Andreas Clenow for this workaround, found here: https://github.com/quantopian/zipline/issues/2480

# Zipline 1.3.0 Patch to resolve KeyError on Continuous Futures backtesting

This bug shows as the following crypic error messgae:
```
KeyError: <class 'zipline.assets.continuous_futures.ContinuousFutures'>
```

Part 1:  Bug fix for DataPortal

If you want to create continuous futures, you'll need to fix Zipline for a bug in the DataPortal code.  Effectively what has been left out of the Zipline source code is the ability to read futures data.  We could either fake our futures data to look like Equities data, or do this simple patch.

You'll need to edit your Zipline package library as follows:

* Firstly, navigate to the exact path of your Python environment installation (from the error message above, the environment path is C:\Users\pyuser\Anaconda3\envs\zip35 )
* Then navigate to Lib\site-packages\zipline\utils  (i.e. full path for an environment named zip35 would be "C:\Users\<your username>\Anaconda3\envs\zip35\Lib\site-packages\zipline\utils")
* Edit the file run_algo.py and find the following lines (around line 141):

```py
        data = DataPortal(
            env.asset_finder,
            trading_calendar=trading_calendar,
            first_trading_day=first_trading_day,
            equity_minute_reader=bundle_data.equity_minute_bar_reader,
            equity_daily_reader=bundle_data.equity_daily_bar_reader,
            adjustment_reader=bundle_data.adjustment_reader,
```

Add the following two lines to the end of this argument list:
```py
            future_minute_reader=bundle_data.equity_minute_bar_reader,
            future_daily_reader=bundle_data.equity_daily_bar_reader,
```

The entire section of code should now read as follows:
```py
        data = DataPortal(
            env.asset_finder,
            trading_calendar=trading_calendar,
            first_trading_day=first_trading_day,
            equity_minute_reader=bundle_data.equity_minute_bar_reader,
            equity_daily_reader=bundle_data.equity_daily_bar_reader,
            adjustment_reader=bundle_data.adjustment_reader,
            future_minute_reader=bundle_data.equity_minute_bar_reader,
            future_daily_reader=bundle_data.equity_daily_bar_reader,
            )
```

Part 2:  Workaround for markets without defined volatility

By default, Zipline has defined constants for volatility that are used for slippage modelling.  If you attempt to test on a market that is not defined in the constants.py file, you will get a KeyError like this:

This bug shows as the following crypic error messgae:
```
KeyError: 'KC'
```

This patch will give any market without an explicitly defined volatility a default volatility.

* Edit finance/slippage.py
* At around line 27, find the following:

```py
from zipline.finance.constants import ROOT_SYMBOL_TO_ETA
```

Change this to:

```py
from zipline.finance.constants import ROOT_SYMBOL_TO_ETA, DEFAULT_ETA
```

* At around line 510, within get_simulated_impact, find:

```py
        eta = self._eta[order.asset.root_symbol]
```

change this to:

```py
        try:
            eta = self._eta[order.asset.root_symbol]
        except:
            eta = DEFAULT_ETA
```

# Jupyter reports no module named win32api

Install/reinstall pywin32

```
conda install pywin32
```


# Backtesting prior to in-built Zipline/trading-calendar limits

Zipline will only backtest according to the calendar within the trading_calendars package.  With some easy patches you can extend backtesting for US stocks from 1990 to 1970 and Futures from 2000 to 1970.

1970 is the limit though.  It is not possible to extend prior to this  Most likely there's an underlying limitation to the Unix Epoch (1970-01-01 00:00:00).

Firstly, we need extend internal benchmarking code to handle dates prior to 1980:
* Navigate to the exact path of your Python environment installation (from the error message above, the environment path is C:\Users\pyuser\Anaconda3\envs\zip35 )
* Then navigate to Lib\site-packages\zipline\data  (i.e. full path for an environment named zip35 would be "C:\Users\<your username>\Anaconda3\envs\zip35\Lib\site-packages\zipline\data")
* Edit the file treasuries.py and find the following lines (around line 58):
```py
    return pd.Timestamp('1980', tz='UTC')
```

change this to:
```py
    return pd.Timestamp('1970', tz='UTC')
```

To extend backtestng prior to 1970 for US stocks:
* Navigate to the exact path of your Python environment installation (from the error message above, the environment path is C:\Users\pyuser\Anaconda3\envs\zip35 )
* Then navigate to Lib\site-packages\trading_calendars  (i.e. full path for an environnment named zip35 would be "C:\Users\<your username>\Anaconda3\envs\zip35\Lib\site-packages\trading_calendars")
* Edit the file trading_calendar.py and find the following lines (around line 45):
```py
start_default = pd.Timestamp('1990-01-01', tz=UTC)
```

change this to:
```py
start_default = pd.Timestamp('1970-01-01', tz=UTC)
```

To extend backtestng prior to 2000 for futures:
* Firstly, navigate to the exact path of your Python environment installation (from the error message above, the environment path is C:\Users\pyuser\Anaconda3\envs\zip35 )
* Then navigate to Lib\site-packages\trading_calendars  (i.e. full path for an environment named zip35 would be "C:\Users\<your username>\Anaconda3\envs\zip35\Lib\site-packages\trading_calendars")
* Edit the file us_futures_calendar.py and find the following lines (around line 49):
```py
                 start=Timestamp('2000-01-01', tz=UTC),
```

change this to:
```py
                 start=Timestamp('1970-01-01', tz=UTC),
```

Note:  This section is a work-in-progress.  There are additional trading holidays that need to be included.  Norgate Data will be submitting a pull request for such changes to the trading_calendar package.  In the meantime, if you want accurate holidays for NYSE (US Stocks), or ASX (Australian Stocks) contact Norgate data.  We'd be happy to email the trading calendar files.

# Testing on ASX data

By default, run_algorithm uses the 'NYSE' trading calendar.  To backtest other markets, you need to specify the calendar.

At the top of your algorithm:
```py
from trading_calendars import get_calendar
```

In the run_algorithm call, add a trading_calendar= line, for example:

```py
results = run_algorithm(
    start=start, end=end, 
    initialize=initialize, analyze=analyze, 
    handle_data=handle_data, 
    capital_base=10000, 
    trading_calendar=get_calendar('XASX'),
    data_frequency = 'daily', 
    bundle='norgatedata-spasx200',
)
```

ASX users will need an updated ASX trading calendar too.

This can be upgraded by conda.

```
conda upgrade trading-calendars -c Quantopian
```

# Books/publications that use Zipline, adapted for Norgate Data use

We have adapted the Python code in the following books to use Norgate Data.  

* [Trading Evoled:  Anyone can Build Killer Trading Strategies in Python](https://www.followingthetrend.com/trading-evolved/).  Source code in Jupyter notebook format here: http://norgatedata.com/book-examples/trading-evolved/NorgateDataTradingEvolvedExamples.zip

If there are other book/publications that use Zipline and worth adding here, let us know.

# FAQs

### During a backtest I receive an error ValueError: 'Time Period' is not in list.  How do I fix this?

This can occur when the items in the bundle do not match the latest data in the Norgate Data database.  For stocks, if there are symbol changes within the database then the bundle will have the old symbol but the Norgate database will have the new symbol.    For Futures, there may have been additional futures contracts listed since your previous ingestion and the roll-over algorithm is trying to roll into them.  The solution is simple:  Ingest the bundle with the fresh data.

# Support

For support on Norgate Data or usage of the zipline-norgatedata extension:
[Norgate Data support](https://norgatedata.com/contact.php)

Please put separate issues in separate emails, as this ensures each issue is separately ticketed and tracked.

For Zipline coding/usage issues, join the [Zipline Google Group](https://groups.google.com/forum/#!forum/zipline).  For bug reports on Zipline, report them on [Zipline Github](https://github.com/quantopian/zipline/issues)

# Thanks

Thanks to:

* [Andreas Clenow](https://www.followingthetrend.com) for his pioneering work in documenting Zipline bundles in his latest book [Trading Evolved: Anyone can Build Killer Trading Strategies in Python](https://www.followingthetrend.com/trading-evolved/).  We used many of the techniques described in the book to build our bundle code.
* Norgate Data alpha and beta testers.  Without your persistence we wouldn't have implemented half of the features.
* The team at Quantopian for developing and open sourcing Zipline

