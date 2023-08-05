"""
Handle the UI for extra assets:
"""

import pymel.core as pm
from ciomaya.lib import const as k
from ciopath.gpath import Path
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI."""
    attr = pm.Attribute(node_attr)
    with AEcommon.ae_template():

        form = pm.formLayout("ddFormName", nd=100)

        field = pm.textFieldGrp("destinationField", label="Destination Directory")
        label = pm.layout(field, q=True, childArray=True)[0]
        pm.popupMenu(parent=label)
        pm.menuItem(label="Reset")

        button = pm.symbolButton(
            "destinationButton", image="SP_DirClosedIcon.png", width=24, height=24
        )
        pm.setParent("..")  # out of formLayout

        form.attachNone(button, "left")
        form.attachForm(button, "right", 2)
        form.attachForm(button, "top", 2)
        form.attachForm(button, "bottom", 2)

        form.attachForm(field, "left", 2)
        form.attachControl(field, "right", 2, button)
        form.attachForm(field, "top", 2)
        form.attachForm(field, "bottom", 2)

        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""
    widgets = _get_widgets()

    attr = pm.Attribute(node_attr)
    val = attr.get()
    pm.textFieldGrp(
        widgets["field"],
        edit=True,
        text=val,
        changeCommand=pm.Callback(on_text_changed, widgets["field"], attr),
    )

    pm.symbolButton(
        widgets["button"],
        edit=True,
        command=pm.Callback(_on_browse_button, attr, widgets["field"]),
    )

    item = pm.popupMenu(widgets["popup_menu"], q=True, itemArray=True)[0]
    pm.menuItem(item, edit=True, command=pm.Callback(_on_reset, attr, widgets["field"]))


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)

    field_grp = AEcommon.find_ui("destinationField", parent)
    label = pm.layout(field_grp, q=True, childArray=True)[0]
    return {
        "field": field_grp,
        "button": AEcommon.find_ui("destinationButton", parent),
        "popup_menu": pm.control(label, q=True, popupMenuArray=True)[0],
    }


def _on_browse_button(attr, field):
    path = browse_for_dest_directory()
    if path:
        try:
            path = Path(path).fslash()
        except ValueError:
            pm.displayError("{} is not a valid path".format(path))
        attr.set(path)
        pm.textFieldGrp(field, edit=True, text=path)
        AEcommon.print_setAttr_cmd(attr)


def browse_for_dest_directory():

    project_path = pm.workspace.getPath()
    entries = pm.fileDialog2(
        caption="Choose Directory",
        okCaption="Choose",
        fileFilter="*",
        dialogStyle=2,
        fileMode=3,
        dir=project_path,
    )
    if entries:
        return entries[0]
    pm.displayWarning("No files Selected")


def on_text_changed(text_field, attribute):
    val = pm.textFieldGrp(text_field, q=True, text=True)
    try:
        val = Path(val).fslash()
    except ValueError:
        pm.displayError("{} is not a valid path".format(val))
    attribute.set(val)
    pm.textFieldGrp(text_field, edit=True, text=val)
    AEcommon.print_setAttr_cmd(attribute)


def _on_reset(attribute, text_field):
    attribute.set(k.DEFAULT_DESTINATION_DIR_TEMPLATE)
    pm.textFieldGrp(text_field, edit=True, text=k.DEFAULT_DESTINATION_DIR_TEMPLATE)
    AEcommon.print_setAttr_cmd(attribute)
