# -*- coding: utf-8 -*-

from pyrevit import forms
import urllib2
import json
import os

# Caminho do version.json local
LOCAL_VERSION_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "version.json")
)

# URL do version.json no GitHub
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/jsaugusto/INTEGRAR-Tools/main/version.json"


def version_tuple(version):
    return tuple(int(x) for x in version.split("."))


try:
    # Lê versão local
    with open(LOCAL_VERSION_FILE, "r") as f:
        local_version = json.load(f)["version"]

    # Lê versão remota
    response = urllib2.urlopen(REMOTE_VERSION_URL)
    remote_data = json.loads(response.read())
    remote_version = remote_data["version"]

    # Compara versões
    if version_tuple(remote_version) > version_tuple(local_version):
        forms.alert(
            u"Nova versão disponível!\n\n"
            u"Instalada: {}\n"
            u"Disponível: {}".format(
                local_version,
                remote_version
            ),
            title="Atualizar INTEGRAR"
        )
    else:
        forms.alert(
            u"Você já está utilizando a versão mais recente ({})".format(local_version),
            title="Atualizar INTEGRAR"
        )

except Exception as e:
    forms.alert(
        u"Erro ao verificar atualização.\n\n{}".format(e),
        title="Atualizar INTEGRAR"
    )