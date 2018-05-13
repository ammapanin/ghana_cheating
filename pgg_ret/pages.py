from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants


class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1
    
    def vars_for_template(self):
        n_other_group = Constants.players_per_group - 1
        n_rounds_audit = Constants.switch_audit_round - 1
        var_dic = {"n_other_group_members": n_other_group,
                   "n_rounds_audit": n_rounds_audit}
        
        div_10 = [(p * 100) % 10 == 0 for p in Constants.probs]
        if sum(div_10) == len(div_10):
            base = 10
        else:
            base = 100
        prob_text = "<b>{}/{}</b>{}".format("{}", base, {})
            
        for p in self.group.get_players():
            
            p0_text = " i.e. you will <b>never</b> be inspected"
            probs = p.participant.vars.get("prob_order")
                        
            for ix, p in enumerate(probs, 1):
                p_int = int(p * base)
                if p_int == 0:
                    p_extra = p0_text
                else:
                    p_extra = ""
                p_text = prob_text.format(p_int, p_extra)
                p_dic = {"audit_prob_{}".format(ix):
                         p_text}
                var_dic.update(p_dic)
                
            return var_dic
                  

class AuditChangeInstructions(Instructions):
    def is_displayed(self):
        return self.round_number == Constants.switch_audit_round

    # def vars_for_template(self):
    #     return Instructions.vars_for_template()
        #for p in self.group.get_players():
        #    return {'prob_chance': p.audit_prob}

class WorkPage(Page):
    timer_text = 'Time left to complete this round:'
    timeout_seconds = Constants.task_time

    def before_next_page(self):
        self.player.set_ret_earnings()
        self.player.dump_tasks()

class Declaration(Page):
    form_model = 'player'
    form_fields = ['declaration']

    def declaration_max(self):
        return self.player.ret_earning

class BeforeResultsWP(WaitPage):
    def after_all_players_arrive(self):
        self.group.calculate_pgg()
        for p in self.group.get_players():
            p.set_payoff()

class Results(Page):
    def vars_for_template(self):
        return {'total_deduction': self.player.deduction + self.player.fine}


page_sequence = [
    Instructions,
    AuditChangeInstructions,
    WorkPage,
    Declaration,
    BeforeResultsWP,
    # Results,
]
