from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Your name here'

doc = """
Your app description
"""

LEFT_RIGHT_CHOICES = [
    ('1', ''),
    ('2', ''),
    ('3', ''),
    ('4', ''),
    ('5', ''),
    ('6', ''),
    ('7', ''),
    ('8', ''),
    ('9', ''),
]

class Constants(BaseConstants):
    name_in_url = 'questionnaire'
    players_per_group = None
    num_rounds = 1
    show_app_name = "Questionnaire"
    die_conversion = c(1)

    AGE_CHOICES = [
        'Younger than 18',
        '18-24 years old',
        '25-39 years old',
        '40-59 years old',
        '60 years or older',
    ]
    GENDER_CHOICES = [
        'Female',
        'Male',
        'Other',
    ]
    TRUST_CHOICES = [
        'You can trust most people.',
        'You can never be too careful with others.',
    ]
    EDUCATION_CHOICES = [
        'Less than high school degree',
        'High school degree or equivalent (e.g., GED)',
        'Some college but no degree',
        'Associate degree',
        'Bachelor degree',
        'Graduate degree',
    ]

    INCOME_CHOICES = [
        'Under GHS5, 000 per year',
        'GHS5, 000 to GHS9, 999 per year',
        'GHS10, 000 to GHS14, 999 per year',
        'GHS15, 000 to GHS19, 999 per year',
        'GHS20, 000 to GHS24, 999 per year',
        'GHS25, 000 to GHS29, 999 per year',
        'GHS30, 000 to GHS34, 999 per year',
        'GHS35, 000 and over',
        'Prefer not to answer',
        'Don\'t know',
    ]

    cheat_tax_choices = tuple([('0', "Always justified")] + LEFT_RIGHT_CHOICES + [('10', "Never justified")])

    tax_democracy_choices = tuple([('0', "Absolutely essential")] + LEFT_RIGHT_CHOICES + [('10', "Not essential")])

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    die_roll = models.IntegerField(min = 0, max = 6)
    
    age = models.StringField(
        verbose_name='Please indicate your age range',
        choices=Constants.AGE_CHOICES, widget=widgets.RadioSelect)
        
    income = models.StringField(
        verbose_name=("A household is defined as either one or "
                      "more persons (not necessarily related) who "
                      "live together and consume living products out "
                      "of shared wages, salaries, or rents. "
                      "What is your gross household income?"),
        choices=Constants.INCOME_CHOICES)

    gender = models.StringField(
        choices=Constants.GENDER_CHOICES,
        verbose_name='Please indicate your gender',
        widget=widgets.RadioSelect)
    
    trust = models.StringField(verbose_name="""
     Generally speaking, would you say that most people can be trusted, 
    or that you can 't be too careful in dealing with people?  """,
                               choices=Constants.TRUST_CHOICES,
                               widget=widgets.RadioSelect, )

    
    cheat_tax = models.StringField(
        verbose_name = ("Please tell me if you think that cheating on "
                        "taxes if you have the chance can always be "
                        "justified, never be justified, or something in"
                        " between."),
        choices=Constants.cheat_tax_choices,
        widget=widgets.RadioSelectHorizontal
    )

    tax_democracy = models.StringField(
        verbose_name = ("How essential is it for a democracy that the "
                        "government will tax the rich and subsidize the"
                        " poor"),
        choices=Constants.tax_democracy_choices,
        widget=widgets.RadioSelectHorizontal
        )

    word_1 = models.StringField(
        verbose_name = ("What do you think this study was about? Please "
                        "enter the first 3 words that come to your mind.")
    )
    word_2, word_3 = [models.StringField(verbose_name = "")
                      for i in (0, 1)]
    def set_payoff(self):
        self.payoff = self.die_roll * Constants.die_conversion
