# -*- coding: utf-8 -*-
"""
ENERGIA PB--03 - pyRevit / Revit 2027

O script:
1) Confere se existe o nivel PB--03.
2) Salva o projeto atual.
3) Cria uma copia TEMP do RVT.
4) Na copia TEMP, remove todos os MEP Spaces colocados fora do PB--03.
5) Mantem todos os Spaces do PB--03.
6) Nao altera Spaces em arquivos vinculados.

Depois, crie normalmente o Modelo de Energia no Revit.
Ao terminar, feche a copia TEMP e volte ao arquivo original.
"""

import os
import re
from datetime import datetime

from pyrevit import revit, DB, forms, script
from System.Collections.Generic import List


# ============================================================
# CONFIGURACAO
# ============================================================

TARGET_LEVEL_NAME = "PB--03"


# ============================================================
# FUNCOES
# ============================================================

def safe_filename(text):
    """Remove caracteres invalidos de nome de arquivo."""
    return re.sub(r'[<>:"/\\|?*]+', "_", text).strip()


def get_desktop():
    """Retorna a pasta Desktop do usuario."""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.isdir(desktop):
        return desktop
    return os.path.expanduser("~")


def find_level(doc, level_name):
    levels = DB.FilteredElementCollector(doc)\
               .OfClass(DB.Level)\
               .WhereElementIsNotElementType()\
               .ToElements()

    for level in levels:
        if level.Name.strip() == level_name:
            return level
    return None


def get_placed_spaces(doc):
    """Coleta somente MEP Spaces colocados no modelo atual."""
    spaces = DB.FilteredElementCollector(doc)\
               .OfCategory(DB.BuiltInCategory.OST_MEPSpaces)\
               .WhereElementIsNotElementType()\
               .ToElements()

    result = []
    for space in spaces:
        try:
            # Space nao colocado normalmente nao possui Location valida.
            if space.Location is None:
                continue

            # Area > 0 ajuda a ignorar Spaces nao colocados/invalidos.
            try:
                if space.Area <= 0:
                    continue
            except:
                pass

            result.append(space)
        except:
            pass

    return result


# ============================================================
# INICIO
# ============================================================

doc = revit.doc

if doc is None:
    forms.alert(
        "Nenhum projeto do Revit esta aberto.",
        title="Energia - PB--03",
        warn_icon=True
    )
    script.exit()

if doc.IsFamilyDocument:
    forms.alert(
        "Este comando deve ser executado em um projeto, nao em uma familia.",
        title="Energia - PB--03",
        warn_icon=True
    )
    script.exit()


# ============================================================
# LOCALIZA O NIVEL
# ============================================================

target_level = find_level(doc, TARGET_LEVEL_NAME)

if target_level is None:
    forms.alert(
        "Nao encontrei o nivel '{}'.\n\n"
        "Confira se o nome esta exatamente igual no Revit.".format(TARGET_LEVEL_NAME),
        title="Energia - PB--03",
        warn_icon=True
    )
    script.exit()


# ============================================================
# CONTA OS SPACES ANTES DE FAZER QUALQUER ALTERACAO
# ============================================================

placed_spaces = get_placed_spaces(doc)

spaces_keep = []
spaces_remove = []

for space in placed_spaces:
    try:
        if space.LevelId == target_level.Id:
            spaces_keep.append(space)
        else:
            spaces_remove.append(space)
    except:
        pass

if len(spaces_keep) == 0:
    forms.alert(
        "O nivel '{}' existe, mas nao encontrei nenhum MEP Space colocado nele.\n\n"
        "Nada foi alterado.".format(TARGET_LEVEL_NAME),
        title="Energia - PB--03",
        warn_icon=True
    )
    script.exit()

if len(spaces_remove) == 0:
    forms.alert(
        "Todos os MEP Spaces colocados ja pertencem ao nivel '{}'.\n\n"
        "Nao ha Spaces de outros niveis para remover.".format(TARGET_LEVEL_NAME),
        title="Energia - PB--03"
    )
    script.exit()


# ============================================================
# CONFIRMACAO
# ============================================================

msg = (
    "Nivel que sera mantido: {0}\n\n"
    "Spaces mantidos: {1}\n"
    "Spaces de outros niveis que serao removidos da COPIA TEMP: {2}\n\n"
    "O arquivo original nao sera alterado.\n"
    "O Revit sera salvo primeiro e depois mudara para uma copia TEMP.\n\n"
    "Continuar?"
).format(TARGET_LEVEL_NAME, len(spaces_keep), len(spaces_remove))

if not forms.alert(
    msg,
    title="Criar modelo temporario - {}".format(TARGET_LEVEL_NAME),
    yes=True,
    no=True
):
    script.exit()


# ============================================================
# SALVA O ORIGINAL
# ============================================================

try:
    # Se houver caminho valido, salva o estado atual antes do Save As.
    # Em alguns modelos cloud/workshared o Save pode ter regras proprias;
    # nesse caso o erro e tratado antes de qualquer Space ser apagado.
    if doc.PathName:
        doc.Save()
except Exception as ex:
    forms.alert(
        "Nao consegui salvar o arquivo original antes de criar a copia TEMP.\n\n"
        "Nenhum Space foi removido.\n\n"
        "Erro:\n{}".format(ex),
        title="Energia - PB--03",
        warn_icon=True
    )
    script.exit()


# ============================================================
# CRIA A COPIA TEMP
# ============================================================

desktop = get_desktop()

base_title = safe_filename(os.path.splitext(doc.Title)[0])
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

temp_name = "{}_ENERGIA_{}_TEMP_{}.rvt".format(
    base_title,
    safe_filename(TARGET_LEVEL_NAME),
    timestamp
)

temp_path = os.path.join(desktop, temp_name)

save_options = DB.SaveAsOptions()
save_options.OverwriteExistingFile = False

# Tenta preservar corretamente modelos com worksharing.
if doc.IsWorkshared:
    try:
        ws_options = DB.WorksharingSaveAsOptions()
        # Mantem a copia como modelo workshared sem transforma-la
        # deliberadamente em novo central.
        ws_options.SaveAsCentral = False
        save_options.SetWorksharingOptions(ws_options)
    except:
        pass

try:
    doc.SaveAs(temp_path, save_options)
except Exception as ex:
    forms.alert(
        "Nao consegui criar a copia TEMP.\n\n"
        "Nenhum Space foi removido.\n\n"
        "Se o projeto estiver em ACC/BIM 360 ou tiver configuracao especial "
        "de compartilhamento, faca primeiro um Save As manual para um RVT local "
        "e rode o comando novamente.\n\n"
        "Erro:\n{}".format(ex),
        title="Energia - PB--03",
        warn_icon=True
    )
    script.exit()


# ============================================================
# REMOVE OS SPACES DE OUTROS NIVEIS SOMENTE NA COPIA TEMP
# ============================================================

ids_to_delete = List[DB.ElementId]()

for space in spaces_remove:
    try:
        # Os elementos continuam validos depois do SaveAs porque o documento
        # aberto e o mesmo; somente o caminho do arquivo mudou.
        ids_to_delete.Add(space.Id)
    except:
        pass

deleted_count = 0

try:
    with revit.Transaction(
        "TEMP - manter somente Spaces do {}".format(TARGET_LEVEL_NAME),
        doc=doc
    ):
        if ids_to_delete.Count > 0:
            deleted_ids = doc.Delete(ids_to_delete)
            deleted_count = deleted_ids.Count

    # Salva a copia TEMP ja com a limpeza feita.
    doc.Save()

except Exception as ex:
    forms.alert(
        "A copia TEMP foi criada, mas ocorreu um erro ao remover os Spaces.\n\n"
        "Feche esta copia e volte ao arquivo original.\n\n"
        "Erro:\n{}".format(ex),
        title="Energia - PB--03",
        warn_icon=True
    )
    script.exit()


# ============================================================
# FINAL
# ============================================================

forms.alert(
    "PRONTO.\n\n"
    "Voce esta trabalhando na COPIA TEMP.\n\n"
    "Nivel mantido: {0}\n"
    "Spaces mantidos no nivel: {1}\n"
    "Spaces selecionados para remocao: {2}\n"
    "Elementos removidos pelo Revit: {3}\n\n"
    "Arquivo TEMP:\n{4}\n\n"
    "Agora crie o Modelo de Energia normalmente.\n\n"
    "Quando terminar, feche esta copia TEMP e abra novamente "
    "o seu arquivo original.".format(
        TARGET_LEVEL_NAME,
        len(spaces_keep),
        len(spaces_remove),
        deleted_count,
        temp_path
    ),
    title="Energia - PB--03"
)
