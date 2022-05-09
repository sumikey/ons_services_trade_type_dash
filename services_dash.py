 #------------------------- IMPORT PACKAGES USED
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

#------------------------- DATA LOADING & PREPROCESSING

df = pd.read_csv('service_trade.csv')

# subset for quarterly only, drop annual data
dfq = df[['Direction', 'Service type code', 'Service type', 'Country code','Country', 
       '2016Q1', '2016Q2', '2016Q3', '2016Q4', '2017Q1', '2017Q2', '2017Q3', '2017Q4',
       '2018Q1', '2018Q2', '2018Q3', '2018Q4', '2019Q1', '2019Q2', '2019Q3',
       '2019Q4', '2020Q1', '2020Q2', '2020Q3', '2020Q4', '2021Q1', '2021Q2',
       '2021Q3', '2021Q4']]

# create a column of first digits only
dfq['type_code_1dig'] = [x.split('.')[0] for x in list(dfq['Service type code'])]

# create a column of codes + descriptions
dfq['code_desc'] = [ (x+': '+y) for x,y in zip(dfq['Service type code'], dfq['Service type']) ]

# reorder to put new columns where want them
dfq = dfq[['Direction', 'code_desc', 'Service type code', 'type_code_1dig', 'Service type', 'Country code','Country', 
       '2016Q1', '2016Q2', '2016Q3', '2016Q4', '2017Q1', '2017Q2', '2017Q3', '2017Q4',
       '2018Q1', '2018Q2', '2018Q3', '2018Q4', '2019Q1', '2019Q2', '2019Q3',
       '2019Q4', '2020Q1', '2020Q2', '2020Q3', '2020Q4', '2021Q1', '2021Q2',
       '2021Q3', '2021Q4']]

# rename columns in better way
dfq.columns = ['direction', 'code_desc', 'code', 'code_1dig', 'type', 'country_code','country', 
       '2016Q1', '2016Q2', '2016Q3', '2016Q4', '2017Q1', '2017Q2', '2017Q3', '2017Q4',
       '2018Q1', '2018Q2', '2018Q3', '2018Q4', '2019Q1', '2019Q2', '2019Q3',
       '2019Q4', '2020Q1', '2020Q2', '2020Q3', '2020Q4', '2021Q1', '2021Q2',
       '2021Q3', '2021Q4']

#------------------------- TITLE AND BASIC PAGE INTRO

# make a title & Intro section
st.title('UK Services Trade by Type and Partner')
st.write('---')
st.write("""This dashboard analyses the UK's services trade by services trade type and partner,
based on data from the UK's [Office for National Statistics](https://www.ons.gov.uk/businessindustryandtrade/internationaltrade/datasets/uktradeinservicesservicetypebypartnercountrynonseasonallyadjusted).
This dataset is not seasonally-adjusted. All data is published in GBP Millions""" )

#------------------------- SECTION FOR CHOOSING PARAMETERS TO ANALYSE

# make a subheader for next section
st.write('---')
st.subheader('Analysing services trade of a single type with a chosen partner') 
st.write("""Choose the type of services trade you wish to analyse, your preferred partner
and whether you wish to examine exports or imports. This selection will display the value
of trade for the given quarter and year-on-year growth expressed in both % and absolute GBP terms.""")

# create lists of codes_descriptions, countries and flow types
# to use in streamlit select boxes
list_codes_desc = list(dfq.code_desc.unique())
list_countries = list(dfq.country.unique())
list_flows = list(dfq.direction.unique())

# add three select boxes in line (i.e. not in sidebar)
# use our created lists of unique values
service = st.selectbox('Which services type do you want to analyse?', list_codes_desc)
partner = st.selectbox('Which trade partner do you want to analyse?', list_countries)
flow = st.selectbox('Which trade flow do you want to analyse?', list_flows)

#------------------------- FILTER OUR DF BY OUR SELECTBOX CHOICES

# filter df by our selections
df_plot = dfq
df_plot = df_plot[df_plot['direction'] == flow]
df_plot = df_plot[df_plot['country'] == partner]
df_plot = df_plot[df_plot['code_desc'] == service]

#------------------------- PREPROCESS DATA SO CAN PLOT

# remove unncessary columns and transpose
df_plot = (df_plot
           .iloc[:,7:] # remove columns
           .T)         # transpose

# fix datetime index
new_index = [x[0:4]+''+x[4:] for x in df_plot.index] # create a new list of index terms with hyphens between year and quarter
df_plot.index = new_index  # set as the index
df_plot.index = pd.to_datetime(df_plot.index) # convert to datetime
df_plot.index = df_plot.index + pd.offsets.QuarterEnd(0) # add offsets to the end of relevant quarter
df_plot.loc['2016-01-01'] = '' # add an extra empty
df_plot.index = pd.to_datetime(df_plot.index) # convert to datetime again so new empty row converted
df_plot.sort_index(inplace=True)

# convert the single column to numeric, was previously an object
# coerce errors (into NaNs) for those non-disclosed values
# NaNs leaves empty space on chart - more informative than zero
df_plot.iloc[:,0] = pd.to_numeric(df_plot.iloc[:,0], errors='coerce')

# remove the column name as only plotting single value
df_plot.columns = ['']

# create a to/from depending on if exports or imports
word_to_from = 'to' if flow == 'Exports' else 'from'

#------------------------- CREATE PLOT TITLE & PLOT

# write out title based on all our variables
st.write(f"UK {flow} of '{service}' {word_to_from} {partner}, Quarterly, GBP Millions")
# create a line plot of our selected data
st.line_chart(df_plot)

#------------------------- CREATE PLOT OF YOY DIFF

# write out title based on all our variables
st.write(f"UK {flow} of '{service}' {word_to_from} {partner}, Quarterly, change yoy in GBP Millions")
# create a line plot of our selected data
st.line_chart(df_plot.diff(4))

#------------------------- CREATE PLOT OF % CHANGE YOY

# write out title based on all our variables
st.write(f"UK {flow} of '{service}' {word_to_from} {partner}, Quarterly, GBP Millions, % change yoy")
# create a line plot of our selected data
st.line_chart(df_plot.pct_change(4, fill_method=None).mul(100))


#------------------------- SECTION FOR COMPARING EXPORTS TO SEVERAL CHOSEN PARTNERS

# make a subheader for next section
st.write('---')
st.subheader('Comparing services trade of the same types with additional partners')
st.write("""This section will allow you to compare the same metrics as the previous section
but against additional partners. Add additional trade partners into the selection box for
them to be added to the charts""")

# add three select boxes in line (i.e. not in sidebar)
# use our created lists of unique values
#service2 = st.selectbox('Which services type do you want to analyse?', list_codes_desc)
partners2 = st.multiselect(f'Which trade partners do you want to compare trade with {partner} to?', list_countries, default=[partner])
#flow2 = st.selectbox('Which trade flow do you want to analyse?', list_flows)

#------------------------- FILTERING A NEW DATAFRAME BASED ON SELECTIONS

# filter df by our original selections
df_plot2 = dfq
df_plot2 = df_plot2[df_plot2['direction'] == flow]
df_plot2 = df_plot2[df_plot2['code_desc'] == service]

# and filter for countries in our list using a boolean condition
boolean_series = df_plot2.country.isin(partners2)
df_plot2 = df_plot2[boolean_series]

#------------------------- PREPROCESSING THIS NEW DATAFRAME

# remove unncessary columns and transpose
df_plot2 = (df_plot2
           .iloc[:,7:] # remove columns
           .T)         # transpose

# fix datetime index
# and add row 01 Jan 2016 so that plots display years
new_index2 = [x[0:4]+''+x[4:] for x in df_plot2.index] # create a new list of index terms with hyphens between year and quarter
df_plot2.index = new_index2  # set as the index
df_plot2.index = pd.to_datetime(df_plot2.index) # convert to datetime
df_plot2.index = df_plot2.index + pd.offsets.QuarterEnd(0) # add offsets to the end of relevant quarter
df_plot2.loc['2016-01-01'] = [None for _ in range(len(df_plot2.columns))] # add nones, length dynamic based on no. partners selected
df_plot2.index = pd.to_datetime(df_plot2.index) # convert to datetime again so new empty row converted
df_plot2.sort_index(inplace=True)

# convert the names into our country names
df_plot2.columns = partners2

# convert the single column to numeric, was previously an object
# coerce errors (into NaNs) for those non-disclosed values
# NaNs leaves empty space on chart - less misleading than zero
for col in df_plot2.columns:
    df_plot2[col] = pd.to_numeric(df_plot2[col], errors='coerce')

# write out title based on all our variables
st.write(f"UK {flow} of '{service}' {word_to_from} {partner} and selected comparitors, Quarterly, GBP Millions")
# plot absolute values
st.line_chart(df_plot2)

# write out title based on all our variables
st.write(f"UK {flow} of '{service}' {word_to_from} {partner} and selected comparitors, Quarterly, change yoy in GBP Millions")
# create a line plot of our selected data
st.line_chart(df_plot2.diff(4))

# write out title based on all our variables
st.write(f"UK {flow} of '{service}' {word_to_from} {partner} and selected comparitors, Quarterly, % change yoy")
# create a line plot of our selected data
st.line_chart(df_plot2.pct_change(4, fill_method=None).mul(100))

#------------------------- PLOTLY TREEMAP OF EXPORTS TO PARTNER AS SHARE OF WORLD

st.write('---')

# create a list of only countries - no aggregates
list_countries = list(dfq.country.unique())
list_countries.remove('Total EU27') # operating on list, so remove in place
list_countries.remove('Rest of World')
list_countries.remove('World total')

# basic preprocessing
df_plotly = dfq
df_plotly = df_plotly[df_plotly['direction'] == flow] # subset for flow
df_plotly = df_plotly[df_plotly['code_desc'] == service] # subset for service
df_plotly = df_plotly.iloc[:,6:] # remove unwanted columns

# filter so that only
boolean_series_plotly = df_plotly.country.isin(list_countries)
df_plotly = df_plotly[boolean_series_plotly]

# create a slider for the rolling value
rol_val = st.slider('Rolling over how many quarters?', min_value=1, max_value=4)

# set country as index ahead of numeric conversion
# get it out of the way
df_plotly.set_index('country', inplace=True)

# convert each column to numeric
# choose errors coerce which leaves errors as NaN
for col in df_plotly.columns[:]:
    df_plotly[col] = pd.to_numeric(df_plotly[col], errors='coerce')

# adding a rolling factor based upon chosen rolling slider
# transpose, roll and sum and transpose back
df_plotly = (df_plotly.T.rolling(rol_val).sum().T)

# reset the index so that country comes back as column
# add ca be used in the plotly chart
df_plotly.reset_index(inplace=True)

# set a list of options for the treemap to roll through to
through_to_list = list(df_plotly.columns[1:])

# # select box to quarter we are rolling through to
through_to = st.selectbox('Rolling through to which quarter?', 
                          options= through_to_list, 
                          index= len(through_to_list)-1  # cannot enter -1 directly
                         )

# create a plotly figure, path as country and values based on the last column
fig = px.treemap(df_plotly, path=['country'],
                  values='2021Q4')

# add a title that morphs based upon context
st.write(f"UK {flow} of '{service}' {word_to_from} {partner} in context of global {flow}, for {rol_val} quarters through to {through_to[-2:]} {through_to[:-2]}, GBP Millions")

# use streamlit to display the plotly chart
st.plotly_chart(fig, use_container_width=True)
