import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px


from datetime import datetime as dt
import json
import numpy as np
import pandas as pd
import os
from geopy.geocoders import Nominatim
import folium
import geopandas
import branca

# Recall app
from app import app
from data_fetch import get_views

def create_map():
    '''
    This functions creates the map off Colombia where the company has stores.
    params:
        none
    returns:
        creates an html for Colombia where each city has information about
        customers purchase frecuency
    '''
	
	df_for_map = get_views.get_view_by_name('tiendas_frecuencia')
	df_for_map["Radio_for_map"]=((df_for_map["valor_neto"])/df_for_map["valor_neto"].mean())*10+5

	# Create the map:
	m_prueba = folium.Map(location=[6.461508, -75.000000],max_zoom=18, zoom_start=6, tiles="cartodbpositron")

	circle="""
	<svg version='1.1' xmlns='http://www.w3.org/2000/svg'
		width='25' height='25' viewBox='0 0 120 120'>
	<circle cx='60' cy='60' r='50'
			fill={} />
	</svg>
	"""

	group1=folium.FeatureGroup(name=circle.format('#FF0000')+"<FONT SIZE=2>Freq. [1,1.25]</font>  ")
	m_prueba.add_child(group1)

	group2=folium.FeatureGroup(name=circle.format('#FF7070')+"<FONT SIZE=2>Freq. [1.25,1.35]</font>", show=False)
	m_prueba.add_child(group2)

	group3=folium.FeatureGroup(name=circle.format('#FF6B22')+"<FONT SIZE=2>Freq. [1.35,1.5]</font>" , show=False)
	m_prueba.add_child(group3)

	group4=folium.FeatureGroup(name=circle.format('#0FFB0E')+"<FONT SIZE=2>Freq. [1.5,1.8]</font>", show=False)
	m_prueba.add_child(group4)

	group5=folium.FeatureGroup(name=circle.format('#019F00')+"<FONT SIZE=2>Freq. > 1.8</font>", show=False)
	m_prueba.add_child(group5)

	for i in range(df_for_map.shape[0]):
		
		sales=round(df_for_map.loc[i,"valor_neto"]/1000000,1)
		sales=f"${sales}M"
		
		html_ = """
		<h2 style="margin-bottom:-10"; align="center">{}</h2>""".format(df_for_map.loc[i,'punto_venta']) + """ <br>
		<b>Total ventas (1 año):</b> {}""".format(sales) + """ <br/>
		<b>Frec. de venta (1 año):</b> {}""".format(round(df_for_map.loc[i,'frequency'],4)) + """ <br/>
		<b>Centro comercial:</b> {}""".format(df_for_map.loc[i,'centro_comercial']) + """ <br/>
		<b>Canal:</b> {}""".format(df_for_map.loc[i,'canal']) + """ <br/>
		<b>Codigo tienda:</b> {}""".format(df_for_map.loc[i,'codigo_tienda']) + """ <br/>
		<b>IDGEO:</b> {}""".format(df_for_map.loc[i,'id_geo'])

		iframe = branca.element.IFrame(html=html_, width=300, height=250)
		popup = folium.Popup(iframe, max_width=305, parse_html=True)

		if (df_for_map.loc[i,"frequency"] > 1) & (df_for_map.loc[i,"frequency"] <= 1.25):
			folium.CircleMarker(radius=df_for_map.loc[i,"Radio_for_map"], 
						location=[df_for_map.loc[i,"latitude"],df_for_map.loc[i,"longitude"]],
						popup=popup,
								color="black",fill=True,fill_color="#FF0000",weight=1,
								fill_opacity=0.7,
						tooltip=f"<FONT SIZE=4><b>Ventas</b>:{sales}</font>").add_to(group1)
		
		elif (df_for_map.loc[i,"frequency"] > 1.25) & (df_for_map.loc[i,"frequency"] <= 1.35):
			folium.CircleMarker(radius=df_for_map.loc[i,"Radio_for_map"], 
						location=[df_for_map.loc[i,"latitude"],df_for_map.loc[i,"longitude"]],
						popup=popup,color="black",fill=True,fill_color="#FF7070",weight=1,
								fill_opacity=0.7,
						tooltip=f"<FONT SIZE=4><b>Ventas</b>:{sales}</font>").add_to(group2)
			
		elif (df_for_map.loc[i,"frequency"] > 1.35) & (df_for_map.loc[i,"frequency"] <= 1.5):
			folium.CircleMarker(radius=df_for_map.loc[i,"Radio_for_map"], 
						location=[df_for_map.loc[i,"latitude"],df_for_map.loc[i,"longitude"]],
						popup=popup,color="black",fill=True,fill_color="#FF6B22",weight=1,
								fill_opacity=0.8,
						tooltip=f"<FONT SIZE=4><b>Ventas</b>:{sales}</font>").add_to(group3)
		
		elif (df_for_map.loc[i,"frequency"] > 1.5) & (df_for_map.loc[i,"frequency"] <= 1.8):
			folium.CircleMarker(radius=df_for_map.loc[i,"Radio_for_map"], 
						location=[df_for_map.loc[i,"latitude"],df_for_map.loc[i,"longitude"]],
						popup=popup,color="black",fill=True,fill_color="#8EFF94",weight=1,
								fill_opacity=0.8,
						tooltip=f"<FONT SIZE=4><b>Ventas</b>:{sales}</font>").add_to(group4)
		else:
			folium.CircleMarker(radius=df_for_map.loc[i,"Radio_for_map"], 
						location=[df_for_map.loc[i,"latitude"],df_for_map.loc[i,"longitude"]],
						popup=popup,color="black",fill=True,fill_color="#2B9A00",weight=1,
								fill_opacity=0.8,
						tooltip=f"<FONT SIZE=4><b>Ventas</b>:{sales}</font>").add_to(group5)
			
	folium.LayerControl(collapsed=False).add_to(m_prueba)
	m_prueba.save('maps/Colombia_map.html')
	##############################
	# Map Layout
	##############################
	map = html.Div(
	    [
			html.H5("Sales frequency and amount per store"),
			html.P("Full Country"),
	        # Place the main graph component here:
	        html.Iframe(srcDoc = open('maps/Colombia_map.html','r').read()
	        	, id="COL_map",width='100%',height=526)
	    ],
	    #className="ds4a-body",
	)

	return map
