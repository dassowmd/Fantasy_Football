# https://github.com/BrutalSimplicity/YHandler/blob/master/README.rst
from YHandler import YHandler, YQuery
from tabulate import tabulate
import pandas as pd
from fuzzywuzzy import fuzz
import player
import team
import league
import json
import copy
import time

def manual_team_roster_load(file_path):
    f = open(file_path)
    json_object = json.load(f)
    return json_object

def parse_json(json):
    output = []
    for player in json['query']['results']['team']['roster']['players']['player']:
        temp = {}
        temp['Player'] = player['name']['full']
        temp['Bye'] = player['bye_weeks']
        temp['Pos'] = player['display_position']
        temp['Team'] = player['editorial_team_full_name']
        output.append(temp)
    df = pd.DataFrame(output)
    return df

handler = YHandler()
query = YQuery(handler, 'nfl')

# print tabulate(query.get_games_info(), headers='keys',tablefmt='psql')
#
# print tabulate(query.get_games_info(True), headers='keys',tablefmt='psql')
#
# print tabulate(query.get_user_leagues(), headers='keys',tablefmt='psql')

# print tabulate(query.find_player(994469, 'antonio brown'), headers='keys',tablefmt='psql')
# print tabulate(query.get_player_week_stats(24171, '1'), headers='keys',tablefmt='psql')

full_player_list = pd.read_csv('Full_Player_List.csv')
full_player_list.set_index(['Player', 'Team', 'Pos'])

roster_positions = [{'position':['QB']}
    , {'position':['RB']}
    , {'position':['RB']}
    , {'position':['WR']}
    , {'position':['WR']}
    , {'position':['TE']}
    , {'position':['RB','WR','TE']}
    , {'position':['K']}
    , {'position':['DST']}
    , {'position':['BN']}
    , {'position':['BN']}
    , {'position':['BN']}
    , {'position':['BN']}
    , {'position':['BN']}
    , {'position':['BN']}]
league = league.league(roster_positions=roster_positions)
player_points = []
unique_positions = pd.Series(['QB','RB','WR','TE','K','DST'])
# unique_positions.delete('BN')
for pos in unique_positions:
    df = pd.read_csv('FantasyPros_Fantasy_Football_Projections_%s.csv' % pos)
    for i in df.iterrows():
        i = dict(i[1])
        # TODO improve projected points. Currently dividing total season by 16
        player_points.append({'Player': i['Player'], 'Team':i['Team'], 'Pos':pos, 'Projected_Points': i['FPTS']/16})
player_points_df = pd.DataFrame(player_points)
player_points_df.set_index(['Player', 'Team', 'Pos'])
full_player_list = full_player_list.merge(player_points_df)

# TODO Convert this to dynamically get teams and iterate through them
for i in range(1,11):
    # roster_query = pd.DataFrame(query.query_team_roster('994469', i))

    #Get manually loaded rosters
    roster_query = parse_json( manual_team_roster_load(r'Manual_Team_Rosters/%s.json' %str(i)))

    roster_query.set_index('Player')
    rost = team.team(owner_name=i, roster=[], roster_position_list=league.roster_positions)
    league.add_team(rost)
    for pl in roster_query.iterrows():
        # player = player.player()
        pl = dict(pl[1])
        try:
            name = pl['Player']
            projected_points = full_player_list[full_player_list['Player'] == name]['Projected_Points'].item()
            League_Team = i
            bye = full_player_list[full_player_list['Player'] == name]['Bye'].item()
            position = full_player_list[full_player_list['Player'] == name]['Pos'].item()
            player_instance = player.player(name=name, projected_points_dict=projected_points, league_team_name=rost.owner_name, bye=bye, position=position)
            rost.add_player(player=player_instance)
        except Exception as e:
            try:
                best_ratio = 0
                best_match = player.player()
                for p in full_player_list.iterrows():
                    p = dict(p[1])
                    ratio = fuzz.partial_ratio(name, p['Player'])
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match = p
                    if best_ratio == 100:
                        break
                name = best_match['Player']
                projected_points = full_player_list[full_player_list['Player'] == name][
                    'Projected_Points'].item()
                League_Team = i
                bye = full_player_list[full_player_list['Player'] == name]['Bye'].item()
                position = full_player_list[full_player_list['Player'] == name]['Pos'].item()
                player_instance = player.player(name=name, projected_points_dict=projected_points,
                                                league_team_name=rost.owner_name, bye=bye,
                                                position=position)
                rost.add_player(player=player_instance)
            except Exception as e:
                print e
                print 'Can not process %s' % pl['Player']
        # print player_irost.owner_namenstance
    # print tabulate(rost.get_DataFrame(), headers='keys', tablefmt='psql')
weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]

t = league.team_list[0]
t_total_points=[]
for week in weeks:
    t_starting_lineup = t.get_starting_lineup(week=week)
    t_weekly_points = t_starting_lineup['projected_points'].sum()
    t_total_points.append(t_weekly_points)
t_total_points = pd.Series(t_total_points).sum()
results = []
max_players = 15
total_calcs = max_players * max_players * (max_players - 1) * (max_players - 1) * (len(league.team_list) - 1)
for i in league.team_list:
    try:
        i_total_points=[]
        for week in weeks:
            i_starting_lineup = i.get_starting_lineup(week=week)
            i_weekly_points = i_starting_lineup['projected_points'].sum()
            i_total_points.append(i_weekly_points)
        i_total_points = pd.Series(i_total_points).sum()
        if i != t:
            # TODO Currently running for only first x players for each team to save calc time. Remove to search all
            for team_1_first_player_traded in t.roster[0:max_players]:
                for team_1_second_player_traded in t.roster[0:max_players]:
                    if team_1_first_player_traded != team_1_second_player_traded:
                        time_start = time.time()
                        for team_2_first_player_traded in i.roster[0:max_players]:
                            for team_2_second_player_traded in i.roster[0:max_players]:
                                if team_2_first_player_traded != team_2_second_player_traded:
                                    # Use deep copy function to create a new instance and avoid creating based on a pointer
                                    temp_team_1 = copy.deepcopy(t)
                                    temp_team_2 = copy.deepcopy(i)
                                    temp_team_1.remove_player(team_1_first_player_traded)
                                    temp_team_1.remove_player(team_1_second_player_traded)
                                    temp_team_1.add_player(team_2_first_player_traded)
                                    temp_team_1.add_player(team_2_second_player_traded)
                                    temp_team_2.remove_player(team_2_first_player_traded)
                                    temp_team_2.remove_player(team_2_second_player_traded)
                                    temp_team_2.add_player(team_1_first_player_traded)
                                    temp_team_2.add_player(team_1_second_player_traded)
                                    team_1_total_points = []
                                    team_2_total_points = []
                                    for week in weeks:
                                        # time_start = time.time()
                                        team_1_starting_lineup = temp_team_1.get_starting_lineup(week=week)
                                        # print time.time() - time_start
                                        team_1_weekly_points = team_1_starting_lineup['projected_points'].sum()
                                        team_1_total_points.append(team_1_weekly_points)
                                        # print 'Team: %s, Week: %i, Trade for: %s Projected Points: %s' %(t.owner_name, week, team_2_first_player_traded, team_1_weekly_points)
                                        team_2_starting_lineup = temp_team_2.get_starting_lineup(week=week)
                                        team_2_weekly_points = team_2_starting_lineup['projected_points'].sum()
                                        team_2_total_points.append(team_2_weekly_points)
                                        # print 'Team: %s, Week: %i, Trade for: %s Projected Points: %s' %(i.owner_name, week, team_1_first_player_traded, team_2_weekly_points)

                                    temp = {}
                                    temp['team_1_owner'] = t.owner_name
                                    temp['team_1_total_points'] = pd.Series(team_1_total_points).sum()
                                    temp['team_1_trade_for_player_1'] = team_2_first_player_traded
                                    temp['team_1_trade_for_player_2'] = team_2_second_player_traded
                                    temp['team_1_original_total_points'] = t_total_points
                                    temp['team_1_point_dif'] = temp['team_1_total_points'] - temp['team_1_original_total_points']

                                    temp['team_2_owner'] = i.owner_name
                                    temp['team_2_total_points'] = pd.Series(team_2_total_points).sum()
                                    temp['team_2_trade_for_player_1'] = team_1_first_player_traded
                                    temp['team_2_trade_for_player_2'] = team_1_second_player_traded
                                    temp['team_2_original_total_points'] = i_total_points
                                    temp['team_2_point_dif'] = temp['team_2_total_points'] - temp['team_2_original_total_points']

                                    results.append(temp)
                        percent_done = float(len(results))/float(total_calcs)
                        print '%s - Percent Complete: %d' % (str(time.time()),(percent_done*100))
                        # print len(results)

    except Exception as e:
        print e
    results_df = pd.DataFrame(results)
    results_df.to_csv('temp_comparison.csv')
    print results_df
results_df = pd.DataFrame(results)
results_df.to_csv('Trade_Comparison_Output.csv')
print results_df

