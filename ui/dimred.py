import dash 
import polars as pl 
import plotly.graph_objects as go 
import dash_bootstrap_components as dbc
import sys
sys.path.insert(0, r'talmin')
from numba.core.errors import NumbaDeprecationWarning
import warnings
warnings.filterwarnings("ignore", category=NumbaDeprecationWarning) 
from utils.Base_Components import *
from dash import dcc,html,Input, Output, State,ctx
from plotting.ScatterPlot import ScatterPlotter
from sklearn.decomposition import PCA,KernelPCA,FastICA
from sklearn.manifold import TSNE,MDS
import plotly.express as px
import umap



class DimensionReducer(dash.Dash):
    def __init__(self, id):
        self.data=pl.DataFrame()
        self.id=id

    def set_data(self,data):
        """set data

        Args:
            data (pl.DataFrame): data for the class
        """
        self.data=data
    def get_data(self) -> pl.DataFrame:
        """get data

        Args:
            data (pl.DataFrame): data of the class

        Returns:
            data: pl.DataFrame
        """
        return self.data 
    def get_ui(self):
        return [dbc.Row(children=[dbc.Stack([create_dropdown_paging(id=f'mode-{self.id}',options=['PCA','KernelPCA','FastICA','UMAP','TSNE','MDS'],value='PCA',name='Select Dimension Reduction Type',multi=False),
                                             create_dropdown_paging(f'dimred-color-{self.id}',options=self.data.columns,value='',name='Select Color',multi=False),
                                             create_dropdown_paging(f'dimred-dimensions-{self.id}',options=[2,3],value=2,name='Select Dimension',multi=False),
                                             create_Button(f'dimred-button-{self.id}',color='secondary',children=['Reduce Dimensions'])
                                             ]),
                                  
                                          ]),
                dbc.Row(id=f'dimred-space-{self.id}',children=dcc.Loading(id=f'dimred-space-loading{self.id}')),
                create_Tooltip(target=f'mode-{self.id}',tip='Select DimRed Algorithm. You can select between PCA (Principal Componet Analysis), KernelPCA, FastIndependent Component Analysis (FastICA), UMAP, T-distributed Stochastic Neighbor Embedding (TSNE) and Multidimensional scaling (MDS)'),
                create_Tooltip(target=f'dimred-color-{self.id}',tip='Select column for color. The column is removed from the DimRed.'),]
    def create_base_callbacks(self,app):
        @app.callback(Output(f'dimred-space-loading{self.id}','children'),
                       State(f'mode-{self.id}','value'),
                       State(f'dimred-dimensions-{self.id}','value'),
                       State(f'dimred-color-{self.id}','value'),
                       Input(f'dimred-button-{self.id}','n_clicks'),
                       prevent_inital_call=True)
        def create_plots(mode,dimensions,color,button):
            """creates plot specifc settings
            Args:
                plot_type (string):type of the plot
            """
            if ctx.triggered_id==f'dimred-button-{self.id}':
                if color:
                    color_col=self.data.select(color).to_series()
                else:
                    color_col=None    
                if dimensions==2:
                    # try:
                    if mode=='PCA':
                        red=PCA(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                    # using numpy arrays lets row values match with original, otherwise very few rows
                    if mode=='KernelPCA':
                        red=KernelPCA(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                    if mode=='FastICA':
                        red=FastICA(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                    if mode=='TSNE':
                        red=TSNE(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                    if mode=='UMAP':
                        red=umap.UMAP(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                    if mode=='MDS':
                        red=MDS(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                    return dcc.Graph(id=f'dimread-graph-{self.id}',figure=px.scatter(red,x=red[:,0],y=red[:,1],color=color_col))
                    # except:
                    #      return create_Toast(header='Warning',icon='warning',children='Dimension could not be reduced. Maybe you still have non-numerical datatypes?')
                if dimensions==3:
                    try:
                        if mode=='PCA':
                            red=PCA(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                        if mode=='KernelPCA':
                            red=KernelPCA(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                        if mode=='FastICA':
                            red=FastICA(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                        if mode=='TSNE':
                            red=TSNE(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                        if mode=='UMAP':
                            red=umap.UMAP(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                        if mode=='MDS':
                            red=MDS(n_components=dimensions,random_state=42).fit_transform(self.data.select(pl.exclude(color)).to_numpy())
                        return dcc.Graph(id=f'dimread-graph-{self.id}',figure=px.scatter_3d(red,x=red[:,0],y=red[:,1],z=red[:,2],color=color_col))
                    except:
                        return create_Toast(header='Warning',icon='warning',children='Dimension could not be reduced. Maybe you still have non-numerical datatypes?')
                    
                    
                return [],[]
        create_dropdown_paging_callback(f'Mode-{self.id}',app)
        create_dropdown_paging_callback(f'dimred-dimensions-{self.id}',app)
        