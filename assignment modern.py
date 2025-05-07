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

organ = organ.loc[:, ["projectID", "country", "role"]]

organ.loc[:, "contributors"] = organ.groupby(["projectID"])["projectID"].transform("count")

mask = organ.role == 'coordinator'

organ = organ.loc[mask, :]

#print(organ.info())
organ.sort_values("contributors")
organ = organ.loc[:, ["projectID", "country", "contributors"]]

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
merge["mask"] = mask
merge.loc[mask, "proportion_cost"] = np.mean(merge.proportion_cost)


print(np.mean(merge.proportion_cost))

merge.loc[mask, "totalCost"] = np.floor(merge.ecMaxContribution)

merge["logCost"] = np.log2(merge["totalCost"])


Sci = pd.read_csv("euroSciVoc.csv", sep=";")


Sci = Sci.loc[:, ["projectID", "euroSciVocPath"]]

#print(Sci.info())
Sci.sort_values("projectID")

#print(merge.head)

#print(merge.info())


mask = merge.totalCost != merge.ecMaxContribution

#print(merge.loc[mask,:])


merge.to_csv("oscar_dataset1.csv")

Sci['field'] = Sci['euroSciVocPath'].str.extract(r'^/?([^/]+)')

print(Sci)
print(merge)