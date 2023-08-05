import numpy as np
import pandas as pd
import datetime

from ecl2df import EclFiles

from ecl2df.common import (
    parse_opmio_deckrecord,
    parse_opmio_date_rec,
    parse_opmio_tstep_rec,
)
from ecl2df.compdat import unrolldf

from preprocessing.utils import expand_dates, expand_wcon

COMPDAT_RENAMER = {
    "WELL": "WELL",
    "I": "I",
    "J": "J",
    "K1": "K1",
    "K2": "K2",
    "STATE": "OP/SH",
    "SAT_TABLE": "SATN",
    "CONNECTION_TRANSMISSIBILITY_FACTOR": "TRAN",
    "DIAMETER": "WBDIA",
    "Kh": "KH",
    "SKIN": "SKIN",
    "D_FACTOR": "DFACT",
    "DIR": "DIR",
    "PR": "PEQVR",
}
WCONKEYS = ["WCONHIST", "WCONINJE", "WCONINJH", "WCONPROD"]


class WellSpecsProcessor:
    def __init__(self, data_path):
        self.data = EclFiles(data_path)

        self.compdat_frame, self.wcon_frame, self.dates = self.read_keywords(self.data)

        # Extract helper variables
        dimens = self.data.get_ecldeck()["DIMENS"][0]
        self.dims = np.array([dimens[2].value, dimens[0].value, dimens[1].value])

    def process(self):
        # Group dataframes by well to create the processed object
        grouped_compdat = None
        grouped_wcon = None
        if not self.compdat_frame.empty:
            grouped_compdat = self.compdat_frame.groupby(by=["WELL"], sort=False, dropna=False)
        if not self.wcon_frame.empty:
            grouped_wcon = self.wcon_frame.groupby(by=["WELL"], sort=False, dropna=False)

        # Loop the groups to create the processed object
        wells = {}
        for well_name, df in grouped_compdat:
            reference_depth = (
                df[df["REFERENCE_DEPTH"].notna()].iloc[0].at["REFERENCE_DEPTH"]
                if not df[df["REFERENCE_DEPTH"].notna()].empty
                else 0.0
            )
            df = df.groupby(by=["WELL", "I", "J", "K"], sort=False, dropna=False)

            # Get wcon information: well type and well status list
            well_type = {}
            well_phase = {}
            well_schedule = {}
            if grouped_wcon:
                wcon_info_df = grouped_wcon.get_group(well_name)
                well_type = (
                    "PRODUCER"
                    if wcon_info_df[wcon_info_df["KEYWORD"].notna()].iloc[0].at["KEYWORD"] in ["WCONHIST", "WCONPROD"]
                    else "INJECTOR"
                )
                well_schedule = (wcon_info_df["STATUS"] == "OPEN").to_list()
                well_phase = (
                    wcon_info_df[wcon_info_df["TYPE"].notna()].iloc[0].at["TYPE"]
                    if not wcon_info_df[wcon_info_df["TYPE"].notna()].empty
                    else np.nan
                )

            well_info = {
                "reference_depth": reference_depth,
                "well_type": well_type,
                "well_phase": well_phase,
                "well_schedule": well_schedule,
                "schedule": [],
                "perforations": [],
            }

            # Get compdat information: schedule matrix and perforations list
            for index, value in df:
                _, i, j, k = index
                tran_list = value["TRAN"].dropna().mode()
                tran = tran_list[0] if len(tran_list) > 0 else 0
                global_index = k * self.dims[1] * self.dims[2] + i * self.dims[2] + j

                well_info["perforations"].append([k - 1, i - 1, j - 1, global_index, tran])
                well_info["schedule"].append((value["STATUS"] == "OPEN").to_list())

            wells[well_name] = well_info

        return {
            "perforation_keys": ["k", "i", "j", "global_index", "tran"],
            "dates": self.dates,
            "wells": wells,
        }

    def read_keywords(self, deck):
        """
        Reads the keywords and generate the parsed dataframe

        Args:
            deck (EclFile): eclFile to read keywords from

        Returns:
            compdat_df: dataframe with all compdat information
            wcon_df: dataframe with all wcon information
            dates: list of timestep dates
        """

        deck = deck.get_ecldeck()

        welspecs = {}
        compdatrecords = []
        complumprecords = []
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

            # COMPLUMP keywords
            elif kword.name == "COMPLUMP":
                for rec in kword:  # Loop over the lines inside COMPLUMP record
                    rec_data = parse_opmio_deckrecord(rec, "COMPLUMP")
                    rec_data["DATE"] = date
                    complumprecords.append(rec_data)

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

            # COMPDAT keywords
            elif kword.name == "WELSPECS":
                for wellrec in kword:
                    welspecs_rec_dict = parse_opmio_deckrecord(wellrec, "WELSPECS")
                    welspecs[welspecs_rec_dict["WELL"]] = {
                        "I": welspecs_rec_dict["HEAD_I"],
                        "J": welspecs_rec_dict["HEAD_J"],
                        "REFERENCE_DEPTH": welspecs_rec_dict["REF_DEPTH"],
                    }
            elif kword.name == "COMPDAT":
                for rec in kword:  # Loop over the lines inside COMPDAT record
                    rec_data = parse_opmio_deckrecord(rec, "COMPDAT", renamer=COMPDAT_RENAMER)
                    rec_data["DATE"] = date
                    rec_data["KEYWORD_IDX"] = idx
                    if rec_data["I"] == 0:
                        if rec_data["WELL"] not in welspecs:
                            raise ValueError("WELSPECS must be provided when I is defaulted in COMPDAT")
                        rec_data["I"] = welspecs[rec_data["WELL"]]["I"]
                    if rec_data["J"] == 0:
                        if rec_data["WELL"] not in welspecs:
                            raise ValueError("WELSPECS must be provided when J is defaulted in COMPDAT")
                        rec_data["J"] = welspecs[rec_data["WELL"]]["J"]
                    if not rec_data.get("REFERENCE_DEPTH"):
                        rec_data["REFERENCE_DEPTH"] = welspecs[rec_data["WELL"]]["REFERENCE_DEPTH"]
                    compdatrecords.append(rec_data)
            elif kword.name in WCONKEYS:
                for rec in kword:  # Loop over the lines inside WCON* record
                    rec_data = parse_opmio_deckrecord(rec, kword.name)
                    rec_data["DATE"] = date
                    rec_data["KEYWORD"] = kword.name
                    wconrecords.append(rec_data)

        compdat_df = pd.DataFrame(compdatrecords)
        welopen_df = pd.DataFrame(welopenrecords)
        complump_df = pd.DataFrame(complumprecords)
        wcon_df = pd.DataFrame(wconrecords)

        if not compdat_df.empty:
            compdat_df = unrolldf(compdat_df, "K1", "K2")

            compdat_df = compdat_df.drop(["K2"], axis=1)
            compdat_df.rename(columns={"K1": "K", "OP/SH": "STATUS"}, inplace=True)

        if not welopen_df.empty:
            compdat_df = self.apply_compdat_welopen(
                compdat_df,
                welopen_df,
                complump_df,
            )
            wcon_df = expand_wcon(
                wcon_df,
                welopen_df,
            )

        # Apply dates
        dates_df = pd.DataFrame(dates, columns=["DATE"])
        if not compdat_df.empty:
            compdat_df = expand_dates(
                compdat_df,
                dates_df,
                index=["WELL", "I", "J", "K"],
                fills=["STATUS", "TRAN", "REFERENCE_DEPTH"],
            )
            compdat_df["STATUS"] = compdat_df["STATUS"].fillna("SHUT")

        if not wcon_df.empty:
            wcon_df = expand_dates(wcon_df, dates_df, index=["WELL"], fills=["STATUS", "KEYWORD"])
            wcon_df["STATUS"] = wcon_df["STATUS"].fillna("SHUT")

        if "KEYWORD_IDX" in compdat_df.columns:
            compdat_df.drop(["KEYWORD_IDX"], axis=1, inplace=True)

        if not "TYPE" in wcon_df.columns:
            wcon_df["TYPE"] = np.nan

        return compdat_df, wcon_df, dates

    def apply_compdat_welopen(self, compdat_df, welopen_df, complump_df):
        """
        Expand compdat with all welopen info

        Args:
            compdat_df (Dataframe): compdat_df to expand welopen
            welopen_df (Dataframe): welopen_df dataframe

        Returns:
            dataframe: dataframe with the expanded welopen
        """

        # Remove well interactions
        welopen_df = welopen_df.query("not (I.isnull() and J.isnull() and K.isnull() and C1.isnull() and C2.isnull())")
        specific_welopen = welopen_df.query("not (I.isnull() and J.isnull() and K.isnull())")
        welopen_complump = welopen_df.query("not (C1.isnull() and C2.isnull())")

        welopen_complump = self.expand_complump_in_welopen_df(welopen_complump, complump_df)

        # Drop and rename columns
        specific_welopen = specific_welopen.drop(["C1", "C2"], axis=1)

        welopen_complump = welopen_complump.drop(
            ["C1", "C2", "N", "K", "K2", "I_welopen", "J_welopen", "DATE_complump"],
            axis=1,
        )
        welopen_complump.rename(
            columns={
                "DATE_welopen": "DATE",
                "I_complump": "I",
                "J_complump": "J",
                "K1": "K",
            },
            inplace=True,
        )

        # Add missing information from compdat
        dataframe = (
            pd.concat(
                [compdat_df, specific_welopen, welopen_complump],
                keys=["I", "J", "K", "WELL", "DATE", "STATUS"],
                ignore_index=True,
            )
            .drop_duplicates(subset=["I", "J", "K", "WELL", "DATE", "STATUS"])
            .merge(
                compdat_df,
                how="left",
                on=["WELL", "I", "J", "K"],
                suffixes=("_result", "_compdat"),
            )
        )

        # Clean result
        dataframe.drop(
            [
                "SATN_result",
                "TRAN_result",
                "WBDIA_result",
                "KH_result",
                "SKIN_result",
                "DFACT_result",
                "DIR_result",
                "PEQVR_result",
                "KEYWORD_IDX_result",
                "KEYWORD_IDX_compdat",
                "DATE_compdat",
                "STATUS_compdat",
            ],
            axis=1,
            inplace=True,
        )
        dataframe.rename(
            columns={
                "SATN_compdat": "SATN",
                "TRAN_compdat": "TRAN",
                "WBDIA_compdat": "WBDIA",
                "KH_compdat": "KH",
                "SKIN_compdat": "SKIN",
                "DFACT_compdat": "DFACT",
                "DIR_compdat": "DIR",
                "PEQVR_compdat": "PEQVR",
                "DATE_result": "DATE",
                "STATUS_result": "STATUS",
                "REFERENCE_DEPTH_compdat": "REFERENCE_DEPTH",
            },
            inplace=True,
        )

        return dataframe

    def expand_complump_in_welopen_df(self, welopen_df, complump_df):
        """
        Expand welopen with all complump info

        Args:
            welopen_df (Dataframe): welopen_df to expand complump
            complump_df (Dataframe): complump_df dataframe

        Returns:
            dataframe: dataframe with the expanded complump
        """

        # Fill Nan values
        welopen_df["C2"] = welopen_df["C2"].fillna(welopen_df["C1"])
        complump_df["K2"] = complump_df["K2"].fillna(complump_df["K1"])

        # Unroll
        welopen_df = unrolldf(welopen_df, "C1", "C2")
        complump_df = unrolldf(complump_df, "K1", "K2")

        # Merge complump with welopen
        return complump_df.merge(
            welopen_df,
            how="inner",
            left_on=["WELL", "N"],
            right_on=["WELL", "C1"],
            suffixes=("_complump", "_welopen"),
        )
