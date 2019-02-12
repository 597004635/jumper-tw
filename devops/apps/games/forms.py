from django import forms
from .models import GameServer
from django.forms import widgets


class GameServerfileForm(forms.ModelForm):
    class Meta:
        model = GameServer
        fields = "__all__"


class GameServerUpdateForm(forms.ModelForm):
    class Meta:
        model = GameServer
        fields = ['hostname','servername','inner_ip','db_ip']
