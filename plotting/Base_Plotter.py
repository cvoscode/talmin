import plotly.graph_objs as go
import plotly.offline as offline
from dash import dcc,html,Input, Output, State,ctx
import dash
import dash_bootstrap_components as dbc
import os
import time
import sys
# insert package path to get the utils components
sys.path.insert(0, r'talmin')
from utils.Base_Components import *

class PlotlyFigure:
    def __init__(self,id, data=None, layout=None ,fig=None):
        """_summary_

        Args:
            data (plotly.Figure.data): data to plot
            layout (plotly.Figure.layout): plotly layout dict
            id (str): Dash Component ID
            fig (go.Figure): plotly Figure
        """
        if not data and not layout and not fig:
            raise ValueError('You must either provide data and layout to be displayed or a fig ')
        if not fig:
            self.fig=go.Figure(data=data, layout=layout)
        else:
            try: 
                self.fig=fig
                self.layout = fig.layout
            except:
                raise TypeError('No valid plotly figure was supplied')
        self.data = data
        self.id=id
        
        self.save_button=create_Button(id=f'save-button-{self.id}', color='primary',children=['Save Graph'])
        self.popup_button=create_Button(id=f'popup-button-{self.id}', color='primary',children=['Popup'])
        self.title_input=create_Text_Input(id=f'title-input-{self.id}',placeholder='Enter a new title for the graph',value=[self.layout['title'] if isinstance(self.layout['title'],str) else self.layout['title']['text']])
        self.save_tooltip=create_Tooltip(f"Saves the graph to a html file named after the current title of the graph",target=f'save-button-{self.id}')      
        self.popup_tooltip=create_Tooltip(f"Opens the graph in full screen mode",target=f'popup-button-{self.id}')
        self.title_tooltip=create_Tooltip(f"Provides the title of the graph",target=f'title-input-{self.id}')
    
    def get_figure(self):
        """Update Funktion for the Graph

        Returns:
            dcc.Graph: dcc Graph element which is updated
        """
        return dcc.Loading(id=f'loading-{self.id}',children=[dcc.Graph(id=f'Graph-{self.id}',figure=self.fig,config=dict(displaylogo=False, toImageButtonOptions=dict(format= 'svg'),
                    modeBarButtonsToAdd=['drawline',
                                        'drawopenpath',  
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]))])

    def update_data(self,data):
        self.data=data

    def add_trace(self, trace):
        """Add a new trace to the figure"""
        self.fig.add_trace(trace)
    
    def update_layout(self, **kwargs):
        """
        Updates the layout 
        """
        self.fig.update_layout(**kwargs)

    def update_traces(self, updates, selector=None):
        """Updates Traces of the graph

        Args:
            updates (_type_): Updates to the traces
            selector (_type_, optional): Selector of which trace should be updated. Defaults to None.
        """
        # not sure if that really works :D
        self.fig.update_traces(updates, selector=selector)

    def update_title(self, new_title):
        """updates the Graph title

        Args:
            new_title (str): New graph title
        """
        self.layout['title'] = new_title

    def save(self, filename,auto_open=False):
        """
        Save the Plotly figure as an image file

        Args:
            filename (str): Path and Name of the Graph to be saved
            auto_open (bool, optional): Open the html_file in the default browser. Defaults to False.
        """
        try:
            filename=filename+'.html'
            os.makedirs(os.path.dirname(filename),exist_ok=True)
            offline.plot(self.fig,filename=filename,auto_open=auto_open,include_plotlyjs='cdn',config=
                         dict(displaylogo=False, toImageButtonOptions=dict(format= 'svg'),
                    modeBarButtonsToAdd=['drawline',
                                        'drawopenpath',  
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape'
                                       ]))
            return filename,True
        except:
            return filename, False

    def get_ui(self):
        ui=html.Div([
            dbc.Row(id=f'plot-div-{self.id}',children=[self.get_figure()]),
            dbc.Row(dbc.Col(dbc.Stack([self.title_input,self.save_button,self.popup_button],direction='horizontal', gap=2), width={"offset":8})),
            self.save_tooltip,
            self.popup_tooltip,
            self.title_tooltip,
        ])
        return ui
    def cerate_base_callbacks(self,app):        
        @app.callback(Output(f'plot-div-{self.id}','children'),
                      Input(f'popup-button-{self.id}','n_clicks'),
                      Input(f'title-input-{self.id}','value'),
                      Input(f'save-button-{self.id}','n_clicks'),
                      suppress_callback_exceptions=True)
        def popup(popup,title,save):
            if ctx.triggered_id ==f'popup-button-{self.id}':
                return [self.get_figure(),
                        dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle(f"{self.layout['title'] if isinstance(self.layout['title'],str) else self.layout['title']['text']} Graph")),
                            dbc.ModalBody(self.get_figure()),
                            dbc.ModalFooter(
                                dbc.Button("Close", id=f"close-modal{self.id}", className="ml-auto"),
                                 ),
                        ],
                        id="modal-fs",
                        fullscreen=True,is_open=True
                    )]
            elif ctx.triggered_id ==f'title-input-{self.id}':
                    self.fig.update_layout(title=title)
                    return self.get_figure()
            elif ctx.triggered_id==f'save-button-{self.id}':
                    filename,sucess=self.save(filename=title)
                    if sucess:
                        return self.get_figure(),create_Toast([html.P(f'The graph was sucessfully save to "{filename}"!')],'Save sucessful',icon="success")
                    else:
                        return self.get_figure(), create_Toast([html.P(f'The graph could not be save to "{filename}"! If no title was set, please provide one.')],header='Saveing Error',icon="danger")
            else: return self.get_figure()