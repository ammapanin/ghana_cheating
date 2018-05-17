from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

from dg.models import Player as dgPlayer, Constants as dgConstants
from phonesurvey.models import Player as phonesurveyPlayer, Constants as phonesurveyConstants
from pgg_ret.models import Player as pgg_retPlayer, Constants as pgg_retConstants
from questionnaire.models import Player as questionnairePlayer, Constants as qConstants
from cem.models import Player as cemPlayer, Constants as cemConstants

MODULE_DIC = {"cem": (cemPlayer, cemConstants.show_app_name),
              "dg": (dgPlayer, dgConstants.show_app_name),
              "pgg_ret":( pgg_retPlayer,
                          pgg_retConstants.show_app_name),
              "phonesurvey": (phonesurveyPlayer,
                              phonesurveyConstants.show_app_name),
              "questionnaire": (questionnairePlayer,
                                qConstants.show_app_name)} 
        
class BeginPayment(Page):
    pass
        
class cemPay(Page):
    def vars_for_template(self):
        participant = self.participant
        player = cemPlayer.objects.get(participant = participant)

        appC = cemConstants
        show_name =  "Module Results: {}"
        mod_pay_name = show_name.format(appC.show_app_name)
        # unzip <cem_choices> into list of lists
        choices = [list(t)
                   for t in zip(*participant.vars['cem_choices'])]
        indices = choices[0]

        # payoff information
        index_to_pay = participant.vars['cem_index_to_pay']
        round_to_pay = indices.index(index_to_pay) + 1
        cem_choices = participant.vars['cem_choices']
        choice_to_pay = cem_choices[round_to_pay - 1]

        if player.option_to_pay == "A":
            acc_rej = ("accept",)
        else:
            acc_rej = ("reject",)
        
        return {'choice_to_pay': [choice_to_pay],
                'option_to_pay': player.option_to_pay,
                'accept_reject': acc_rej,
                'payoff': player.payoff,
                "module_pay_name": mod_pay_name}

class dgPay(Page):
    def vars_for_template(self):
        participant = self.participant
        player = dgPlayer.objects.get(participant = participant)

        
        appC = dgConstants
        show_name =  "Module Results: {}"
        mod_pay_name = show_name.format(appC.show_app_name)

        sender = player.group.get_player_by_role("sender")
        amount_sent = sender.dg_decision
        
        if player.is_dictator:
            p_role = "Player 1"
        else:
            p_role = "Player 2"
        return {"player_role": p_role,
                "payoff": player.payoff,
                "amount_sent": amount_sent,
                "endowment": dgConstants.endowment,
                "mod_pay_name": mod_pay_name}

class pggPay(Page):
    def vars_for_template(self):
        participant = self.participant

        appC = pgg_retConstants
        show_name =  "Module Results: {}"
        mod_pay_name = show_name.format(appC.show_app_name)

        pay_round = self.participant.vars["pay_round"]
        player = pgg_retPlayer.objects.get(participant = participant,
                                           round_number = pay_round)
        group = player.group
        
        return {'player': player,
                'group': group,
                'total_deduction': player.deduction + player.fine,
                'module_pay_name': mod_pay_name}

 
class questionnairePay(Page):
    def vars_for_template(self):
        participant = self.participant
        player = questionnairePlayer.objects.get(
            participant = participant)

        appC = qConstants
        show_name =  "Module Results: {}"
        mod_pay_name = show_name.format(appC.show_app_name)

        return {"payoff": player.payoff,
                "die_roll": player.die_roll,
                "die_conversion": qConstants.die_conversion,
                "module_pay_name": mod_pay_name}

class phonesurveyPay(Page):
    def vars_for_template(self):
        participant = self.participant
        player = phonesurveyPlayer.objects.get(
            participant = participant)

        appC = phonesurveyConstants
        show_name =  "Module Results: {}"
        mod_pay_name = show_name.format(appC.show_app_name)

        return {"payoff": player.payoff,
                "treatment": player.treatment,
                "flat_pay": phonesurveyConstants.flat_fee,
                "per_phone_pay": phonesurveyConstants.per_phone_fee,
                "n_phones": player.num_phones,
                "module_pay_name": mod_pay_name}

class Payment(Page):
    form_model = 'player'
    form_fields = ["payment_phone_1",
                   "payment_phone_2",
                   "payment_confirm"]
    
    def after_all_players_arrive(self):
        p, q = calculate_payments()
        self.player.payoffs = p
        self.player.total_additional = q
        print(self.player.payoffs)
        print("/n/n/n/n")
        print("my self")
        
    def payment_phone_2_error_message(self, value):
        phone_1 = self.player.payment_phone_1
        if not str(phone_1) == str(value):
            return "Numbers must match."

    def payment_confirm_error_message(self, value):
        if not value == self.participant.payoff:
            return "Please enter your correct additional earnings."
        
    def vars_for_template(self):
        apps_to_pay = self.session.config["app_sequence"][0:-1]
        modules = [(app_name, MODULE_DIC.get(app_name))
                   for app_name in apps_to_pay]
        
        payoffs = list()
        for app_name, (appPlayer, show_app_name) in modules:
            p = self.participant
            print(app_name)
            if app_name == "pgg_ret":
                player = appPlayer.objects.get(participant = p,
                                               round_number = 2)
            else:
                player = appPlayer.objects.get(participant = p)
            payoff = player.payoff
            payoffs.append((show_app_name, payoff))

        payoffs = [payoff for payoff in payoffs if payoff != None]
        total_additional = p.payoff

        return {"payoffs": payoffs,
                "total": total_additional,
                "participation": self.session.config["participation_fee"]
        }


page_sequence = [
    dgPay,
    pggPay,
    cemPay,
    phonesurveyPay,
    questionnairePay,
    Payment
]
