import pandas as pd
from fuzzywuzzy import fuzz
from tabulate import tabulate
def update_remaining_players(drafted_players, remaining_players):
    remaining_players = full_player_list[~full_player_list['Player'].isin(drafted_players['Player'])]
    return remaining_players

def get_draft_pick(remaining_players):
    pick = raw_input("Who is drafted next?")
    if len(remaining_players[remaining_players['Player'] == pick]) == 1:
        player = remaining_players[remaining_players['Player'] == pick]
        return player
    else:
        for player in remaining_players.iterrows():
            player = dict(player[1])
            ratio = fuzz.partial_ratio(pick, player['Player'])
            if ratio >80:
                if raw_input('Did you mean to select %s, the %s for the %s?' % (player['Player'], player['Pos'], player['Team']))[0:1].lower() == 'y':
                    player = remaining_players[remaining_players['Player'] == player['Player']]
                    return player
        print "I didn't get that. Try again"
        player = get_draft_pick(remaining_players)
        return player

full_player_list = pd.read_csv('Full_Player_List.csv')
full_player_list.set_index('Player')
keeper_list = pd.read_csv('Keepers.csv')
drafted_players = pd.DataFrame(keeper_list)
draft_round = 1
draft_order = pd.DataFrame([
    "Mike Vick in a box",
    "matt's Team",
    "Hangin w MrHernandez",
    "Brian Norton's Team",
    "Dylan Smallwood",
    "Jordy wants to ride",
    "Otte's Official Team",
    "Jeremy Burg's Team",
    "Michael's Team",
    "Ross's Rad Team"
])

positions = [{'Pos':'QB','Num_Start':1}, {'Pos':'RB','Num_Start':2}, {'Pos':'WR','Num_Start':2}, {'Pos':'TE','Num_Start':1}, {'Pos':'K','Num_Start':1},{'Pos':'DST','Num_Start':1}]
player_points = []
for position in positions:
    df = pd.read_csv('FantasyPros_Fantasy_Football_Projections_%s.csv' % position['Pos'])
    for i in df.iterrows():
        i = dict(i[1])
        player_points.append({'Player': i['Player'], 'Projected_Points': i['FPTS']})
player_points_df = pd.DataFrame(player_points)
player_points_df.set_index('Player')
full_player_list = full_player_list.merge(player_points_df)
full_player_list.sort_values('Projected_Points', ascending=False, inplace=True)


remaining_players = full_player_list
remaining_players = update_remaining_players(drafted_players, remaining_players)
pick_counter = 1 + len(drafted_players)
while True:
    player = get_draft_pick(remaining_players)
    print 'Drafted %s' % player.iloc[0]['Player']
    drafted_players = drafted_players.append(player)
    remaining_players = update_remaining_players(drafted_players, remaining_players)
    vs_the_rest = []
    for position in positions:
        position_drafted_count = len(drafted_players[drafted_players['Pos'] == position['Pos']])
        max = int(position['Num_Start']*10)
        all_at_position = remaining_players[remaining_players['Pos'] == position['Pos']][0:max]
        mean_adp = int(all_at_position['ADP'].mean())
        mean_proj_points = int(all_at_position['Projected_Points'].mean())
        median_adp = int(all_at_position['ADP'].median())
        median_proj_points = int(all_at_position['Projected_Points'].median())
        best_at_position = remaining_players[remaining_players['Pos'] == position['Pos']][0:5]
        best_at_position['ADP_vs_replacement_mean'] = best_at_position['ADP'] - mean_adp
        best_at_position['Proj_Points_vs_replacement_mean'] = best_at_position['Projected_Points'] - mean_proj_points
        best_at_position['ADP_vs_replacement_median'] = best_at_position['ADP'] - median_adp
        best_at_position['Proj_Points_vs_replacement_median'] = best_at_position['Projected_Points'] - median_proj_points
        top_at_position = best_at_position['Projected_Points'].iloc[0]
        next_at_position = best_at_position['Projected_Points'].iloc[1]
        vs_next = top_at_position - next_at_position
        next_3_at_position = best_at_position['Projected_Points'][1:3]
        vs_next_3 = top_at_position - next_3_at_position.mean()
        player = best_at_position.iloc[0]
        remaining_player_rank = remaining_players.loc['Denver Broncos']
        remaining_player_rank = remaining_players['Player'].loc[player.iloc[0]['Player']]
        pick_count_vs_ADP = player['ADP'] - pick_counter
        pick_count_vs_rank = player['Rank'] - pick_counter
        vs_the_rest.append({'Position':player['Pos'],'pick_count_vs_ADP':pick_count_vs_ADP,'pick_count_vs_Rank':pick_count_vs_rank,'Player':player['Player'], 'vs_next':vs_next, 'vs_next_3':vs_next_3})
        print 'Pick Number: %i' % pick_counter
        print tabulate(best_at_position, headers='keys',tablefmt='psql')
        print 'Mean ADP:' + str(int(all_at_position['ADP'].mean())) + '  Mean Projected Points: ' + str(int(all_at_position['Projected_Points'].mean()))
    print tabulate(pd.DataFrame(vs_the_rest), headers='keys',tablefmt='psql')
    pick_counter += 1


# print remaining_players.head()
# drafting_team =
# while draft_round <=15:
#     if (draft_round % 2 == 0):