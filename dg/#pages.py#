from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Instructions(Page):
    ...

class Decision(Page):
    form_fields = ['dg_decision']
    form_model = 'player'

class AfterDecisionWP(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()
        
page_sequence = [
    Instructions,
    Decision,
    AfterDecisionWP,
]
