from sklearn.preprocessing import MinMaxScaler
import polars as pl
from Errors import DependencyError

import polars as pl

numeric=[pl.Decimal,pl.Float32,pl.Float64,pl.Int16,pl.Int32,pl.Int64,pl.Int8,pl.UInt16,pl.UInt32,pl.UInt64,pl.UInt8]
temporal=[pl.Date,pl.Datetime,pl.Duration,pl.Time]
nested=[pl.List,pl.Struct]
discrete=[pl.Boolean,pl.Binary,pl.Categorical,pl.Null,pl.Object,pl.Utf8]

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
    nested=[pl.List,pl.Struct]
    discrete=[pl.Boolean,pl.Binary,pl.Categorical,pl.Null,pl.Object,pl.Utf8]
    
    numeric_cols=data.select(pl.col(numeric)).columns
    temporal_cols=data.select(pl.col(temporal)).columns
    nested_cols=data.select(pl.col(nested)).columns
    discrete_cols=data.select(pl.col(discrete)).columns

    return numeric_cols,temporal_cols,nested_cols,discrete_cols

class LabelEncoder():
    """ A LabelEncoder based on polars. Requires the pyarrow dependecy
    """
    def __init__(self):
        self.labels_={}
        self.classes_ = []
        
    def get_encoding(self):
        return self.labels_
    
    def check_data_type(self,data):
        if data.dtypes[0] in discrete:
            return True
        else:
            raise TypeError('The Data in this Column is not discrete and thus should not be transformed with the LabelEncoder')
        
    def fit(self, data):
        self.classes_ = data.unique().to_series().to_list()
        for i, label in enumerate(self.classes_):
            self.labels_[label]=i

    def transform(self, data:pl.DataFrame):
        if self.check_data_type(data):
            try:
                return data.to_series().map_dict(self.labels_)
            except:
                raise DependencyError('The Encoding did not work, perhaps you can resolve this by installing pyarrow via pip install pyarrow','pyarrow')
    def fit_transform(self, data:pl.DataFrame):
        self.fit(data)
        return self.transform(data)

    def inverse_transform(self, data_encoded:pl.DataFrame):
        inversed_labels_={val: key for (key, val) in self.labels_.items()}
        return data_encoded.map_dict(inversed_labels_)
    

    
class DateTimeEncoder():
    """Transforms Datetimes to UNIX Timestamp which are integers
    """
    def __init__(self,datetime_format="%Y-%m-%d"):
        self.datetime_format=datetime_format
    def check_data_type(self,data):
        if data.dtypes[0] in [pl.Utf8]+discrete:
            return True
        else:
            raise TypeError('The Data in this Column is not a string and thus should not be transformed with the DateTimeEncoder')
    def fit_transform(self, data):
        if self.check_data_type(data):
            try:
                fmt = None
                if self.datetime_format:
                    fmt = self.datetime_format.replace('%-', '%')
                data = data.to_series().str.strptime(pl.Datetime,fmt)
                data=data.dt.epoch()
            except ValueError as error:
                if 'Unknown string format:' in str(error):
                    message = 'Data must be of dtype datetime, or castable to datetime.'
                    raise TypeError(message) from None
                raise ValueError('Data does not match specified datetime format.') from None
        return data
    def inverse_transform(self, data):
        return data.cast(pl.Datetime).dt.strftime(self.datetime_format)


class MinMaxScaler():
    def __init__(self,feature_range=[0,1]):
        self.min=None
        self.max=None
        self.feature_range=feature_range
        self.dtypes=None
    def get_params(self):
        return {'Max':self.max,'Min':self.min,'Column_Types':self.dtypes}
    
    def fit(self,data):
        self.min=data.min()
        self.max=data.max()

    def fit_transform(self,data):
        #data=data.to_series()
        self.dtypes=data.dtypes
        self.fit(data)
        scaler=data.with_columns([
                ((pl.col(col) - self.min[col])/(self.max[col]-self.min[col])) for col in data.columns
                ])
        return scaler*(self.feature_range[1]-self.feature_range[0])+self.feature_range[0]
    
    def inverse_transform(self,data):
        unscaled_data =(data-self.feature_range[0])/(self.feature_range[1]-self.feature_range[0])
        inversed_data=unscaled_data.with_columns([
            ((pl.col(col))*(self.max[col]-self.min[col])+self.min[col]) for col in data.columns
        ])
        return inversed_data.with_columns([(pl.col(col).cast(self.dtypes[i])) for i,col in enumerate(inversed_data.columns)])
    
class StandardScaler():
    def __init__(self):
        self.mean=None
        self.std=None
        self.dtypes=None
    def get_params(self):
        return {'Mean':self.mean,'Standard-Deviation':self.std}
    
    def fit(self,data):
        self.mean=data.mean()
        self.std=data.std()

    def fit_transform(self,data):
        self.dtypes=data.dtypes
        self.fit(data)

        return  data.with_columns([
                            ((pl.col(col)-self.mean[col])/self.std[col]) for col in data.columns 
                                   ])
    def inverse_transform(self,data):
        inversed_data=data.with_columns([
                            ((pl.col(col)*self.std[col]+self.mean[col])) for col in data.columns  
                                    ])
        return inversed_data.with_columns([(pl.col(col).cast(self.dtypes[i])) for i,col in enumerate(inversed_data.columns)])

class RobustScaler():
    def __init__(self):
        self.mean=None
        self.p75=None
        self.p25=None
        self.dtypes=None
    def get_params(self):
        return {'Mean':self.mean,'Q75':self.p75, 'Q25':self.p25}
    
    def fit(self,data):
        self.mean=data.mean()
        self.p75=data.quantile(quantile=0.75)
        self.p25=data.quantile(quantile=0.25)

    def fit_transform(self,data):
        self.dtypes=data.dtypes
        self.fit(data)
        return data.with_columns([
                    ((pl.col(col)-self.mean[col])/(self.p75[col]-self.p25[col])) for col in data.columns          
                                ])
    
    def inverse_transform(self,data):
        inversed_data=data.with_columns([
                        (pl.col(col)*(self.p75[col]-self.p25[col])+self.mean[col]) for col in data.columns
                                    ])
        return inversed_data.with_columns([(pl.col(col).cast(self.dtypes[i])) for i,col in enumerate(inversed_data.columns)])