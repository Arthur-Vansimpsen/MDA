import pandas as pd
import plotly.graph_objects as go
import math as math 
import numpy as np



Project = pd.read_excel("C:/data/modern data analytics/project.xlsx")

Project = Project.loc[:, ["id", "startDate", "endDate", "totalCost", "ecMaxContribution", "fundingScheme"]]
Project.rename(columns={"id": "projectID"}, inplace=True)

Project.loc[:, "start"] = pd.to_datetime(Project.startDate)
Project.loc[:, "end"] = pd.to_datetime(Project.endDate)
Project.loc[:, "durationday"] = Project.end - Project.start
Project["duration"] = Project["durationday"].dt.days

Project = Project.loc[:, ["projectID", "startDate", "endDate", "totalCost", "ecMaxContribution", "fundingScheme", "duration"]]

print(Project.info())
#print(Project.head)

organ = pd.read_csv("organization.csv", sep=";")

organ = organ.loc[:, ["projectID", "country", "role", "activityType", "city"]]

organ.loc[:, "contributors"] = organ.groupby(["projectID"])["projectID"].transform("count")

mask = organ.role == 'coordinator'

organ = organ.loc[mask, :]

#print(organ.info())
organ.sort_values("contributors")
organ = organ.loc[:, ["projectID", "country", "role", "activityType", "city"]]
# Ensure proper formatting of 'city' column
organ['city'] = organ['city'].str.title()
organ['city'] = organ['city'].replace({
    'Paris 15': 'Paris',
    'Thermi Thessaloniki': 'Thessaloniki',
    'Athina': 'Athens'
})
#print(organ.head)


merge = Project.merge(organ, on=['projectID'], how='inner', validate="one_to_one")

#converting to numeric not working as data had , instead of . 
#use function to replace them 


merge['totalCost'] = merge['totalCost'].str.replace(',', '.', regex=False)
merge['ecMaxContribution'] = merge['ecMaxContribution'].str.replace(',', '.', regex=False)



merge["totalCost"] = pd.to_numeric(merge['totalCost'])
merge["ecMaxContribution"] = pd.to_numeric(merge['ecMaxContribution'])

mask = merge.totalCost != 0


merge.loc[mask, "proportion_cost"] = merge.ecMaxContribution / merge.totalCost

mask = merge.totalCost == 0
merge["mask"] = mask #this is the variable that denotes when totalcost was 0
merge.loc[mask, "proportion_cost"] = np.mean(merge.proportion_cost)


print(np.mean(merge.proportion_cost))

merge.loc[mask, "totalCost"] = np.floor(merge.ecMaxContribution)

merge["logCost"] = np.log2(merge["totalCost"])


Sci = pd.read_csv("euroSciVoc.csv", sep=";")


Sci = Sci.loc[:, ["projectID", "euroSciVocPath"]]

#print(Sci.info())
Sci.sort_values(by="projectID")

#print(merge.head)

#print(merge.info())


mask = merge.totalCost != merge.ecMaxContribution

#print(merge.loc[mask,:])


#merge.to_csv("oscar_dataset1.csv")

Sci['field'] = Sci['euroSciVocPath'].str.extract(r'^/?([^/]+)')

#computing partial count per project per field
count = Sci.groupby(["projectID", "field"]).agg("size").reset_index(name="partial")
#computing total count
total = Sci.groupby(["projectID"]).agg("size").reset_index(name="total")
#putting total and partial count togheter 
SciCount = count.merge(total, on=['projectID'])
#putting total and field count into rest of the dataframe

SciProject = SciCount.merge(merge, on=['projectID'], how='left', validate="many_to_one")

SciProject['Scifunding'] = SciProject.ecMaxContribution * SciProject.partial / SciProject.total

print(SciProject.loc[:  ,["projectID", "ecMaxContribution", "partial", "Scifunding"]])


#SciProject.to_csv("oscar_SciProject.csv")
