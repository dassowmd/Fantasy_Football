import pandas as pd
class player:
    def __init__(self, name=None, projected_points_dict=None, league_team_name=None, bye=None, position=None):
        self.name = name
        self.projected_points = projected_points_dict
        self.league_roster_name = league_team_name
        self.bye = bye
        self.position = position

    def __str__(self):
        string = 'Player Name:%s, Position:%s, Bye:%s' % (self.name, self.position, self.bye)
        return string
