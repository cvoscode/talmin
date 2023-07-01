import sys

import dash_bootstrap_components as dbc
import plotly.express as px
import polars as pl

from dash import Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate

sys.path.insert(0, r'talmin')
from plotting.Base_Plotter import *
from utils.Base_Components import *
from utils.polars_addons import detect_column_types

save_path=''

class HistogramPlotter(Base_Fig):
    def __init__(self, id):
        self.x=None
        self.y=None
        self.color=None
        self.bins=None
        self.histfunc=None
        self.histnorm=None
        self.cumulative=None
        self.barmode=None
        self.marginal=None
        self.text_auto=False
        self.bargap=None
        self.fig={}
        self.numeric_cols=None
        self.temporal_cols=None
        self.nested_cols=None
        self.discrete_cols=None
        self.title=None
        self.id=id
    def update_title(self,title):
        self.title=title

    def set_data(self,df:pl.DataFrame):
        self.data=df
        self.numeric_cols,self.temporal_cols,self.nested_cols,self.discrete_cols=detect_column_types(df)
        self.all_columns=df.columns

    def set_x(self,x:str):
        """_summary_

        Args:
            x (str): name of x col
        """
        self.x=x
    def set_color(self,color:str):
        """_summary_

        Args:
            color (str): color col
        """
        self.color=color
    def set_histnorm(self,histnorm:str):
        self.histnorm=histnorm
    def set_bins(self, bins:int):
        self.bins=bins
    def set_bargap(self, bargap:str):
        self.bargap=bargap
    def set_histfunc(self, histfunc:str):
        self.histfunc=histfunc
    def set_marginal(self,marginal):
        self.marginal=marginal
    def set_text_auto(self,text_auto:bool):
        self.text_auto=text_auto
    def set_barmode(self,barmode:bool):
        self.barmode=barmode
    def set_cumulative(self,cumulative:bool)-> bool:
        # weird that a conversion is needed and by text_auto not?
        if cumulative=='True':
            self.cumulative=True
        else:
            self.cumulative= False
    def update_fig(self):
        if self.x and not self.y:
            self.fig=px.histogram(self.data.to_pandas(),x=self.x,color=self.color, nbins=self.bins,histnorm=self.histnorm,histfunc=self.histfunc,marginal=self.marginal,text_auto=self.text_auto,barmode=self.barmode,cumulative=self.cumulative)
        if self.bargap:
            self.fig.update_layout(bargap=self.bargap)
        if self.title:
            self.fig.update_layout(title=self.title)
    
        
    def get_plot_ui(self):
        ui=html.Div([
        dbc.Row(    
        dbc.Card([               
            dbc.Row(id=f'plot-div-{self.id}',children=[dcc.Loading(id=f'loading-{self.id}',children=[dcc.Graph(id=f'Graph-{self.id}',figure={},config=dict(displaylogo=False, toImageButtonOptions=dict(format= 'svg'),
                    modeBarButtonsToAdd=['drawline',
                                        'drawopenpath',  
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]))]),  
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle(f"Scatter Graph")),
                            dbc.ModalBody(dcc.Graph(id=f'Graph-Modal-{self.id}',figure={},config=dict(displaylogo=False, toImageButtonOptions=dict(format= 'svg'),
                                        modeBarButtonsToAdd=['drawline',
                                        'drawopenpath',  
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]))),
                            dbc.ModalFooter(
                                dbc.Button("Close", id=f"close-modal-{self.id}", className="ml-auto"),
                                 ),
                        ],
                        id=f"modal-fs-{self.id}",
                        fullscreen=True,is_open=False
                    )]),
            dbc.Row(dbc.Col(dbc.Stack([create_Button(id=f'popup-button-{self.id}', color='primary',children=['Popup']),html.Div(id=f'plot_div-{self.id}') ],direction='horizontal'), width={"offset":11})),
            create_Tooltip(f"Opens the graph in full screen mode",target=f'popup-button-{self.id}')
            ]),),])
        return ui
    def get_settings_ui(self):
        ui=dbc.Row([
            html.Hr(),
            dbc.Col([
            create_dropdown_paging(id=f'X-{self.id}',options=self.all_columns,value=None,name='X-Column',multi=False),
            create_Tooltip('Select a column from your data for the horizontal axis',target=f'X-{self.id}')
            ]),
            dbc.Col([
            create_dropdown_paging(id=f'color-{self.id}',options=self.discrete_cols,value=None,name='Color-Column',multi=False),
            create_Tooltip('Select a column from your data as color',target=f'color-{self.id}')
            ]),
            dbc.Col([
            create_Numeric_Input(id=f'nbins-{self.id}',value=20,step=1,min=1,max=10000),
            create_Tooltip('Select the value for bin count',target=f'nbins-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'histfunc-{self.id}',options=['count','sum','avg','min','max'],value='count'),
            create_Tooltip('Select the aggrigation function for the plot',target=f'histfunc-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'histnorm-{self.id}',options=['percent','probability','density','probability density'],value=None),
            create_Tooltip('Select the normalization function for the plot',target=f'histnorm-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'marginal-{self.id}',options=['rug','box','violin','histogram'],value=None),
            create_Tooltip('Select which marginal plot should be shown',target=f'marginal-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'barmode-{self.id}',options=['group','overlay','relative'],value='relativ'),
            create_Tooltip('Select a mode in which multiple historgams are presented',target=f'barmode-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'text-auto-{self.id}',options={True:'add automatic labels',False:'no labels'},value=False),
            create_Tooltip('Select if bars of the historgam should be labeled',target=f'text-auto-{self.id}')
            ]),
            dbc.Col([
            create_dropdown(id=f'cumulative-{self.id}',options={True:'cumulative',False:'non cumulative'},value=False),
            create_Tooltip('Select if the histogram should be cumulative',target=f'cumulative-{self.id}')
            ]),
            dbc.Col([
            dbc.InputGroup([
            dbc.InputGroupText('Title'),
            create_Text_Input(placeholder='Provide a title for saving',id=f'title-{self.id}'),
            create_Button(id=f'save-{self.id}',children=['Save Plot as HTML'],color='primary'),
            ]),
            create_Tooltip('Set your plot Title, the same title is used while saving',target=f'title-{self.id}'),
            create_Tooltip('Save your plot as an HTML file under the globally set directory',target=f'save-{self.id}'),
            ]),
        ])     
        return ui
    
    def cerate_base_callbacks(self, app):
        @app.callback(Output(f"modal-fs-{self.id}",'is_open'),
                    Input(f'popup-button-{self.id}','n_clicks'),
                    Input(f"close-modal-{self.id}",'n_clicks'),allow_duplicate=True)
        def modal(popup,clos):
            if ctx.triggered_id==f'popup-button-{self.id}':
                return True
            if ctx.triggered_id==f"close-modal{self.id}":
                return False
            
        @app.callback(Output(f'Graph-{self.id}','figure'),
                      Output(f'Graph-Modal-{self.id}','figure'),
                      Output(f'plot_div-{self.id}','children',allow_duplicate=True),
                      Input(f'X-{self.id}','value'),
                      Input(f'color-{self.id}','value'),
                      Input(f'histnorm-{self.id}','value'),
                      Input(f'histfunc-{self.id}','value'),
                      Input(f'nbins-{self.id}','value'),
                      Input(f'cumulative-{self.id}','value'),
                      Input(f'text-auto-{self.id}','value'),
                      Input(f'barmode-{self.id}','value'),
                      Input(f'marginal-{self.id}','value'),
                      Input(f'title-{self.id}','value'),
                      prevent_initial_call=True,)
        def vals(x,color,histnorm,histfunc,nbins,cumulative,text,barmode,marginal,title):
            if ctx.triggered_id==f'X-{self.id}':
                self.set_x(x)
            elif ctx.triggered_id==f'color-{self.id}':
                self.set_color(color)
            elif ctx.triggered_id==f'histnorm-{self.id}':
                self.set_histnorm(histnorm)
            elif ctx.triggered_id==f'nbins-{self.id}':
                self.set_bins(nbins)
            elif ctx.triggered_id==f'histfunc-{self.id}':
                self.set_histfunc(histfunc)
            elif ctx.triggered_id==f'cumulative-{self.id}':
                self.set_cumulative(cumulative)
            elif ctx.triggered_id==f'text-auto-{self.id}':
                self.set_text_auto(text)
            elif ctx.triggered_id==f'barmode-{self.id}':
                self.set_barmode(barmode)
            elif ctx.triggered_id==f'marginal-{self.id}':
                self.set_marginal(marginal)
            elif ctx.triggered_id==f'title-{self.id}':
                self.update_title(title=title)
                self.fig.update_layout(title=self.title)
                return self.fig,self.fig,[]
            self.update_fig()
            if self.fig:
                return self.fig,self.fig,[]
            else:
                raise PreventUpdate
                       
            
        # @app.callback(Output(f'color-{self.id}','disabled'),
        #               Output(f'save-{self.id}','disabled'),
        #               Output(f'title-{self.id}','disabled'),
        #               Input(f'X-{self.id}','value'),
        #               Input(f'Y-{self.id}','value'),
        #                )
        # def activate_settings(x,y):
        #     if not x or not y:
        #         return [True,True,True]
        #     else:
        #         return [False,False,False]
        
        for id in [f'X-{self.id}',f'color-{self.id}']:
            create_dropdown_paging_callback(id,app)

        @app.callback(Output(f'plot_div-{self.id}','children',allow_duplicate=True),
                      Input(f'save-{self.id}','n_clicks'),
                      State(f'title-{self.id}','value'),
                      prevent_initial_callback=True
                      )
        #TODO correct save plot
        def save_plot(save,title):
            if save:
                super.save(self.fig,title,save_path)
                return create_Toast(children=f'The plot was sucessfully saved to {save_path} under the name {title}',header='Plot saved',icon='sucess')