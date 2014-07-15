from django import forms
from django.forms.widgets import RadioSelect


class QuestionForm(forms.Form):
    def __init__(self, question, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields["answers"] = forms.ModelChoiceField(
            queryset=question.get_answers(),
            empty_label=None,
            widget=RadioSelect)
