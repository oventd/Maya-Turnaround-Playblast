"""Turnaround camera helpers for Maya.

Given a camera and an "asset" node, compute a (tx, ty, tz) on +Z that frames
the asset with a small padding, using the camera's horizontal/vertical FOV.
Public API: get_turnaround_camera_pos(camera_name).
"""

import math
import maya.api.OpenMaya as om
import maya.cmds as cmds

def _get_fov(cam_node):
    """Return (h_fov, v_fov) in degrees for a camera transform or shape.

    Args:
        cam_node (str): Camera transform or camera shape name.

    Returns:
        tuple[float, float]: Horizontal and vertical FOV (degrees).
    """
    node_type = cmds.nodeType(cam_node) if cmds.objExists(cam_node) else None
    if node_type == "transform":
        shapes = cmds.listRelatives(cam_node, shapes=True, type="camera") or []
        if not shapes:
            raise ValueError("No camera shape under transform: {}".format(cam_node))
        cam_shape = shapes[0]
    else:
        cam_shape = cam_node

    h_fov = cmds.camera(cam_shape, q=True, hfv=True)
    v_fov = cmds.camera(cam_shape, q=True, vfv=True)
    return h_fov, v_fov

def get_turnaround_camera_pos(camera_name="camera1", asset_grp="asset"):
    """Compute (tx, ty, tz) on +Z to frame the "asset" node with padding.

    Args:
        camera_name (str): Camera transform or shape to query FOV from.

    Returns:
        tuple[float, float, float] | None: Camera position (tx, ty, tz), or
        None if the asset node is missing.
    """
    if not cmds.objExists(asset_grp):
        cmds.warning("Asset node not found: {}".format(asset_grp))
        return None

    if not cmds.objExists(camera_name):
        cmds.warning("Camera not found: {}".format(camera_name))
        return None

    # Find the asset node.
    sel = om.MSelectionList()
    sel.add(asset_grp)
    asset_dag = sel.getDagPath(0)

    # Asset world-space bounding box.
    bb = om.MFnDagNode(asset_dag).boundingBox

    # Half extents.
    half_w = bb.width * 0.5
    half_h = bb.height * 0.5
    half_d = bb.depth * 0.5

    # Horizontal radius in XZ (turnaround silhouette).
    r_h = math.hypot(half_w, half_d)

    # FOV in radians (clamped to avoid zero).
    h_fov, v_fov = _get_fov(camera_name)
    h = math.radians(max(h_fov, 1e-6))
    v = math.radians(max(v_fov, 1e-6))

    # Required distances to fit horizontally and vertically.
    d_h = r_h / math.tan(0.5 * h) + r_h
    d_v = half_h / math.tan(0.5 * v) + r_h

    # Use the larger to satisfy both.
    distance = max(d_h, d_v)

    # Small padding to avoid tight framing.
    padding = 1.10

    tz = distance * padding
    ty = bb.center.y
    return (0.0, ty, tz)
