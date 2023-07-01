import polars as pl 
import dash



class DataContainer(dash.Dash):
    def __init__(self) -> None:
        self.data=None
    
    def set_data(self,data:pl.DataFrame) -> None:
        self.data=data

    def get_data(self, data:pl.DataFrame) -> pl.DataFrame:
        return self.data


