import pandas as pd


def migrate(df: pd.DataFrame):
    # migrate data
    df = df.loc[:, ~df.columns.str.endswith('impactAssessment.systemBoundary')]

    # make sure to return the DataFrame so it can be uploaded
    return df
