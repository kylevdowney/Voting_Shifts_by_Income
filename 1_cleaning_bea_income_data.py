import geopandas
import numpy as np
import pandas as pd
import io
import zipfile
import csv

#%%
# import Bureay of Economic Analysis Data and clean it up so it can be later
#joined together with the shapefile and voting data ana analyzed

fix_dtype = {"Median Income" : int, 
             "FIPS": str, 
             "GeoFIPS" : str, #note GeoFIPS not GEOID
             "GEOID" : str,
             "year" : str, 
             "party" : str, 
             "state_po" : str}


bea_data = pd.read_csv("CAINC1__ALL_AREAS_1969_2019.csv", dtype = fix_dtype)

income_rows = bea_data.query("Description == 'Per capita personal income (dollars) 2/'")
bea_data_trim = income_rows[["GeoFIPS",
                             "GeoName",
                             "Description",                              
                             "2000",
                             "2004",
                             "2008",
                             "2012",
                             "2016"]].copy()

newnames = {'Per capita personal income (dollars) 2/' : "Average Income",
            "GeoFIPS" : "GEOID"}

bea_data_trim = bea_data_trim.rename(newnames, axis = "columns")
for i, col in enumerate(bea_data_trim.columns):
    bea_data_trim.iloc[:, i] = bea_data_trim.iloc[:, i].str.replace('"', '')
    bea_data_trim.iloc[:, i] = bea_data_trim.iloc[:, i].str.replace(' ', '')

#counties_all = geopandas.read_file("tl_2016_us_county.shp", dtype = fix_dtype)
#counties = counties_all.query("STATEFP != '02' and STATEFP != '15'")
#counties["GEOID"] = counties["GEOID"].astype(str)

#%% The data comes spread out horizontally with a different column for each
#year, break it into five pieces which can later be stacked vertically on top
# of each other

#This dictionary will be used to turn the five seperate columns into a column
#with one common name which will later be stacked on top of each other

changing_columns = {"2000" : "Per_Capita_Income",
                    "2004" : "Per_Capita_Income",
                    "2008" : "Per_Capita_Income",
                    "2012" : "Per_Capita_Income",
                    "2016" : "Per_Capita_Income"
                    }

#%%
#2000

#create dataframe
year2000_income = bea_data_trim[["GEOID",
                              "GeoName",
                              "Description",
                              "2000"]].copy()
year2000_income = year2000_income.rename(changing_columns, axis = "columns")
year2000_income["year"] = "2000"


#%%
#2004

#create dataframe
year2004_income = bea_data_trim[["GEOID",
                              "GeoName",
                              "Description",
                              "2004"]].copy()
year2004_income = year2004_income.rename(changing_columns, axis = "columns")
year2004_income["year"] = "2004"


#%%
#2008

#create dataframe

year2008_income = bea_data_trim[["GEOID",
                              "GeoName",
                              "Description",
                              "2008"]].copy()
year2008_income = year2008_income.rename(changing_columns, axis = "columns")
year2008_income["year"] = "2008"


#%%
#2012

#create dataframe

year2012_income = bea_data_trim[["GEOID",
                              "GeoName",
                              "Description",
                              "2012"]].copy()
year2012_income = year2012_income.rename(changing_columns, axis = "columns")
year2012_income["year"] = "2012"


#%%
#2016

year2016_income = bea_data_trim[["GEOID",
                              "GeoName",
                              "Description",
                              "2016"]].copy()
year2016_income = year2016_income.rename(changing_columns, axis = "columns")
year2016_income["year"] = "2016"


#%%
#build into one df, with the years and income columns stacked vertically on
#top of each other.
#Watch out for the leading space in front of GEOID, wash that out or it'll
#get in the way of the merges later

five_elections = [year2000_income, year2004_income, year2008_income, year2012_income, year2016_income]
stacked_data = pd.concat(five_elections).reset_index(drop=True)
for i, col in enumerate(stacked_data.columns):
    stacked_data.iloc[:, i] = stacked_data.iloc[:, i].str.replace(' ', '')

cleaned_data = stacked_data.query("Per_Capita_Income != '(NA)'")
tidied_up_data = cleaned_data.query("GeoName != 'United States'")
tidied_up_data.to_csv("per_capita_income_2000-2016.csv")

#%%