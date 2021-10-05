import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from pycountry_convert import country_alpha2_to_country_name
from geopy.geocoders import Nominatim

st.title('Dylan Ndengu\'s COVID Analysis App')

#date_column = 'Date_reported'
url_data = "https://covid19.who.int/WHO-COVID-19-global-table-data.csv"
data = pd.read_csv(url_data, index_col=False)
data = data[data["WHO Region"].notna()]
data = data[data["Cases - newly reported in last 7 days per 100000 population"]>0]


# Filter Widget

data = data.reset_index()
data = data.rename(columns={"Name":"Country"})
Country_options = data["Country"].drop_duplicates()
country_choice = st.sidebar.multiselect("Select your country/countries :", Country_options, "South Africa")

pcnt = lambda x : f"{x:.2%}"

def load_data(csv_path):
    data = pd.read_csv(csv_path)
    data = data.dropna()
    return data
    

def describe_data(dataframe):
    frame = pd.DataFrame(dataframe).groupby("Country")
    describe_frame = frame["Cases - newly reported in last 7 days per 100000 population"].max()
    describe_frame = describe_frame.dropna()
    return describe_frame

def death_vs_infection(dataset):
    deathvinfect = dataset["Deaths - newly reported in last 7 days per 100000 population"]/dataset["Cases - newly reported in last 7 days per 100000 population"]
    deathvinfect = pd.concat([dataset["Country"],deathvinfect], axis=1)
    deathvinfect = deathvinfect.rename(columns={"Name" : "Country", 0 : "Percentages of Infections Leading to Death"})
    deathvinfect = deathvinfect.dropna()
    deathvinfect["Percentages of Infections Leading to Death"] = deathvinfect["Percentages of Infections Leading to Death"]
    return deathvinfect
    

#Creates a text element to let the reader know data is loading
data_load_state = st.text('Loading Raw Data...')

#load the data
loaded_data = pd.read_csv(url_data,index_col=False)
loaded_data = loaded_data[loaded_data["Cases - newly reported in last 7 days per 100000 population"]>0]
st.subheader('Raw Data')
st.dataframe(loaded_data)

#Notify the user that the data was successfully loaded

data_load_state.text('Done Loading Raw Data!')


#Graph of COVID deaths per region
category_tr = data.groupby(by="WHO Region").sum()
category_tr = category_tr.reset_index()
category_tr=category_tr.sort_values("Cases - newly reported in last 7 days per 100000 population", ascending=False)
fig1 = px.bar(category_tr, x="Cases - newly reported in last 7 days per 100000 population", y="WHO Region", color="WHO Region")
fig1.update_layout(showlegend=False)
st.subheader("Cumulative Infections in the Past 7 Days Per 100 000")
st.plotly_chart(fig1)


#Description of Data

description_of_data = describe_data(data)
description_of_data = description_of_data[description_of_data!=0].sort_values(ascending=False)
st.subheader("Countries with the most Infected per 100 000 People in the past 7 Days")
st.table(description_of_data.head(10))

col1, col2 = st.columns(2)

with col1:
    st.subheader("Countries with the most deaths per 100 000 people in the past 7 Days")
    dfd = pd.DataFrame(data["Deaths - newly reported in last 7 days per 100000 population"])
    st.table(description_of_data.sort_values(ascending=False).head(5))


with col2:
    st.subheader("Countries with the least deaths per 100 000 people in the past 7 days")
    dfd = pd.DataFrame(data["Deaths - newly reported in last 7 days per 100000 population"])
    st.table(description_of_data.sort_values(ascending=True).head(5))

st.subheader("Deaths vs Infections")
death_infection = death_vs_infection(data)
death_infection_sorted = death_infection.sort_values(by=["Percentages of Infections Leading to Death"], ascending = False)
death_infection_sorted["Percentages of Infections Leading to Death"] = death_infection_sorted["Percentages of Infections Leading to Death"].map(pcnt)
death_infection_sorted=death_infection_sorted.head(10).reset_index(drop=True)
death_infection_sorted.index = np.arange(1, len(death_infection_sorted)+1)
st.table(death_infection_sorted)

#st.subheader("Raw Vaccination Data")
url_vaccine_data = "https://covid19.who.int/who-data/vaccination-data.csv"
vaccine_data = load_data(url_vaccine_data)
#st.dataframe(vaccine_data)

st.subheader("Most Vaccinated Countries")
variable_list = ["COUNTRY","TOTAL_VACCINATIONS_PER100","PERSONS_VACCINATED_1PLUS_DOSE_PER100","PERSONS_FULLY_VACCINATED_PER100"]
mv_countries = vaccine_data[variable_list].sort_values(by="TOTAL_VACCINATIONS_PER100", ascending=False).head(10)
mv_countries=mv_countries.reset_index(drop=True)
mv_countries.index = np.arange(1, len(mv_countries)+1)
st.dataframe(mv_countries)

st.subheader("Country-Specific Statistics")

cnt_vac_variables = vaccine_data[vaccine_data['COUNTRY'].isin(country_choice)].sort_values(by="COUNTRY").reset_index(drop=True)
cnt_inf_variables = data[data["Country"].isin(country_choice)].sort_values(by="Country").reset_index(drop=True)
cnt_dr_variables = death_infection[death_infection["Country"].isin(country_choice)].sort_values(by="Country").reset_index(drop=True)

cnt_data_table = pd.concat([cnt_inf_variables["Country"],cnt_inf_variables["Cases - newly reported in last 7 days per 100000 population"],
cnt_dr_variables["Percentages of Infections Leading to Death"].map(pcnt),cnt_vac_variables["PERSONS_FULLY_VACCINATED_PER100"],
 cnt_vac_variables["VACCINES_USED"]],axis=1)

cnt_data_table = cnt_data_table.rename(columns={"Country" : "Country", "Cases - newly reported in last 7 days per 100000 population": "New Cases per 100K",
"Percentages of Infections Leading to Death" : "Death Rate", "PERSONS_FULLY_VACCINATED_PER100" : "Fully Vaccinated / 100K", "VACCINES_USED" : "Vaccines Used"})

cnt_data_table = cnt_data_table.sort_values(by="New Cases per 100K", ascending=False).reset_index(drop=True)

st.table(cnt_data_table)

url_country_code = "https://covid19.who.int/WHO-COVID-19-global-data.csv"
var_code_list = ["Country","Country_code"]
country_code_data = pd.read_csv(url_country_code, index_col=False)
country_code_data = country_code_data.drop_duplicates(subset="Country")[var_code_list]
combined_table = data.merge(country_code_data, how="left", on="Country")


@st.cache
def get_countryname(code):
        try:
            country_name = country_alpha2_to_country_name(code)      
        except:
            country_name = "Unknown"
        return country_name


combined_table["CountryNames"] = combined_table["Country_code"].map(get_countryname)
combined_table = combined_table.drop(columns="index")


geolocator = Nominatim(user_agent="COVID_analysis4")
def geolocate(country):
    try:
        # Geolocate the center of the country
        loc = geolocator.geocode(country)
        # And return latitude and longitude
        return float(loc.latitude) , float(loc.longitude)
    except:
        # Return missing value
        return np.nan


st.subheader("Dataset with country code")
dropped_countries = ["Unknown","Holy See (Vatican City State)","Korea, Democratic People's Republic of", "Palestine, State of","Georgia"]


located_countries = combined_table

for country in dropped_countries:
    located_countries = located_countries[~located_countries["CountryNames"].isin([country])]

print(located_countries.shape)

located_countries = located_countries.reset_index(drop=True)
st.dataframe(located_countries)

located_countries["Latitude"] = ""
located_countries["Longitude"] = ""

country_list = list(located_countries["CountryNames"])

i=0
for countryname in country_list:
    lat, lon = geolocate(countryname)
    located_countries["Latitude"][i] = lat
    located_countries["Longitude"][i] = lon
    i+=1


#empty map
world_map= folium.Map(tiles="cartodbpositron")
marker_cluster = MarkerCluster().add_to(world_map)
#for each coordinate, create circlemarker of user percent
for i in range(len(located_countries)):
        lat = located_countries.iloc[i]['Latitude']
        long = located_countries.iloc[i]['Longitude']
        radius=4
        popup_text = """Country : {}<br>
                     New Cases : {}<br>
                     New Deaths : {}<br>"""
        popup_text = popup_text.format(located_countries.iloc[i]['CountryNames'],
                                   located_countries.iloc[i]['Cases - newly reported in last 7 days'],
                                   located_countries.iloc[i]['Deaths - newly reported in last 7 days']
                                   )
        folium.Marker(location = [lat, long], radius=radius, popup= popup_text, fill =True, prefer_canvas=True).add_to(marker_cluster)
#show the map
st.subheader("New Cases and Deaths In The Past 7 Days")
st.write(world_map)