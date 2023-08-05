def expand_wcon(wcon_df, welopen_df):
    """
    Expand wcon with all welopen info

    Args:
        wcon_df (Dataframe): wcon_df to expand welopen
        welopen_df (Dataframe): welopen_df dataframe

    Returns:
        dataframe: dataframe with the expanded welopen
    """

    # Filter by well interactions
    welopen_df = welopen_df.query("I.isnull() and J.isnull() and K.isnull() and C1.isnull() and C2.isnull()")

    # Drop and rename columns
    welopen_df = welopen_df.drop(["I", "J", "K", "C1", "C2", "KEYWORD_IDX"], axis=1)

    dataframe = wcon_df.merge(welopen_df, how="outer", on=["WELL", "DATE"], suffixes=("_result", "_welopen"))
    dataframe["STATUS_result"] = dataframe["STATUS_result"].fillna(dataframe["STATUS_welopen"])
    dataframe = dataframe.drop(["STATUS_welopen"], axis=1)
    dataframe.rename(columns={"STATUS_result": "STATUS"}, inplace=True)

    return dataframe
