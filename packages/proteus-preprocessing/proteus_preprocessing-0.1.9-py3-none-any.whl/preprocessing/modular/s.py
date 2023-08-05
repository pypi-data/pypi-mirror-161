import datetime

import ecl2df.summary as summary
import ecl2df.wcon as wcon
from ecl2df.compdat import deck2dfs
from ecl2df import EclFiles

from ecl2df.common import (
    parse_opmio_deckrecord,
    parse_opmio_date_rec,
    parse_opmio_tstep_rec,
)

from ecl.summary import EclSum
from ecl2df.summary import df2eclsum

import pandas as pd

from preprocessing.utils import expand_dates, expand_wcon


WCONKEYS = ["WCONHIST", "WCONINJE", "WCONINJH", "WCONPROD"]


class WellSummaryProcessor:
    def __init__(self, summary_path):

        # Read Ecl files
        summary_ecl = EclSum(summary_path, include_restart=False)
        data_ecl = EclFiles(summary_path)

        # Create Ecl dataframes
        wcon_df = self.read_keywords(data_ecl)
        summary_columns = [
            "WOPR:*",
            "WWPR:*",
            "WGPR:*",
            "WBHP:*",
            "WOPT:*",
            "WWPT:*",
            "WGPT:*",
        ]
        summary_df = summary.df(summary_ecl, column_keys=["YEARS", *summary_columns], include_restart=False)

        # Save raw summary dataframe
        self.raw_summary_df = summary_df.copy()

        # Split date(time) column into date and time
        summary_df = summary_df.reset_index(["DATE"])
        date_time = pd.DatetimeIndex(summary_df["DATE"])
        summary_df["TIME"] = date_time.time
        summary_df["DATE"] = date_time.date

        # Extract well names from columns to rows
        summary_index = [*filter(lambda index: index in summary_df, ["DATE", "TIME", "YEARS"])]
        summary_df = summary_df.set_index(summary_index, append=True)
        summary_df.columns = summary_df.columns.str.split(":", expand=True)
        summary_df = (
            summary_df.stack(level=1)
            .rename_axis(("INDEX", *summary_index, "WELL"))
            .reset_index([*summary_index, "WELL"])
        )

        # Merge wcon with summary
        self.parsed_summary_df = wcon_df.merge(
            summary_df,
            how="left",
            on=["WELL", "DATE"],
            suffixes=("_result", "_summary"),
        )
        self.parsed_summary_df = self.parsed_summary_df.drop_duplicates(["WELL", "DATE"])

    def read_keywords(self, deck):
        """
        Reads the keywords and generate the parsed dataframe

        Args:
            deck (EclFile): eclFile to read keywords from

        Returns:
            wcon_df: dataframe with all wcon information
        """
        deck = deck.get_ecldeck()

        welopenrecords = []
        wconrecords = []
        dates = []
        date = None
        for idx, kword in enumerate(deck):
            # DATES keywords
            if kword.name == "DATES" or kword.name == "START":
                for rec in kword:
                    date = parse_opmio_date_rec(rec)
                    dates.append(date)
            elif kword.name == "TSTEP":
                if not date:
                    print("Can't use TSTEP when there is no start_date")
                    return {}
                for rec in kword:
                    steplist = parse_opmio_tstep_rec(rec)
                    # Assuming not LAB units, then the unit is days.
                    days = sum(steplist)
                    assert isinstance(date, datetime.date)
                    date += datetime.timedelta(days=days)
                    dates.append(date)

            elif kword.name in WCONKEYS:
                for rec in kword:  # Loop over the lines inside WCON* record
                    rec_data = parse_opmio_deckrecord(rec, kword.name)
                    rec_data["DATE"] = date
                    rec_data["KEYWORD"] = kword.name
                    wconrecords.append(rec_data)

            # WELOPEN keywords
            elif kword.name == "WELOPEN":
                for rec in kword:
                    rec_data = parse_opmio_deckrecord(rec, "WELOPEN")
                    rec_data["DATE"] = date
                    rec_data["KEYWORD_IDX"] = idx
                    if rec_data["STATUS"] not in [
                        "OPEN",
                        "SHUT",
                        "STOP",
                        "AUTO",
                        "POPN",
                    ]:
                        rec_data["STATUS"] = "SHUT"
                    welopenrecords.append(rec_data)

        welopen_df = pd.DataFrame(welopenrecords)
        wcon_df = pd.DataFrame(wconrecords)

        if not welopen_df.empty:
            wcon_df = expand_wcon(
                wcon_df,
                welopen_df,
            )

        # Apply dates
        dates_df = pd.DataFrame(dates, columns=["DATE"])
        if not wcon_df.empty:
            wcon_df = expand_dates(
                wcon_df,
                dates_df,
                index=["WELL"],
                fills=["STATUS", "KEYWORD", "TYPE", "ORAT", "WRAT", "GRAT"],
            )
            wcon_df["STATUS"] = wcon_df["STATUS"].fillna("SHUT")

            wcon_df[["ORAT", "WRAT", "GRAT"]] = wcon_df[["ORAT", "WRAT", "GRAT"]].fillna(0)

            wcon_df = wcon_df.drop("index", axis=1)

        return wcon_df

    def process(self):
        """
        Return the preprocessed dataframes

        Args:
            -

        Returns:
            parsed_summary_df: preprocessed dataframe with all summary + wcon information
            raw_summary_df: raw summary dataframe
        """
        return self.parsed_summary_df, self.raw_summary_df
