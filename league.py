class league:
    def __init__(self, roster_positions=None, team_list=[]):
        self.roster_positions = roster_positions
        self.team_list = team_list

    def add_team(self, team):
        self.team_list.append(team)

