

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import pandas as pd 
import seaborn as sns
match=pd.read_csv('matches.csv')
deliveries=pd.read_csv('deliveries.csv')
deliveries=deliveries
##Initializing Required Variables
Teams = list(deliveries['batting_team'].drop_duplicates())

#Function to add batsman_points
def batsman_point_func(x):
    if x ==6:
        x=x+2
        return x
    elif x ==4:
        x=x+1
        return x
    else:
        return x
deliveries['Batsman_points']=deliveries['batsman_runs'].apply(batsman_point_func)
#Function to add Bowlers_Points
def bowlers_point_func(x):
    if x =="bowled":
        y=25
        return y
    elif x =="caught":
        y=25
        return y
    elif x =="caught and bowled":
        y=33
        return y
    elif x =='hit wicket':
        y=25
        return y
    elif x =="lbw":
        y=25
        return y
    elif x =="stumped":
        y=25
        return y
    else:
        return 0
deliveries["Bowlers_Point"]=deliveries["dismissal_kind"].apply(bowlers_point_func)
deliveries.tail()
#Function to add Fielders_points
def fielders_point_func(x):
    if x =="caught":
        y=8
        return y
    elif x =="stumped":
        y=12
        return y
    elif x =="run out":
        y=8 
        return y
    else:
        return 0
deliveries["Fielders_Point"]=deliveries["dismissal_kind"].apply(fielders_point_func)
deliveries.tail()

#New DataFrame for Batsman_points
bat_points=deliveries.groupby(['match_id','batsman'], as_index=False)
batting_points=pd.DataFrame(bat_points.Batsman_points.sum())
batting_points=batting_points.rename({'batsman':'Players'},axis=1)
batting_points['batting_join']=batting_points['match_id'].astype(str)+','+batting_points['Players']


#New DataFrame for Bowling_points
bowler_points=deliveries.groupby(['match_id','bowler'], as_index=False)
bowling_points=pd.DataFrame(bowler_points.Bowlers_Point.sum())
bowling_points=bowling_points.rename({'bowler': 'Players'}, axis=1)
bowling_points['bowling_join']=bowling_points['match_id'].astype(str)+','+bowling_points['Players']


#New DataFrame for Fielding_points
fielder_points=deliveries.groupby(['match_id','fielder'], as_index=False)
fielding_points=pd.DataFrame(fielder_points.Fielders_Point.sum())
fielding_points=fielding_points.rename({'fielder': 'Players'}, axis=1)
fielding_points['fielding_join']=fielding_points['match_id'].astype(str)+','+fielding_points['Players']

#Creating Rank DataFrame by mergin bat and bowl points dataframe
Rank=pd.merge(batting_points,bowling_points,left_on='batting_join',right_on='bowling_join',how='outer')
Rank['Player_Name']=np.where(Rank['Players_x'].isnull(),Rank['Players_y'],Rank['Players_x'])
Rank['match_id']=np.where(Rank['match_id_x'].isnull(),Rank['match_id_y'],Rank['match_id_x'])
del Rank['match_id_x']
del Rank['match_id_y']
del Rank['Players_x']
del Rank['Players_y']
del Rank['bowling_join']

#merging field points with rank
Rank=pd.merge(Rank,fielding_points,left_on='batting_join',right_on='fielding_join',how='outer')
Rank['Player_Name']=np.where(Rank['Player_Name'].isnull(),Rank['Players'],Rank['Player_Name'])
Rank['match_id']=np.where(Rank['match_id_x'].isnull(),Rank['match_id_y'],Rank['match_id_x'])
del Rank['match_id_x']
del Rank['match_id_y']
del Rank['Players']
del Rank['batting_join']
del Rank['fielding_join']

#Re-Organizing Dataframe
Rank = Rank[['match_id','Player_Name','Batsman_points','Bowlers_Point','Fielders_Point']]
Rank.fillna(0.0,inplace=True)

#Ranking based on Total Points
Rank['Total_Points'] = Rank.Batsman_points+Rank.Bowlers_Point+Rank.Fielders_Point
Rank['rank'] = Rank.groupby('match_id')['Total_Points'].rank(ascending=False,method='dense')

#Extracting Top 10 No.1 Ranked Players
Top_Rank_Players = pd.DataFrame(Rank[Rank['rank']==1.0]['Player_Name'].value_counts().head(10))
Top_Rank_Players = Top_Rank_Players.reset_index()
Top_Rank_Players.rename(columns={'index':'Player_Name','Player_Name':'rank'},inplace=True)
List1=list(Top_Rank_Players['Player_Name'])

temp = Rank[Rank['Player_Name'].isin(List1)]

#################################################

sns.lineplot(x=temp.match_id,y=temp.Batsman_points,data=temp,hue=temp.Player_Name)
sns.lineplot(x=temp.match_id,y=temp.Bowlers_Point,data=temp,hue=temp.Player_Name)
sns.lineplot(x=temp.match_id,y=temp.Total_Points,data=temp,hue=temp.Player_Name)

#Most Sixes Dataset
sixes = pd.DataFrame(deliveries[deliveries['batsman_runs']==6]['batsman'].value_counts())
sixes.rename(columns={'batsman':'No_of_Sixes'},inplace=True)

#Most Fours Dataset
fours = pd.DataFrame(deliveries[deliveries['batsman_runs']==4]['batsman'].value_counts())
fours.rename(columns={'batsman':'No_of_Fours'},inplace=True)

#Most Wickets Taken
dismissal_kinds = ['caught','bowled','lbw','stumped','caught and bowled']
wickets=pd.DataFrame(deliveries[deliveries['dismissal_kind'].isin(dismissal_kinds)]['bowler'].value_counts())
wickets.rename(columns={'bowler':'No_of_Wickets'},inplace=True)

scorecard=pd.concat([fours,sixes,wickets],axis=1)
scorecard.fillna(0,inplace=True)
scorecard=scorecard.reset_index()
scorecard.rename(columns={'index':'Player'},inplace=True)

#Economy Rate Calculation
#Grouping
y=pd.DataFrame((deliveries['match_id'].map(str)+'-'+deliveries['over'].map(str),deliveries['bowler'],deliveries['total_runs'])).T
y.rename(columns={'Unnamed 0':'ID'},inplace=True)

#Match-Over Wise Over Total
eco_calc=y.groupby(['ID','bowler'],as_index=False).agg({'total_runs':'sum'})
eco_calc.rename(columns={'total_runs':'Over_Runs'},inplace=True)

#Overall Runs Conceded
temp=eco_calc.groupby(['bowler'],as_index=False).agg({'Over_Runs':'sum'})
temp.rename(columns={'Over_Runs':'Total_Runs_Conceded'},inplace=True)
eco_calc=pd.merge(left=eco_calc,right=temp,left_on='bowler',right_on='bowler',how='outer')
del temp 

#Overall Overs Bowled
temp=eco_calc['bowler'].value_counts()
temp=temp.reset_index()
temp.rename(columns={'index':'bowler','bowler':'Overs_Bowled'},inplace=True)
eco_calc=pd.merge(left=eco_calc,right=temp,left_on='bowler',right_on='bowler',how='outer')
del temp

#Economy Rate
eco_calc['Economy']=eco_calc['Total_Runs_Conceded']/eco_calc['Overs_Bowled']
eco_calc.fillna(0,inplace=True)

temp=eco_calc[['bowler','Economy']].drop_duplicates()
scorecard=pd.merge(left=scorecard,right=temp,left_on='Player',right_on='bowler',how='outer')
scorecard.fillna(0,inplace=True)
del scorecard['bowler']
del temp

#No. of Matches Played
temp=pd.DataFrame(Rank['Player_Name'].value_counts())
temp=temp.reset_index()
temp.rename(columns={'Player_Name':'Matches'},inplace=True)
scorecard=pd.merge(scorecard,temp,left_on='Player',right_on='index',how='outer')
del scorecard['index']
del temp

#Strike Rate Calculator
sr_calc=pd.DataFrame(deliveries.groupby(['batsman'],as_index=False).agg({'ball':'count','batsman_runs':'sum'}))
sr_calc['Strike_Rate']=100*(sr_calc['batsman_runs']/sr_calc['ball'])
scorecard=pd.merge(left=scorecard,right=sr_calc,left_on='Player',right_on='batsman',how='outer')
del scorecard['batsman']

#ReOrdering Scorecard
scorecard=scorecard[['Player', 'Matches', 'ball', 'batsman_runs', 'No_of_Fours', 'No_of_Sixes', 'No_of_Wickets', 'Strike_Rate', 'Economy']]
scorecard.rename(columns={'ball':'Balls_Faced','batsman_runs':'Total_Runs'},inplace=True)

temp=scorecard[scorecard['Player'].isin(list(Top_Rank_Players['Player_Name']))]

#Plotting Economy and Strike Rate for Top Rank Players
xyz=sns.scatterplot(x=temp.Player,y=temp.Economy,data=temp)
[tick.set_rotation(30) for tick in xyz.get_xticklabels()]
abc=sns.lineplot(x=temp.Player,y=temp.Strike_Rate,data=temp)
[tick.set_rotation(30) for tick in abc.get_xticklabels()]
del temp


#Batting_Order
temp=deliveries[['match_id','inning','batting_team','batsman']]
temp.drop_duplicates(inplace=True)
temp.reset_index(inplace=True)
del temp['index']
temp['index']=temp.index

temp['batting_order']= temp.groupby(['match_id','inning','batting_team']).index.rank(method='first')
del temp['index']

temp['Joined_Field'] = temp[['batting_order', 'batsman']].apply(lambda x: '-'.join((x).astype(str)), axis=1)
temp[(temp['batting_team']=='Chennai Super Kings') & (temp['batting_order']==2)]['Joined_Field'].value_counts().head(1)
    