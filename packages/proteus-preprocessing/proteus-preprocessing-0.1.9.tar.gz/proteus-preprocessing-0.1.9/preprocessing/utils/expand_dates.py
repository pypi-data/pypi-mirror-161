def expand_dates(dataframe, dates_df, index=[], fills=[]):
    """
    Expand dataframe with all the provided dates,
    it will use the index list to drop duplicates

    Args:
        dataframe (Dataframe): dataframe to expand dates
        dates_df (Dataframe): dates dataframe
        index (List): list of index of the dataframe
        fills (List): list of columns to fordward fill

    Returns:
        dataframe: dataframe with the expanded dates
    """

    well_names_df = dataframe.drop_duplicates(index)
    well_names_df = well_names_df[index]

    cross_merge = dates_df.merge(well_names_df, how="cross")

    merge_keys = index + ["DATE"]
    dataframe = dataframe.merge(cross_merge, how="right", on=merge_keys, suffixes=("_compdat", "_dates"))
    dataframe = dataframe.sort_values(merge_keys).reset_index()

    grouped_compdat = dataframe.groupby(by=index, sort=False, dropna=False)

    for fill in fills:
        if fill in dataframe.columns:
            dataframe[fill] = grouped_compdat[fill].fillna(method="ffill")

    return dataframe
