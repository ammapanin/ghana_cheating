from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Your name here'

doc = """
Your app description
"""

dg_decision_name = ('Please decide how many points '
                    'you would like to send to your partner')

    
class Constants(BaseConstants):
    name_in_url = 'dg'
    players_per_group = 2
    num_rounds = 1
    endowment = c(6)
    show_app_name = "Sharing"

class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            p.endowment = Constants.endowment
            p.is_dictator = p.role() == "sender"

class Group(BaseGroup):

    def set_payoffs(self):
        sender = self.get_player_by_role('sender')
        receiver = self.get_player_by_role('receiver')
        sender.payoff = sender.endowment - sender.dg_decision
        receiver.payoff = sender.dg_decision


class Player(BasePlayer):
    endowment = models.CurrencyField()
    dg_decision = models.CurrencyField(min = 0,
                                       max = Constants.endowment,
                                       verbose_name = dg_decision_name)
    is_dictator = models.BooleanField()
    
    def get_another_group_name(self):
        if self.role() == 'sender':
            return 'Group B'
        return 'Group A'

    def get_group_name(self):
        if self.role() == 'sender':
            return 'Group A'
        return 'Group B'

    def role(self):
        if self.id_in_group == 1:
            return 'sender'
        return 'receiver'
