from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Instructions(Page):
    def vars_for_template(self):
        return {"example_4": Constants.die_conversion * 4,
                "example_1": Constants.die_conversion * 1}

class Dice(Page):
    form_model = 'player'
    form_fields = ['die_roll']

    def before_next_page(self):
        self.player.set_payoff()
        print("Payoff set" + str(self.player.payoff))

class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'income',
                   'trust', 'cheat_tax', 'tax_democracy',
                   "word_1", "word_2", "word_3"]
    pass


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


page_sequence = [
    Instructions,
    Dice,
    Questionnaire,
]
