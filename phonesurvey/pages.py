from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from django.forms import inlineformset_factory
from .forms import PhoneFormset
import json
from django.core import serializers

class Instructions(Page):
    def vars_for_template(self):
        var_dic = {"treatment": self.player.treatment,
                   "flat_fee": Constants.flat_fee,
                   "per_phone_fee": Constants.per_phone_fee,
                   "time_minutes": Constants.time / 60,
                   "demographics": self.player.demographics}
        return var_dic
        
class Phones(Page):
    timeout_seconds = Constants.time
  
    def get_queryset(self):
        return self.player.phones.all()

    def get_context_data(self, bounded_formset=None, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.get_queryset()
        if bounded_formset:
            formset = bounded_formset
        else:
            formset = PhoneFormset(instance=self.player, queryset=q)
        context['formset'] = formset
        return context

    def post(self):
        self.object = self.get_object()
        self.form = self.get_form(
            data=self.request.POST,
            files=self.request.FILES,
            instance=self.object)
        q = self.get_queryset()
        formset = PhoneFormset(self.request.POST,
                               instance=self.player,
                               queryset=q)
        
        if formset.is_valid():
            formset.save()
            
        if not formset.is_valid():
            for form in formset.forms:
                if form.is_valid():
                    form.save()
                else:
                    form.DELETE = True
            
            context = self.get_context_data() #pass unbound form at timeout
            context['last_form_counter'] = len(formset)
            return self.render_to_response(context)

        return super().post()

    def vars_for_template(self):
        var_dic = {"treatment": self.player.treatment,
                   "flat_fee": Constants.flat_fee,
                   "per_phone_fee": Constants.per_phone_fee,
                   "time_minutes": Constants.time / 60,
                   "demographics": self.player.demographics}
        return var_dic

    def before_next_page(self):
        if self.timeout_happened:
            pass
        self.player.set_payoff()
        self.player.dump_phones = json.dumps(
            [(p.name, p.number, p.residence)for p in self.player.phones.all()])


class FinishPage(Page):
    ...

page_sequence = [
    Instructions,
    Phones
]
