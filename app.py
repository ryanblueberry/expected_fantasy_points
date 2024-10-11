from shiny import App, render, ui, reactive
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from shinywidgets import output_widget, register_widget

vals = pd.read_csv("https://raw.githubusercontent.com/ryanblueberry/data/main/vals.csv")

def gb_all(vals):
    vals_gb = vals.groupby('player_id', as_index = False).agg(player_name = ('player_name','last'),
                                                          team = ('team','last'),
                                                          position = ('position','last'),
                                                          avg_pts = ('pts','mean'),
                                                          avg_pred = ('preds', 'mean'),
                                                          games = ('preds','count'))
    vals_gb['avg_pred'] = np.round(vals_gb['avg_pred'].astype(np.float64),2)
    vals_gb['avg_pts'] = np.round(vals_gb['avg_pts'].astype(np.float64),2)
    vals_gb['points over expectation'] = np.round(vals_gb['avg_pts']-vals_gb['avg_pred'],2)
    vals_gb = vals_gb[['player_id', 'player_name', 'team', 'position', 'avg_pts', 'avg_pred','points over expectation',
       'games']]
    return vals_gb

def l4(vals):
    max1 = max(vals['week'])
    vals = vals[vals['week']> (max1-4)]
    return vals

def gb_l4(vals):
    max1 = max(vals['week'])
    vals = vals[vals['week']> (max1-4)]
    vals_gb = vals.groupby('player_id', as_index = False).agg(player_name = ('player_name','last'),
                                                      team = ('team','last'),
                                                      position = ('position','last'),
                                                      avg_pts = ('pts','mean'),
                                                      avg_pred = ('preds', 'mean'),
                                                      games = ('preds','count'))
    vals_gb['avg_pred'] = np.round(vals_gb['avg_pred'].astype(np.float64),2)
    vals_gb['avg_pts'] = np.round(vals_gb['avg_pts'].astype(np.float64),2) 
    vals_gb['points over expectation'] = np.round(vals_gb['avg_pts']-vals_gb['avg_pred'],2)
    vals_gb = vals_gb[['player_id', 'player_name', 'team', 'position', 'avg_pts', 'avg_pred','points over expectation',
       'games']]
    
    return vals_gb

all_vals = gb_all(vals)
l4_vals = gb_l4(vals)

app_ui = ui.page_fluid(
    ui.navset_pill(
        ui.nav("Expected Fantasy Points Table",
               ui.br(),
               ui.panel_title("Fantasy Usage: Expected Fantasy Points"),
                    #ui.br(),
                    ui.row(ui.column(4,"""
                                     Whole season or last month:""")),
                        ui.column(8,
                            ui.input_radio_buttons('choice',
                           '',
                           [
                               'Season',
                               'Last month'
                           ], inline = True, width = '100%')),
                    ui.row(
                        ui.column(2, ui.input_checkbox_group('pos_check',
                                       'Position:',
                                       {'QB':'QB',
                                        'RB':'RB',
                                        'WR':'WR',
                                        'TE':'TE'},
                                        selected=['QB','RB','WR','TE'])),
                        ui.column(2, ui.input_slider('gm_slider',
                                        'Minimum games played:',
                                        min = 0,
                                        max = 4, ###add output here for max val
                                        value = 0)),
                        ui.column(4, ui.input_slider('exp_slider',
                                        'Minimum of expected fantasy points included:',
                                        min = 0, 
                                        max=max(all_vals['avg_pred']),
                                        value = 4,
                                        step = 0.5)),
                        ui.column(4, ui.input_slider('act_slider',
                                        'Minimum of actual fantasy points included:',
                                        min = 0, 
                                        max=max(all_vals['avg_pts']),
                                        value = 4,
                                        step = 0.5))),
                    ui.row(
                        ui.column(12,
                            ui.output_data_frame("mygrid")))),
        ui.nav('Expected Fantasy Points Chart',
                ui.br(),
               ui.panel_title("Fantasy Usage: Chart of Expected Fantasy Points"),
                    #ui.br(),
                    ui.row(ui.column(4,"""
                                     Whole season or last month:""")),
                        ui.column(8,
                            ui.input_radio_buttons('choice1',
                           '',
                           [
                               'Season',
                               'Last month'
                           ], inline = True, width = '100%')),
                    ui.row(
                        ui.column(2, ui.input_checkbox_group('pos_check1',
                                       'Position:',
                                       {'QB':'QB',
                                        'RB':'RB',
                                        'WR':'WR',
                                        'TE':'TE'},
                                        selected=['QB','RB','WR','TE'])),
                        ui.column(2, ui.input_slider('gm_slider1',
                                        'Minimum games played:',
                                        min = 0,
                                        max = 4, ###add output here for max val
                                        value = 0)),
                        ui.column(4, ui.input_slider('exp_slider1',
                                        'Minimum of expected fantasy points included:',
                                        min = 0, 
                                        max=max(all_vals['avg_pred']),
                                        value = 4,
                                        step = 0.5)),
                        ui.column(4, ui.input_slider('act_slider1',
                                        'Minimum of actual fantasy points included:',
                                        min = 0, 
                                        max=max(all_vals['avg_pts']),
                                        value = 4,
                                        step = 0.5))),
                    ui.row(
                        ui.column(12,
                            output_widget("myplt"))))
    )
)
def server(input,output,session):
    @reactive.Effect
    def _2():
        if input.choice1() == 'Season':
            vals1 = all_vals
        else:
            vals1 = l4_vals
        vals1 = vals1[(vals1['avg_pts'] >= input.act_slider1()) &
                    (vals1['avg_pred'] >= input.exp_slider1()) &
                    (vals1['games'] >= input.gm_slider1()) &
                    (vals1['position'].isin(input.pos_check1()))]
        vals1 = vals1.sort_values(by='position')
        myplt = px.scatter(vals1, 
                        x = 'avg_pred',
                        y='avg_pts', 
                        hover_data =['player_name'],
                        symbol ='position',
                        color = 'position',
                        trendline='ols',
                        trendline_scope='overall')
        myplt.update_xaxes(title = 'average points scored')
        myplt.update_yaxes(title = 'average expected fantasy points')
        register_widget('myplt',myplt)
        
    

    @reactive.Effect
    def _():
        if input.choice()== 'Season':
            ui.update_slider("gm_slider", value = 0, min = 0, max = max(all_vals['games']))
        else:
            ui.update_slider("gm_slider", value = 0, min = 0, max = 4)
    @reactive.Effect
    def _1():
        if input.choice1()== 'Season':
            ui.update_slider("gm_slider1", value = 0, min = 0, max = max(all_vals['games']))
        else:
            ui.update_slider("gm_slider1", value = 0, min = 0, max = 4)
        
    @output
    @render.data_frame
    def mygrid():
        if input.choice() == 'Season':
            all_vals1 = all_vals[(all_vals['avg_pts'] >= input.act_slider()) &
                                 (all_vals['avg_pred'] >= input.exp_slider()) &
                                 (all_vals['games'] >= input.gm_slider()) &
                                 (all_vals['position'].isin(input.pos_check()))]
        if input.choice() == 'Last month':
            all_vals1 = l4_vals[(l4_vals['avg_pts'] >= input.act_slider()) &
                                (l4_vals['avg_pred'] >= input.exp_slider()) &
                                (l4_vals['games'] >= input.gm_slider()) &
                                (l4_vals['position'].isin(input.pos_check()))]
        all_vals1 = all_vals1.sort_values(by = 'avg_pts', ascending = False)
        return render.DataGrid(all_vals1.drop('player_id',axis=1),width = '100%',
                               filters = True)



app = App(app_ui,server)