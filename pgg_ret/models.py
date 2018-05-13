from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range,
)

from django.db import models as djmodels
from django.db.models.signals import post_save
from django.db.models import F
import json
import random

author = 'Philipp Chapkovski, chapkovski@gmail.com'

doc = """
    multi-round real effort task + public good game (R.Duch)
"""

class Constants(BaseConstants):
    name_in_url = 'pgg_ret'
    players_per_group = 4
    show_app_name = "Additions"
    num_rounds = 20
    switch_audit_round = int(round(num_rounds/2)) + 1
    task_time = 60
    lb = 30
    ub = 99
    alldigs = list(range(30, 99, 1))
    # we filter out the numbers divisible by 5 to make
    # it a bit more complicated
    rchoices = [i for i in alldigs if i % 5 != 0]
    fee = c(1)  # payment for correct answer
    # set of probabilities to be checked (to define later)
    probs = [.0, 0.1]
    tax_rate = .1
    fine_rate = .5
    pgg_factor = 1
    
class Subsession(BaseSubsession):
    def creating_session(self):           
        self.group_randomly()
        for p in self.get_players():
            if self.round_number == 1:
                probs = Constants.probs.copy()
                random.shuffle(probs)
                p.participant.vars["prob_order"] = probs

            probs = p.participant.vars.get("prob_order")
            if self.round_number < Constants.switch_audit_round:
                prob_ix = 0
            else:
                prob_ix = 1
            prob = probs[prob_ix]
            p.audit_prob = prob
            r = random.random()
            if r < prob:
                p.is_checked = True

class Group(BaseGroup):
    total_contribution = models.CurrencyField(
        doc='total contribs to the pool')
    individual_share = models.CurrencyField(
        doc='individual share from the pool')
    def calculate_pgg(self):
        assertion_string = 'cant calculate pool for 0-size groups'
        assert Constants.players_per_group is not None, assertion_string
        for p in self.get_players():
            p.process_deduction()
        self.total_contribution = sum([p.deduction + p.fine
                                       for p in self.get_players()])
        individual_share_raw = (self.total_contribution/
                                Constants.players_per_group)
        self.individual_share = individual_share_raw * Constants.pgg_factor

class Player(BasePlayer):
    audit_prob = models.FloatField()
    ret_earning = models.CurrencyField(
        doc='ret earnings stored here')
    tasks_dump = models.LongStringField(
        doc='to store all tasks with answers')
    declaration = models.CurrencyField(
        doc='amount declared by player',
        min=0,
        verbose_name='Amount to declare:')
    is_checked = models.BooleanField(
        doc='whether a player being checked in this round')
    deduction = models.CurrencyField(doc='total deduction')
    discrepancy = models.CurrencyField(
        doc='diff between declaration and earnings')
    earnings_after_deduction = models.CurrencyField(doc='total deduction')
    fine = models.CurrencyField(
        doc='if checked - by how much is punished', initial=0)

    # the following method makes the deduction from the declared 
    # amounts if a player is not designated for checking
    # in this round. If they do, we take the toll from 
    # real earned amount plus impose the fine
    
    def process_deduction(self):
        ret_assert = ('You shouldn\t call this method before'
                      ' you calculate the earnings by RET')
        declaration_assert = ('You shouldn\t call this method'
                              ' before player declares their earnings')
        assert self.ret_earning is not None, ret_assert
        assert self.declaration is not None, declaration_assert
        # lim to guarantee that nobody declared MORE that they earned
        self.discrepancy = max(self.ret_earning - self.declaration, 0)
        if self.is_checked:
            self.deduction = self.ret_earning * Constants.tax_rate
            self.fine = Constants.fine_rate * self.discrepancy
        else:
            self.deduction = self.declaration * Constants.tax_rate
            self.fine = 0
            # self.fine not necessary, but don't like to leave
            # it to the sake of initial...
        self.earnings_after_deduction = (self.ret_earning -
                                         self.deduction -
                                         self.fine)

    def get_unfinished_task(self):
        unfinished_tasks = self.tasks.filter(answer__isnull=True)
        if unfinished_tasks.exists():
            return unfinished_tasks.first()
        return False

    def set_payoff(self):
        set_assert = ('cant set the payoffs before we calculate '
                      'the pgg pool')
        deduct_assert = 'you should first set the deductions'
        assert self.group.total_contribution is not None, set_assert
        assert self.earnings_after_deduction is not None, deduct_assert
        self.payoff = (self.earnings_after_deduction +
                       self.group.individual_share)

    @property
    def finished_tasks(self):
        return self.tasks.filter(answer__isnull=False)

    def get_recent_finished_task(self):
        is_task = self.finished_tasks.exists()
        if is_task:
            return self.finished_tasks.latest('updated_at')

    def get_correct_tasks(self):
        return self.tasks.filter(correct_answer=F('answer'))

    @property
    def num_tasks_correct(self):
        return self.get_correct_tasks().count()

    def dump_tasks(self):
        # this method will request all completed tasks and dump them
        # to player's field just for the convenience and following 
        # analysis.
        # theoretically we don't need to store 'updated_at' field
        # because it is already sorted by this field but just in case

        q = self.finished_tasks
        data = list(q.values(
            'correct_answer',
            'answer',
            'updated_at'))
        # the following loop we need to avoid issues with converting
        # dateteime to string
        for d in data:
            d['updated_at'] = str(d['updated_at'])
        self.tasks_dump = json.dumps(data)

    def set_ret_earnings(self):
        self.ret_earning = Constants.fee * self.num_tasks_correct


class Task(djmodels.Model):
    class Meta:
        ordering = ['updated_at']

    player = djmodels.ForeignKey(to=Player, related_name='tasks')
    correct_answer = models.IntegerField(doc='right answer')
    answer = models.IntegerField(doc='user\'s answer', null=True)
    created_at = djmodels.DateTimeField(auto_now_add=True)
    updated_at = djmodels.DateTimeField(auto_now=True)
    left = models.IntegerField(doc='for left number to sum')
    right = models.IntegerField(doc='for right number to sum')

    @staticmethod
    def gen_left_right():
        return random.sample(Constants.rchoices, 2)

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        # this presumably is considered the safest method to update 
        # newly created items so we catch the new task, we add there
        # the body based on difficulty level and the correct answer.

        if not created:
            return
        instance.left, instance.right = Task.gen_left_right()
        instance.correct_answer = instance.left + instance.right
        instance.save()

    def get_dict(self):
        # this method pushes the task to the page via consumers
        return {
            # TODO: push left and right number to sumup
            "left": self.left,
            "right": self.right,
            "correct_answer": self.correct_answer,
        }

post_save.connect(Task.post_create, sender = Task)
