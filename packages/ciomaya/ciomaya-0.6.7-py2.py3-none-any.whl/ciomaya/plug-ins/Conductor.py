import sys

import maya.api.OpenMaya as om
import ciocore.loggeria
from ciocore import data as coredata
import maya.cmds as mc


PYMEL_MSG = "PyMEL is not installed.\n"
PYMEL_MSG += "The Conductor Plugin requires the PyMEL Python package.\n"
PYMEL_MSG += "Please follow the instructions at the link below to install it.\n"
PYMEL_MSG += "Alternatively, reinstall Maya and make sure the PyMEL option is selected."
PYMEL_URL = "https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2022/ENU/Maya-Scripting/files/GUID-2AA5EFCE-53B1-46A0-8E43-4CD0B2C72FB4-htm.html"


def pymelConfirmWindow():

    form = mc.setParent(q=True)
    mc.formLayout(form, e=True, width=300)

    link_label = '<a href="{}"><font color=#ec6a17 size=4>Autodesk: Installing PyMEL</font></a>'.format(PYMEL_URL)

    msg_tf = mc.text(label=PYMEL_MSG)
    link_tf = mc.text(hl=True, label=link_label)
 
    mc.formLayout(form, edit=True,attachForm=[ (msg_tf, 'top', 5)])
    mc.formLayout(form, edit=True,attachForm=[  (msg_tf, 'left', 5)])
    mc.formLayout(form, edit=True,attachForm=[  (msg_tf, 'right', 5)])
    mc.formLayout(form, edit=True,attachNone=[ (msg_tf, 'bottom')])

    mc.formLayout(form, edit=True,attachControl=[ (link_tf, 'top', 5, msg_tf)])
    mc.formLayout(form, edit=True,attachForm=[  (link_tf, 'left', 5)])
    mc.formLayout(form, edit=True,attachForm=[  (link_tf, 'right', 5)])
    mc.formLayout(form, edit=True,attachForm=[ (link_tf, 'bottom', 5)])

def check_pymel():
    try:
        import pymel
        return True
    except ModuleNotFoundError:
        mc.layoutDialog(ui=pymelConfirmWindow)
        mc.warning(PYMEL_MSG)
        mc.warning(PYMEL_URL)
    return False

def maya_useNewAPI():
    pass


def initializePlugin(obj):
    # Use "0.6.7 to cause the version to be replaced at build time."
 
    if not check_pymel():
        return

    plugin = om.MFnPlugin(obj, "Conductor", "0.6.7", "Any")
    # ciomaya imports must come after check_pymel.
    from ciomaya.lib.nodes.conductorRender import conductorRender
    try:
        plugin.registerNode(
            "conductorRender",
            conductorRender.id,
            conductorRender.creator,
            conductorRender.initialize,
            om.MPxNode.kDependNode,
        )
    except:
        sys.stderr.write("Failed to register conductorRender\n")
        raise

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib import conductor_menu
    conductor_menu.load()

    coredata.init("maya-io")


def uninitializePlugin(obj):
    plugin = om.MFnPlugin(obj)

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib.nodes.conductorRender import conductorRender
    try:
        plugin.deregisterNode(conductorRender.id)
    except:
        sys.stderr.write("Failed to deregister conductorRender\n")
        raise

    # ciomaya imports must come after check_pymel.
    from ciomaya.lib import conductor_menu
    conductor_menu.unload()
