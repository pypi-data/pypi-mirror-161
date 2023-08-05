import os
import pymel.core as pm
from ciomaya.lib import layer_utils
from ciopath.gpath import Path
from ciotemplate.expander import Expander


def destination_context(node):
    """
    Create data to be used for token generation.

    We do not evaluate the destination path in order to contribute to the result. Therefore, the
    resulting context can be used to evaluate the destination path itself.

    Args:
        node (pm.PyNode):The ConductorRender node

    Returns:
        dict: a dictionary containing tokens and their values
    """

    ws = pm.Workspace()
    images_dir = ws.fileRules.get("images", "images")
    images_dir = ws.expandName(images_dir)

    workspace_dir = Path(ws.getPath()).fslash(with_drive=False)

    context = {
        "Camera": get_renderable_cameras(),
        "Scene": "undefined",
        "SceneFile": "undefined",
        "Object": node.name(),
        "RenderLayer": layer_utils.get_current_layer_name(),
        "WorkspacePath": workspace_dir,
        "Renderer": node.attr("currentRenderer").get(),
        "ConductorVersion": pm.moduleInfo(version=True, moduleName="conductor"),
        "ImagesPath": images_dir,
    }

    file_name = pm.sceneName()
    scene_name = os.path.splitext(os.path.split(file_name)[1])[0]

    if file_name:
        context["Scene"] = scene_name
        context["SceneFile"] = Path(file_name).fslash(with_drive=False)

    lowercase_context = {}
    for key in context:
        key_lower = key.lower()
        if not key_lower in context:
            lowercase_context[key_lower] = context[key]
    context.update(lowercase_context)
    return context


def job_context(node):
    """
    Create data to be used for token generation.

    We do evaluate the destination path in order to contribute to the result. Therefore, the
    resulting context cannot be used to evaluate the destination path itself. It can be used to
    evaluate title, metadata, and so on.

    Args:
        node (pm.PyNode):The ConductorRender node

    Returns:
        dict: a dictionary containing tokens and their values
    """
    context = destination_context(node)
    expander = Expander(**context)
    output_path = expander.evaluate(node.attr("destinationDirectory").get())
    context["OutputPath"] = Path(output_path.strip()).fslash(with_drive=False)
    return context


def task_context(chunk, in_job_context):
    """
    Create data to be used for token generation at the task level.

    This is the union of job context and the data from the current chunk.

    Args:
        node (pm.PyNode):The ConductorRender node

    Returns:
        dict: a dictionary containing tokens and their values
    """
    context = {
        "start": str(chunk.start),
        "end": str(chunk.end),
        "step": str(chunk.step),
        "chunk_length": str(len(chunk)),
    }
    context.update(in_job_context)
    return context


def get_renderable_cameras():
    """Get a comma-separated list of renderable cameras."""
    return ",".join([c.name() for c in pm.ls(type="camera") if c.attr("renderable").get()])
