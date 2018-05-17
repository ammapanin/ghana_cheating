from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
import random

author = 'Philipp Chapkovski, chapkovski@gmail.com'

doc = """
Your app description
"""

DEMOGRAPHIC_CATEGORIES = ["Male, 18 to 25 years",
                          "Male, 30 to 40 years",
                          "Female, 18 to 25 years",
                          "Female, 30 to 40 years"]

class Constants(BaseConstants):
    name_in_url = 'phonesurvey'
    show_app_name = "Recommendations"
    players_per_group = None
    num_rounds = 1
    flat_fee = c(5)
    per_phone_fee = c(0.5)
    time = 600


class Subsession(BaseSubsession):
    def creating_session(self):
        for p in self.get_players():
            random.shuffle(DEMOGRAPHIC_CATEGORIES)
            p.demographics = DEMOGRAPHIC_CATEGORIES[0]
            if p.id_in_subsession % 2 == 0:
                p.treatment = 'flat'
            else:
                p.treatment = 'variable'


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    treatment = models.StringField()
    dump_phones = models.LongStringField()
    num_phones = models.IntegerField()
    demographics = models.LongStringField()

    def set_payoff(self):
        n_phones =  self.phones.all().count()
        self.num_phones = n_phones
        if self.treatment == 'flat':
            self.payoff = Constants.flat_fee
        else:
            self.payoff = (Constants.per_phone_fee * n_phones)
            
class Phone(djmodels.Model):
    player = djmodels.ForeignKey(to=Player, related_name='phones')
    # todo: do some basic checking of the input.
    number = djmodels.BigIntegerField()
    name = models.StringField(label = "Name")
    residence = models.StringField(label = "Area of residence")
    #consent = models.BooleanField(label = "Agreed to participate")

