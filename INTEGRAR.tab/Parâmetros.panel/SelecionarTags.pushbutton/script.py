# -*- coding: utf-8 -*-

import clr  # type: ignore[import]
clr.AddReference('System')

from pyrevit import revit, DB, forms, script  # type: ignore[import]
from System.Collections.Generic import List  # type: ignore[import]

doc = revit.doc
uidoc = revit.uidoc
view = doc.ActiveView

# Elementos selecionados
selection_ids = uidoc.Selection.GetElementIds()

if not selection_ids:
    forms.alert(
        "Selecione um ou mais elementos primeiro.",
        title="Selecionar Tags"
    )
    script.exit()

ids_selecionados = {eid.IntegerValue for eid in selection_ids}

# Procura todas as tags da vista ativa
tags = (
    DB.FilteredElementCollector(doc, view.Id)
    .OfClass(DB.IndependentTag)
    .ToElements()
)

tags_encontradas = []

for tag in tags:

    try:
        ids = tag.GetTaggedLocalElementIds()
    except:
        ids = []

    for eid in ids:
        if eid.IntegerValue in ids_selecionados:
            tags_encontradas.append(tag.Id)
            break

if not tags_encontradas:
    forms.alert(
        "Nenhuma tag encontrada para os elementos selecionados.",
        title="Selecionar Tags"
    )
else:
    uidoc.Selection.SetElementIds(List[DB.ElementId](tags_encontradas))
