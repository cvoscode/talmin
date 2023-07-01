import polars as pl 
def detect_column_types(data:pl.DataFrame): 
    """Get the discrete columns in a dataset.
    Args:
        data (pl.DataFrame):
    Returns:
        numeric_cols (list):
            List of numeric Columns in a polars dataframe.
        temporal_cols (list):
            List of temporal Columns in a polars dataframe.
        nested_cols (list):
            List of nested Columns in a polars dataframe.
        discrete_cols (list):
            List of discrete Columns in a polars dataframe.
    """
    numeric=[pl.Decimal,pl.Float32,pl.Float64,pl.Int16,pl.Int32,pl.Int64,pl.Int8,pl.UInt16,pl.UInt32,pl.UInt64,pl.UInt8]
    temporal=[pl.Date,pl.Datetime,pl.Duration,pl.Time]
    nested=[pl.List]
    discrete=[pl.Boolean,pl.Binary,pl.Categorical,pl.Null,pl.Object,pl.Utf8]
    
    numeric_cols=data.select(pl.col(numeric)).columns
    temporal_cols=data.select(pl.col(temporal)).columns
    nested_cols=data.select(pl.col(nested)).columns
    discrete_cols=data.select(pl.col(discrete)).columns

    return numeric_cols,temporal_cols,nested_cols,discrete_cols