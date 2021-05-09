Instructions for how to use the 3 python scripts and one QGISpackage in Voting_Shifts_by_income

A. cleaning_bea_income_data.py
-  This first script takes in data on personal income by data from the bureau
of Economic Analysis and cleans it so it can be joined in the other scripts to
voting data

1: Go to https://apps.bea.gov/regional/downloadzip.cfm and download "CAINC1:
Annual Personal Income by County."  Extract "CAINC1__ALL_AREAS_1969_2019" and
place in folder along with other scripts

2: Read in the BEA income data, making sure the datatypes are adjusted correctly

3:  There is numerous non-useful data so we start by trimming unhelpful
rows and dropping unhelpful columns

4: Rename the columns to make the income category more clear and so that GEOID can be used later on as join key to merge this dataframe onto a dataframe of voting records

5:  There is no problem with leading zeroes in the newly named GEOID column, but there is a problem with leading spaces, so be sure to eliminate those

6:  The problem with this data is that it's arranged horizontally.  There is
a separate column for each year with county income totals arranged underneath.
We want one clean column of income only running vertically, so break down
the dataframe into five pieces, one for each election.  

7.  Rename their respective year columns (["2000"], ["2004"], etc.) to "Per_Capita_Income."  This will be the common name when they are all stacked
back up

8.  Create a list of the five dataframes then use pd.concat to stack them up.

9.  Double check that leading zero was eliminated, for some reason it consistently seems to reappear

10.  Eliminate NA values with query and also drop the category for the entire United States

11.  Save the cleaned up dataframe to a csv which can be read in the next script.

B. mapping_data.py
 - This is the script with most of the real puzzle solving.  Here we read in the voting data and combine it with our cleaned up income data from the previous scripts.  We'll go on to break it back up into five pieces so we can run for loops on a list of the dataframes, gather info from each and plug it back into columns that will track whether a county switched from the previous election as well as their voting consistency for all five elections

1. For voting data, go to https://electionlab.mit.edu/data and download:
"County Presidential Election Returns 2000-2016"

2. For a baseline shapefile to join data on, go to https://www.census.gov/cgi-bin/geo/shapefiles/index.php --> Select Year: "2016" --> Select a Layer Type: "Counties (and equivalent)" --> download all counties for the US.

3. Read in the voting data from the MIT Election Data Lab, adjust the data types accordingly and rename ["FIPS"] to ["GEOID"]

4.  This file does not come with leading zeroes so be sure to use zfill(5) to fix
that

5.  It's crucial to clean this data in the order presented for the results to be accurate

6.  Use dropna() to get rid of any rows where there are no votes recorded for a candidate.  If you do not do this then Ralph Nader (for whom there are the most cells with no reliable vote counts) will automatically receive the number of votes from the actual winner and he will be listed as the winner instead.

7. Calculate vote_share by dividing each candidate's votes by the total votes.
This ended up not being used in this analysis but is a useful piece of data for future work that might assess the strength of party preference in each county.

8.  Use sort_values() --> groupby() --> last() to shrink the dataframe only to the rows with the candidates which received the largest number of votes for each election.  Be careful to groupby GEOID rather than county because grouping by county will eliminate any county name that is in multiple states except for the one that appears first alphabetically.

9.  Drop unhelpful columns and remove Alaska and Hawaii.  Because Alaska does not use counties it cannot be merged onto the counties shapefile, and this analysis makes more focused sense specifically tracking the 48 mainland states.

10.  Read in the cleaned up income csv created in the previous script and merge them by using ["GEOID"] as a join key.  

11. Read in the shapefile

12.  Break down the newly created master dataframe into five pieces, then put them in a list.

13.  Create a new series that will be used to track voting consistency

14.  Use a for loop to go through each of the five dataframes and track each time they voted Republican and add it to the running total.  The column for 2016 will have the final total of how many times a county voted Republican (5 = they voted republican 5 times, 0 = they voted Democrat 5 times)

15.  Add a new column to each dataframe equal to the 2016 voting consistency score.  This will make it easy to break counties apart later by whether they are "stable" (voted for the same party at least four times) or whether they are "swing" (voted for one party three times and another party two times)

16.  Use a new loop to create a dataframe that will track only whether a county switched from the previous year

17.  Merge that dataframe onto the counties shapefile, split it into five pieces for each election and save them as layers in a GIS package: elections.gpkg.  These will be used to visualize which counties switched party each election.

18. Merge the 2016 dataframe onto the counties later and save it to the same geopackage.  This will provide the layer for the voting consistency map which tracks how many times a county voted Republican

19. Copy and save the 2016 dataframe as a layer for swing counties

20. Use pf.concat() to stack the list of elections back up into one master dataframe.

21.  Save the master dataframe to a csv for analysis in the next script.

C. plotting_voting_by_income.py

Here is where we take the data cleaned and compiled in the previous two scripts and use it to create plots showing the relationship between income, voting and whether or not a county is "swing" or "stable"

1.  Read in the master csv from the previous script, adjusting data types accordingly.

2.  Break the master df into two halves: "swing counties," which voted for one party two out of five times and the other party three times, and "stable counties," which voted for the same party at least four out of five times.  Assign each a type "swing" or "stable" to later identify them.  Save each dataframe to a csv in case anyone wants to use them for a different future analysis.

3. Create a dictionary which will define the party colors used for the violin plots

4.  Create three split violin plots, one for the country as a whole, one for swing counties and one for stable counties.  For each violin plot, map income on the y axis, election year on the x axis and party as the hue.  This will create a series of plots that show the distribution of each income range that voted for one party or the other in each election.  Save all three plots.

5.  Put the swing counties and stable counties in a list then concatenate them back together (they now have ["type"] as unique marker under the same column)

6.  Create a line plot with year on the x axis, income on the y axis and "type" as the hue (which will create two separate lines, one for each type).  Save the results.

D.  election_maps.gpkg

1.  Open QGIS and add layer --> add vector layer --> select election_maps.gpkg from the Voting_Shifts_by_Income folder.

2:  For the layer "Voting_Consistency_Scale" go to symbology --> categorized --> voting scale.  QGIS does not have a preset color scale we want, so for the colore ramp go to "create color ramp," put blue on the left and red on the right, which will result in a blended purple in between.  The final visualization will show voter consistency, with dark blue (0) meaning a county voted democrat 5 times in a row and dark red (5) meaning a county voted Republican 5 times.  Lighter red and lighter blue mean that a county voted for the other party at least once while the in between shades mean a county switched back and forth.

3.  Save as a png

4:  For the "shifting_counties" layers, symbolize each layer with symbology --> categorize --> "[plug in relevant year] shifting counties."  Visualize counties that flipped democrat with blue, counties that flipped republican with red and everything that stayed the same with white.

5.  Save all four maps

6. or the "swing counties" layer, symbolize with "swing counties" with purple for any counties with a "2" or "3" and white for everything else white.

7.  Save to folder as voting_shifts.qgz.
