from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

from django.core.validators import RegexValidator
#from dg.models import Player as dgPlayer
#from phonesurvey.models import Player as phonesurveyPlayer


author = 'Your name here'

doc = """
Your app description
"""

    
class Constants(BaseConstants):
    name_in_url = 'payment'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    def creating_session(self):
        pass




class Group(BaseGroup):
    pass


class Player(BasePlayer):
    phone_regex = RegexValidator(
        regex=r'^\d{9,15}$',
        message= ("Phone number must be entered in the format:"
                  " '0999999999'. Up to 15 digits allowed."))
    payment_phone_1 = models.CharField(validators=[phone_regex],
                                       max_length=17,
                                       blank=True) 
    payment_phone_1 = models.IntegerField()
    payment_phone_2 = models.IntegerField()
    payment_confirm = models.CurrencyField()
    pass
