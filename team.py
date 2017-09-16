import pandas as pd
import threading
import Queue
import copy
import numpy

class team:
    def __init__(self, owner_name, roster=[], roster_position_list=None):
        self.owner_name = owner_name
        self.roster = roster
        self.roster_position_list = roster_position_list

    def get_starting_lineup(self, week):
        full_roster = self.get_List()
        starting_lineup = []
        for pos in self.roster_position_list:
            available_players = []
            best_score = 0
            best_player = None
            for i in pos['position']:
                if i != 'BN':
                    for player in full_roster:
                        pass
                        if (player['position'] == i) & (player['bye'] != week):
                            if player in starting_lineup:
                                pass
                            else:
                                if player['projected_points'] > best_score:
                                    best_score = player['projected_points']
                                    best_player = player
                                available_players.append(player)
            else:
                # TODO there are no available players for the position
                # - get the next best player from the waiver wire for the pos['position']
                pass
            if best_player != None:
                starting_lineup.append(best_player)
        self.starting_lineup = starting_lineup
        return pd.DataFrame(starting_lineup)

    # This was my original method that was SLOWWWWW
    def get_starting_lineup_df(self, week):
        # try:
        full_roster = self.get_DataFrame()
        cols =[list(full_roster.columns.values)]
        starting_lineup = pd.DataFrame(columns=cols)
        for pos in self.roster_position_list:
            available_players = pd.DataFrame()
            for i in pos['position']:
                if i != 'BN':
                    temp = full_roster[(full_roster['position'] == i) & (full_roster['bye'] != week)]
                    if len(temp) > 0:
                        available_players = available_players.append(temp)
                    else:
                        pass
            # remove players already in starting roster
            # if len(starting_lineup[starting_lineup['position'] == i]) > 0:
            if available_players.empty == False:
                available_players = available_players[~available_players['name'].isin(starting_lineup['name'])]

                available_players = available_players.sort_values('projected_points', ascending=False)
                # If no player is available at the position, do not add to starting roster
                if available_players.empty == False:
                    best_player_available = available_players.iloc[0]
                    starting_lineup = starting_lineup.append(best_player_available)

        self.starting_lineup = starting_lineup
        return starting_lineup
        # except Exception as e:
        #     print e
        #     print 'week:%s position:%s available_players:%s' %(week, i, available_players)


    def add_player(self, player):
        self.roster.append(player)

    def remove_player(self, player):
        for i in self.roster:
            if i.name == player.name:
                self.roster.remove(i)
                break


    def get_DataFrame(self):
        output = self.get_List()
        output_df = pd.DataFrame(output)
        return output_df

    def get_List(self):
        output = []
        for i in self.roster:
            p = i.__dict__
            output.append(p)
        return output

    def get_weekly_points_list(self, weeks):
        total_points = []
        for week in weeks:
            res = self.get_single_week_points(week=week)
            total_points.append(res)
        return total_points

    def get_single_week_points(self, week):
        starting_lineup = self.get_starting_lineup(week=week)
        weekly_points = starting_lineup['projected_points'].sum()
        return weekly_points