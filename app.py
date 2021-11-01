# Import necessary packages
import numpy as np
import pandas as pd
import datetime
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
import os
import plotly.express as px
import streamlit.components.v1 as components

image_directory = "logo.png"
image = Image.open(image_directory)
st.set_page_config(layout="wide",
                   page_title="Omdena France Chapter - Flu Dashboard",
                   page_icon= image,
                   menu_items={
                    'Get Help': 'https://omdena.com/omdena-chapter-page-france/',
                    'Report a bug': "https://www.linkedin.com/in/murugesh-manthiramoorthi/",
                    'About': "The dashboad is developed as a part of the *Building a Tracking dashboard for Flu* project initiated by Omdena France Chapter. More than x people from diffrent countries colloborated in the project which aims to create public awareness about the situation of Flu in France"
                        }
)
padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

# Title and description
t1, t2 = st.columns((0.1,1))

t1.image(image, width = 120)
t2.title("Flu in France Dashboard - Omdena France Chapter")
t2.markdown("The aim of the tool is to inform people about public health and best practices in a simple way. It will also reveal the severity of influenza compared to Covid.")


# Metrics
m1, m2, m3= st.columns((1,1,1))
st.markdown("""
<style>
.big-font {
    font-size:300px !important;
}
</style>
""", unsafe_allow_html=True)
# m1.write('')
m1.metric(label ='Total cases in 2020',value = str(round(2260712/1000000,2)) + 'M', delta = str("1.49")+' % higher compared to 2019', delta_color = 'inverse')
m2.metric(label ='Most affected age group',value = "0 - 4", delta = 'Followed by 5-14', delta_color = 'inverse')
m3.metric(label ='Most affected region',value = "Auvergne-Rhône-Alpes", delta = 'Followed by Bretagne', delta_color = 'inverse')
# m1.write('')

# First row of chart
period = st.sidebar.radio("Choose the rate of increase of time:", ('weekly','monthly',"yearly"), )
if period=="weekly":
    c1, c2 = st.columns((1, 1))

    inc_fr = pd.read_csv("incidence_france.csv", index_col=0, infer_datetime_format=True)
    inc_fr['week'] = inc_fr['week'].astype(str)
    inc_fr['week'] = inc_fr['week'].apply(lambda x: datetime.datetime.strptime(x + '-1', "%Y%W-%w"))

    fig = px.line(inc_fr, x="week", y=inc_fr.inc100,
                  hover_data={"week": "|%W-%Y",'inc100_up':True,'inc100_low':True},
                  title='Incidence rate of influenza in France from start of surveillance')
    fig.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')

    df2 = pd.read_csv("ConsultationCleaned.csv")
    df2['YearWeek'] = df2['YearWeek'].astype(str)
    df2['YearWeek'] = df2['YearWeek'].apply(lambda x: datetime.datetime.strptime(x.replace('-W', '') + '0', "%Y%W%w"))
    fig4 = px.line(df2, x='YearWeek', y=['00-04a','05-14a', '15-64a', '65+a'], labels= ["0-4", "5-14", "15-64", "65"],
                   title="Incidence rate of influenza in France per age group", )
    fig4.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')
    newnames = {'00-04a':'0-4 yrs', '05-14a': '5-14 yrs', '15-64a': '15-64 yrs', '65+a': "> 65 yrs"}
    fig4.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                          legendgroup = newnames[t.name],
                                          hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))
    fig4.update_layout(legend_title_text='Age group')

    c1.plotly_chart(fig, use_container_width=True)
    c2.plotly_chart(fig4, use_container_width=True)

    # Second row of charts
    inc_reg = pd.read_csv('./incidence_regionally.csv')
    inc_reg['week'] = inc_reg['week'].astype(str)
    inc_reg['week'] = inc_reg['week'].apply(lambda x: datetime.datetime.strptime(x + '-1', "%Y%W-%w"))
    inc_reg['geo_name'] = inc_reg['geo_name'].apply(lambda x: x.title())
    regions = inc_reg['geo_name'].unique().tolist()
    reg = st.selectbox('Select the department you want to view.', regions)
    if reg:
        df = inc_reg[inc_reg['geo_name']==reg]
        fig2 = px.line(df, x="week", y=df.inc100,
                  hover_data={"week": "|%W-%Y",'inc100_up':True,'inc100_low':True}, height=600,
                  title='Incidence rate of influenza in '+'"'+reg+'"'+ ' region from start of surveillance')
        fig2.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')

    st.plotly_chart(fig2, use_container_width=True)

elif period == "monthly":
    c1, c2 = st.columns((1, 1))

    inc_fr = pd.read_csv("incidence_france.csv", index_col=0, infer_datetime_format=True)
    inc_fr['week'] = inc_fr['week'].astype(str)
    inc_fr['week'] = inc_fr['week'].apply(lambda x: datetime.datetime.strptime(x + '-1', "%Y%W-%w"))
    df_req1 = inc_fr[["week", "inc100"]]
    df_req1 = df_req1.set_index("week")
    df_req1.index = pd.to_datetime(df_req1.index)
    df_req1 = df_req1.groupby(pd.Grouper(freq='M')).sum()

    fig = px.line(x=df_req1.index, y=df_req1.inc100,
                  title='Incidence rate of influenza in France from start of surveillance')
    fig.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')

    df2 = pd.read_csv("ConsultationCleaned.csv")
    df2['YearWeek'] = df2['YearWeek'].astype(str)
    df2['YearWeek'] = df2['YearWeek'].apply(lambda x: datetime.datetime.strptime(x.replace('-W', '') + '0', "%Y%W%w"))
    df_req2 = df2[["YearWeek", '00-04a', '05-14a', '15-64a', '65+a']]
    df_req2 = df_req2.set_index("YearWeek")
    df_req2.index = pd.to_datetime(df_req2.index)
    df_req2 = df_req2.groupby(pd.Grouper(freq='M')).sum()

    fig4 = px.line(df_req2, x=df_req2.index, y=['00-04a', '05-14a', '15-64a', '65+a'], labels=["0-4", "5-14", "15-64", "65"],
                   title="Incidence rate of influenza in France per age group", )
    fig4.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')
    newnames = {'00-04a': '0-4 yrs', '05-14a': '5-14 yrs', '15-64a': '15-64 yrs', '65+a': "> 65 yrs"}
    fig4.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                           legendgroup=newnames[t.name],
                                           hovertemplate=t.hovertemplate.replace(t.name, newnames[t.name])))
    fig4.update_layout(legend_title_text='Age group')

    c1.plotly_chart(fig, use_container_width=True)
    c2.plotly_chart(fig4, use_container_width=True)

    # Second row of charts
    inc_reg = pd.read_csv('./incidence_regionally.csv')
    inc_reg['week'] = inc_reg['week'].astype(str)
    inc_reg['week'] = inc_reg['week'].apply(lambda x: datetime.datetime.strptime(x + '-1', "%Y%W-%w"))
    inc_reg['geo_name'] = inc_reg['geo_name'].apply(lambda x: x.title())
    regions = inc_reg['geo_name'].unique().tolist()
    reg = st.selectbox('Select the department you want to view.', regions)
    if reg:
        df = inc_reg[inc_reg['geo_name'] == reg]
        df_req3 = df[["week", "inc100"]]
        df_req3 = df_req3.set_index("week")
        df_req3.index = pd.to_datetime(df_req3.index)
        df_req3 = df_req3.groupby(pd.Grouper(freq='M')).sum()
        print(df.head())
        fig2 = px.line(df_req3, x=df_req3.index, y=df_req3.inc100,
                       height=600,
                       title='Incidence rate of influenza in ' + '"' + reg + '"' + ' region from start of surveillance')
        fig2.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')

    st.plotly_chart(fig2, use_container_width=True)

elif period == "yearly":
    c1, c2 = st.columns((1, 1))

    inc_fr = pd.read_csv("incidence_france.csv", index_col=0, infer_datetime_format=True)
    inc_fr['week'] = inc_fr['week'].astype(str)
    inc_fr['week'] = inc_fr['week'].apply(lambda x: datetime.datetime.strptime(x + '-1', "%Y%W-%w"))
    df_req1 = inc_fr[["week", "inc100"]]
    df_req1 = df_req1.set_index("week")
    df_req1.index = pd.to_datetime(df_req1.index)
    df_req1 = df_req1.groupby(pd.Grouper(freq='Y')).sum()

    fig = px.line(x=df_req1.index, y=df_req1.inc100,
                  title='Incidence rate of influenza in France from start of surveillance')
    fig.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')

    df2 = pd.read_csv("ConsultationCleaned.csv")
    df2['YearWeek'] = df2['YearWeek'].astype(str)
    df2['YearWeek'] = df2['YearWeek'].apply(lambda x: datetime.datetime.strptime(x.replace('-W', '') + '0', "%Y%W%w"))
    df_req2 = df2[["YearWeek", '00-04a', '05-14a', '15-64a', '65+a']]
    df_req2 = df_req2.set_index("YearWeek")
    df_req2.index = pd.to_datetime(df_req2.index)
    df_req2 = df_req2.groupby(pd.Grouper(freq='Y')).sum()

    fig4 = px.line(df_req2, x=df_req2.index, y=['00-04a', '05-14a', '15-64a', '65+a'], labels=["0-4", "5-14", "15-64", "65"],
                   title="Incidence rate of influenza in France per age group", )
    fig4.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')
    newnames = {'00-04a': '0-4 yrs', '05-14a': '5-14 yrs', '15-64a': '15-64 yrs', '65+a': "> 65 yrs"}
    fig4.for_each_trace(lambda t: t.update(name=newnames[t.name],
                                           legendgroup=newnames[t.name],
                                           hovertemplate=t.hovertemplate.replace(t.name, newnames[t.name])))
    fig4.update_layout(legend_title_text='Age group')

    c1.plotly_chart(fig, use_container_width=True)
    c2.plotly_chart(fig4, use_container_width=True)

    # Second row of charts
    inc_reg = pd.read_csv('./incidence_regionally.csv')
    inc_reg['week'] = inc_reg['week'].astype(str)
    inc_reg['week'] = inc_reg['week'].apply(lambda x: datetime.datetime.strptime(x + '-1', "%Y%W-%w"))
    inc_reg['geo_name'] = inc_reg['geo_name'].apply(lambda x: x.title())
    regions = inc_reg['geo_name'].unique().tolist()
    reg = st.selectbox('Select the department you want to view.', regions)
    if reg:
        df = inc_reg[inc_reg['geo_name'] == reg]
        df_req3 = df[["week", "inc100"]]
        df_req3 = df_req3.set_index("week")
        df_req3.index = pd.to_datetime(df_req3.index)
        df_req3 = df_req3.groupby(pd.Grouper(freq='Y')).sum()
        print(df.head())
        fig2 = px.line(df_req3, x=df_req3.index, y=df_req3.inc100,
                       height=600,
                       title='Incidence rate of influenza in ' + '"' + reg + '"' + ' region from start of surveillance')
        fig2.update_layout(xaxis_title="year", yaxis_title="rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')

    st.plotly_chart(fig2, use_container_width=True)

# Third row of chart
inc_reg["month"] = inc_reg["week"].dt.month
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
fig6 = px.bar(x=months, y=inc_reg.groupby(["month"])["inc100"].sum().values, title="Variation in cases over the months")
fig6.update_layout(xaxis_title="months", yaxis_title="sum of rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')
st.plotly_chart(fig6, use_container_width=True)

# Fourth row of chart
fig5 = px.bar(x=inc_reg.groupby(["geo_name"])["inc100"].sum().sort_values(ascending=False).index, y=inc_reg.groupby(["geo_name"])["inc100"].sum().sort_values(ascending=False).values, title="Most affected regions")
fig5.update_layout(xaxis_title="department", yaxis_title="sum of rate per 100K habitants", plot_bgcolor='rgb(255,255,255)')
st.plotly_chart(fig5, use_container_width=True)

# Fifth row of chart
sf = gpd.read_file('france-topo.json')
inc_reg['geo_name'].replace({'Ile-De-France': "Île-de-France", "Centre-Val-De-Loire": "Centre-Val de Loire",
                            'Auvergne-Rhone-Alpes':'Auvergne-Rhône-Alpes','Bourgogne-Franche-Comte':'Bourgogne-Franche-Comté',
                            'Pays-De-La-Loire':'Pays de la Loire','Provence-Alpes-Cote-D-Azur':"Provence-Alpes-Côte d'Azur",
                            'Hauts-De-France':'Hauts-de-France'}, inplace=True)
inc_reg['week'] = inc_reg['week'].astype(str)
inc_reg['year'] = pd.DatetimeIndex(inc_reg['week']).year
df =pd.DataFrame(inc_reg.groupby(['year','geo_name'])['inc100','inc100_low','inc100_up'].agg('sum').reset_index())
df['inc100_low'] = df['inc100_low'].astype(int)
df['inc100_up'] = df['inc100_up'].astype(int)
fig3 = px.choropleth_mapbox(data_frame=df,
                    geojson=sf,
                    locations='geo_name', # name of dataframe column
                    featureidkey='properties.nom',
                    hover_data={"year": "|%Y",'geo_name':True,'inc100_up':True,'inc100_low':True},# path to field in GeoJSON feature object with which to match the values passed in to locations
                    color='inc100',
                    animation_frame='year',
                    mapbox_style="carto-positron",
                    color_continuous_scale="Magma",
                    zoom=4,center = {"lat": 46.227638, "lon": 2.213749},
                    width=800, height=700)
fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.markdown("Incidence rate of influenza per region through years")
st.plotly_chart(fig3, use_container_width=True)

# components.html("<div class='tableauPlaceholder' id='viz1635350397970' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Fl&#47;FlunetTypeA_B&#47;Sheet1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='FlunetTypeA_B&#47;Sheet1' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Fl&#47;FlunetTypeA_B&#47;Sheet1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1635350397970');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>",
#                 height=600, width=1200)
# components.html("<div class='tableauPlaceholder' id='viz1635350480660' style='position: relative'><noscript><a href='#'><img alt=' ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Di&#47;DifferencesVis&#47;Sheet1&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='DifferencesVis&#47;Sheet1' /><param name='tabs' value='yes' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Di&#47;DifferencesVis&#47;Sheet1&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='en-US' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1635350480660');                    var vizElement = divElement.getElementsByTagName('object')[0];                    vizElement.style.width='100%';vizElement.style.height=(divElement.offsetWidth*0.75)+'px';                    var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>",
#                 height=600, width=1200)