# -*- coding: utf-8 -*-

from pyrevit import forms
import urllib2
import json

URL = "https://raw.githubusercontent.com/jsaugusto/INTEGRAR-Tools/main/version.json"

try:
    resposta = urllib2.urlopen(URL)
    dados = json.loads(resposta.read())

    forms.alert(
        "Versão disponível: {}".format(dados["version"]),
        title="Atualizar INTEGRAR"
    )

except Exception as erro:
    forms.alert(
        "Não foi possível verificar atualizações.\n\n{}".format(erro),
        title="Atualizar INTEGRAR"
    )