# -*- coding: utf-8 -*-

from pyrevit import forms
import urllib2
import json
import os
import tempfile

# Caminho do version.json local
LOCAL_VERSION_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "version.json"
    )
)

# Arquivos remotos
REMOTE_VERSION_URL = (
    "https://raw.githubusercontent.com/"
    "jsaugusto/INTEGRAR-Tools/main/version.json"
)

ZIP_URL = (
    "https://github.com/"
    "jsaugusto/INTEGRAR-Tools/"
    "archive/refs/heads/main.zip"
)


def version_tuple(version):
    return tuple(int(x) for x in version.split("."))


try:
    # Lê a versão instalada
    with open(LOCAL_VERSION_FILE, "r") as arquivo:
        local_version = json.load(arquivo)["version"]

    # Lê a versão do GitHub
    resposta = urllib2.urlopen(REMOTE_VERSION_URL)
    remote_version = json.loads(resposta.read())["version"]

    # Verifica se existe atualização
    if version_tuple(remote_version) > version_tuple(local_version):

        confirmar = forms.alert(
            u"Nova versão disponível!\n\n"
            u"Instalada: {}\n"
            u"Disponível: {}\n\n"
            u"Deseja baixar a atualização?".format(
                local_version,
                remote_version
            ),
            title="Atualizar INTEGRAR",
            yes=True,
            no=True
        )

        if confirmar:
            # Cria o caminho temporário do ZIP
            zip_path = os.path.join(
                tempfile.gettempdir(),
                "INTEGRAR-Tools-main.zip"
            )

            # Baixa o ZIP
            resposta_zip = urllib2.urlopen(ZIP_URL)

            with open(zip_path, "wb") as arquivo_zip:
                arquivo_zip.write(resposta_zip.read())

            forms.alert(
                u"Atualização baixada com sucesso!\n\n"
                u"Arquivo salvo temporariamente em:\n{}".format(zip_path),
                title="Atualizar INTEGRAR"
            )

    else:
        forms.alert(
            u"Você já está utilizando a versão mais recente ({})".format(
                local_version
            ),
            title="Atualizar INTEGRAR"
        )

except Exception as erro:
    forms.alert(
        u"Erro ao verificar ou baixar a atualização.\n\n{}".format(erro),
        title="Atualizar INTEGRAR"
    )