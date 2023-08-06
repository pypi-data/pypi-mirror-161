"""
Cache Yahoo Finance data using the Yahoo Finance API through Pandas DataReader.
"""
import pandas as pd
import pandas_datareader.data as web
import datetime
import dateparser
import pathlib
import logging


class CachedYahooDataReader:
    """
    Get Yahoo finance data speedily with a local cache.
    """

    def __init__(self, cache_dir="cache"):
        self.cache_dir = pathlib.Path(cache_dir)

    @staticmethod
    def get_yahoo_data(ticker, start_date, end_date):
        """
        Get Yahoo Finance data for a given ticker.
        """
        df = web.DataReader(ticker, "yahoo", start_date, end_date)
        # Cast to float
        df = df.astype(float)
        # The stock market is not open every day, so add rows with NaN for in-between days
        dates = [
            start_date + datetime.timedelta(n)
            for n in range((end_date - start_date).days + 1)
        ]
        df_filled = pd.DataFrame(index=dates, columns=df.columns)
        df_filled.update(df)
        return df_filled

    def get_cached_yahoo_data(self, ticker, start_date, end_date):
        """
        Get daily Yahoo Finance data for a given ticker and date range.
        Use cached data if available. If not, get data from Yahoo Finance and cache it.
        """
        # Convert start and end dates to datetime objects if they are strings.
        if isinstance(start_date, str):
            start_date = dateparser.parse(start_date)
        if isinstance(end_date, str):
            end_date = dateparser.parse(end_date)
        try:
            # Open cached data with datetime objects as the indices
            df = pd.read_csv(
                self.cache_dir / f"{ticker.replace('.', '-')}.csv", index_col=0, parse_dates=True
            )
            df.astype(float)
        except FileNotFoundError:
            # Get data from Yahoo Finance
            logging.info(
                "Cache miss for {}. Getting data from Yahoo Finance.".format(ticker)
            )
            df = self.get_yahoo_data(ticker.replace('.', '-'), start_date, end_date)
            # Create the cache directory if it doesn't exist
            pathlib.Path("cache").mkdir(parents=True, exist_ok=True)
            # Save data to cache
            df.to_csv(self.cache_dir / f"{ticker.replace('.', '-')}.csv")
        # Get the data for the given date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        # Check there is a row for each day in the date range and download any missing data
        if len(df) != (end_date - start_date).days + 1:
            logging.info(
                "Cache miss on some days for {}. Getting data from Yahoo Finance.".format(
                    ticker
                )
            )
            df_new = self.get_yahoo_data(ticker, start_date, end_date)
            # Remove any overlapping data
            df_new = df_new[~df_new.index.isin(df.index)]
            # Append to existing data
            df = pd.concat([df, df_new])
            # Sort date
            df = df.sort_index()
            # Cache it
            df.to_csv(self.cache_dir / f"{ticker.replace('.', '-')}.csv")
        # Remove NaN rows
        df = df.dropna(how="all")
        return df

    def DataReader(self, ticker, source="yahoo", start_date=None, end_date=None):
        """
        Get Yahoo Finance data for a given ticker.
        """
        assert start_date is not None, "start_date must be specified"
        if end_date is None:
            end_date = datetime.datetime.now()
        assert source == "yahoo", "Only Yahoo Finance data is supported."
        return self.get_cached_yahoo_data(ticker, start_date, end_date)
