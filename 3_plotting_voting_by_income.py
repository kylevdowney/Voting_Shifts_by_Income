import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#here we want to take the bundled together data from the master_df compiled in
#the last script, adjust income for inflation for intuitive graphs.  

final_dtype = {"inflation adjusted income" : float, 
               "year" : int, 
               "swing_counties" : str} #(do I want to keep year as int?)

master_df = pd.read_csv("final_df.csv", dtype = final_dtype)


#%%
#Then we break the master_df into two halves - swing_counties and stable_counties
#to see how they differ from each other and from the master_df


swing_counties = master_df.query("swing_counties == '2' or swing_counties == '3'").copy()
swing_counties["type"] = "swing"

swing_counties.to_csv("swing_counties.csv")

stable_counties = master_df.query("swing_counties != '2' and swing_counties != '3'")
stable_counties["type"] = "stable"


stable_counties.to_csv("stable_counties.csv")


#%%
# Violin plots for the entire nation
#
party_colors = {"democrat" : "blue",
               "republican" : "red"}

fig, ax1 = plt.subplots(dpi=300)
sns.violinplot(data=master_df,x="year",y="inflation adjusted income",hue="party",split=True, palette=party_colors)
ax1.set_title("Party Preference by Income (Entire Country)")
ax1.set_ylabel("inflation adjusted income")
fig.tight_layout()
fig.savefig('US_voting_by_income_violin_chart.png')


#%% Violin plots just for the swing counties

fig, ax1 = plt.subplots(dpi=300)
sns.violinplot(data=swing_counties,x="year",y="inflation adjusted income",hue="party",split=True, palette=party_colors)
ax1.set_title("Party Preference by Income (Swing Counties)")
ax1.set_ylabel("inflation adjusted income")
fig.tight_layout()
fig.savefig('swing_county_voting_by_income_violin_chart.png')

#%% Violin plots just for the stable counties

fig, ax1 = plt.subplots(dpi=300)
sns.violinplot(data=stable_counties,x="year",y="inflation adjusted income",hue="party",split=True, palette=party_colors)
ax1.set_title("Party Preference by Income (Stable Counties)")
ax1.set_ylabel("inflation adjusted income")
fig.tight_layout()
fig.savefig('stable_county_voting_by_income_violin_chart.png')


#%%
both_df = [swing_counties, stable_counties]
stable_and_swing = pd.concat(both_df).reset_index(drop=True)
stable_and_swing.unstack()

fig, ax1 = plt.subplots(dpi=300)
sns.lineplot(data=stable_and_swing,x="year",y="inflation adjusted income", hue = "type")
ax1.set_title("US Income Growth (disaggregated)")
ax1.set_ylabel("Income")
fig.savefig('US_Income_Growth_(disaggregated).png')

