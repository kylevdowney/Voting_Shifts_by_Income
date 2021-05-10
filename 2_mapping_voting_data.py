import geopandas
import numpy as np
import pandas as pd
import zipfile
from itertools import tee, islice, chain #, izip

#The shapefile is too large to include in the repository.  Download from:
#https://www.census.gov/cgi-bin/geo/shapefiles/index.php,
#Select Year "2016: -->  Select a Layer Type: "Counties (and equivalent)"
# --> download all counties for the US

#clean up the voting data into something useful which can then be joined
#with a map of counties and the cleaned up BEA data from script 1

fix_dtype = {"FIPS": str, 
             "GEOID" : str, 
             "year" : str, 
             "party" : str, 
             "state_po" : str,
             "income" : int}


election_results = pd.read_csv("countypres_2000-2016_(3).csv", dtype = fix_dtype)
new_key_name = {"FIPS" : "GEOID"}
election_results = election_results.rename(new_key_name, axis = "columns")
election_results['GEOID'] = election_results['GEOID'].astype(str)
election_results['GEOID'] = election_results['GEOID'].apply(lambda x: x.zfill(5))

#if you don't dropna() here then everywhere where Nader's votes are NA it will
#automatically give Nader's the real winner's votes and list him as the winner
election_results = election_results.dropna()

#crucial to use GEOID (originally FIPS) below here, sorting/grouping by county
#will drop every county with the same name except the first one alphabetically
election_results["vote_share"] = (election_results["candidatevotes"]/election_results["totalvotes"])*100
sorted_results = election_results.sort_values(["year", "GEOID", "candidatevotes"])
grouped = sorted_results.groupby(["year", "GEOID"])
the_winner_is = grouped.last()
the_winner_is = the_winner_is.reset_index()
the_winner_is = the_winner_is.drop(["state", "office", "totalvotes", "version"], axis = "columns")
contiguous_48 = the_winner_is.query("state_po != 'AK' and state_po != 'HI'")

contiguous_48.set_index("GEOID", inplace = True)


#%%
#merge voting and income into one big dataframe

income_by_counties = pd.read_csv("per_capita_income_2000-2016.csv", dtype = fix_dtype)
master_df = contiguous_48.merge(income_by_counties,
                              how = "inner",
                              on = ["GEOID", "year"],
                              validate = '1:1',
                              indicator = True)

print(master_df["_merge"].value_counts())
master_df = master_df.drop(["_merge"], axis = "columns")
master_df.set_index("GEOID", inplace = True)

#%%
#read in counties shapefile and break the master_df down into five
#dataframes that can be looped over to collect data on voting consistency

counties = geopandas.read_file("tl_2016_us_county.shp", dtype = fix_dtype)

#break the master dataframe into five pieces for editing and mapping, adjust
#the income for inflation to match 2021 dollars

year2000_election = master_df.query("year == '2000'").copy()
year2000_election["inflation adjusted income"] = year2000_election["income"] * 1.55


year2004_election = master_df.query("year == '2004'").copy()
year2004_election["inflation adjusted income"] = year2004_election["income"] * 1.41

year2008_election = master_df.query("year == '2008'").copy()
year2008_election["inflation adjusted income"] = year2008_election["income"] * 1.25

year2012_election = master_df.query("year == '2012'").copy()
year2012_election["inflation adjusted income"] = year2012_election["income"] * 1.15

year2016_election = master_df.query("year == '2016'").copy()
year2016_election["inflation adjusted income"] = year2016_election["income"] * 1.09
#year2016_election.set_index("GEOID", inplace = True)

#%%
#A little extra work to create a layer for consistency in voting across elections
elections = [year2000_election, year2004_election, year2008_election, year2012_election, year2016_election]

# Create a new series to contain the count for Republican victories
voting_consistency = pd.Series(index=year2016_election.index,data=0)
#This loop goes the list of elections and check whether the party column says 
#republican. Add the column of true (1) / false (0) values to the running total

for elec in elections:
    rep_won = elec["party"] == "republican"
    voting_consistency = voting_consistency + rep_won
    elec["voting_scale"] = voting_consistency

#While the bove adds the total to every df, year2016_electin is the only truly 
#useful one which will be mapped.  This is because it is the only one that 
#stores the count for ALL five elections
#Here we create a seperate column for each df equal to the 2016 scores so that
#each df contains the relevant info
for elec in elections:
    elec["swing_counties"] = year2016_election["voting_scale"]

#%%
#create a dataframe that tracks whether a county switched parties from the year
#before

winners = pd.DataFrame()
for elec in elections:
    yr = elec['year'].iloc[0]
    winners[yr] = elec['party']
winners = winners.sort_index(axis = "columns")
print(winners)

changes = pd.DataFrame()
last_yr = 0
for this_yr in winners.columns:
    if last_yr != 0:
        changes[this_yr] = winners[this_yr] != winners[last_yr]
    last_yr = this_yr
print( changes )        
print( winners[changes] )

#%%
#four map layers showing counties which switched party, using the df created
#in the previous cell

map_of_change = counties.merge(winners[changes],
                               how = "inner",
                               on = "GEOID",
                               validate = '1:1',
                               indicator = True)

print(map_of_change["_merge"].value_counts())
map_of_change = map_of_change.drop(["_merge"], axis = "columns")
map_of_change.reset_index()
map_of_change.copy()
change_in_2004 = map_of_change.drop(["2008", "2012", "2016"], axis = "columns")
change_in_2004.to_file("election_maps.gpkg", layer= "shifting_counties_2004", driver="GPKG")
change_in_2008 = map_of_change.drop(["2004", "2012", "2016"], axis = "columns")
change_in_2008.to_file("election_maps.gpkg", layer= "shifting_counties_2008", driver="GPKG")
change_in_2012 = map_of_change.drop(["2004", "2008", "2016"], axis = "columns")
change_in_2012.to_file("election_maps.gpkg", layer= "shifting_counties_2012", driver="GPKG")
change_in_2016 = map_of_change.drop(["2004", "2008", "2012"], axis = "columns")
change_in_2016.to_file("election_maps.gpkg", layer= "shifting_counties_2016", driver="GPKG")



#%%
#For the map showing voting consistency we need to use 2016 instead of the 
#other election dataframes because they will be missing data from every
#election that comes after them

election_2016_map = counties.merge(year2016_election,
                                   how = "inner",
                                   on = "GEOID",
                                   validate = '1:1',
                                   indicator = True)

print(election_2016_map["_merge"].value_counts())
election_2016_map = election_2016_map.drop(["_merge"], axis = "columns")
election_2016_map.reset_index()
election_2016_map.to_file("election_maps.gpkg", layer= "Voting_Consistency_Scale", driver="GPKG")
election_2016_map.to_file("election_maps.gpkg", layer= "Swing_Counties", driver="GPKG")


#%% Take the list of five dataframes with the new data on voting consistency
#and stack it back up to a final df

stack_it_back_up = pd.concat(elections).reset_index(drop=True)
stack_it_back_up.to_csv("final_df.csv")

#%%