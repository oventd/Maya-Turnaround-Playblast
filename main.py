import maya.api.OpenMaya as om
import maya.cmds as cmds
import math

def get_dagpath_if_exists(name):
    """Return MDagPath if node exists, otherwise None."""
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return sel.getDagPath(0)
    except RuntimeError:
        return None
    
def _get_camera_shape(cam):
    """Return camera shape from a transform or shape name, else None."""
    if not cmds.objExists(cam):
        return None
    if cmds.nodeType(cam) == "camera":
        return cam
    shapes = cmds.listRelatives(cam, shapes=True, type="camera") or []
    return shapes[0] if shapes else None

def _get_fov(cam):
    """Return (h_fov, v_fov) in degrees for the given camera (transform or shape)."""
    cam_shape = _get_camera_shape(cam)
    if not cam_shape:
        return None, None
    h_fov = cmds.camera(cam_shape, q=True, hfv=True)
    v_fov = cmds.camera(cam_shape, q=True, vfv=True)
    return h_fov, v_fov

def main(*args):
    camera_name = "camera1"
    if not cmds.objExists(camera_name):
        return

    target = "asset"
    if not cmds.objExists(target):
        return

    # Use world-space bounding box for accurate framing
    xmin, ymin, zmin, xmax, ymax, zmax = cmds.exactWorldBoundingBox(target)
    center_x = (xmin + xmax) * 0.5
    center_y = (ymin + ymax) * 0.5
    center_z = (zmin + zmax) * 0.5

    half_width = (xmax - xmin) * 0.5
    half_height = (ymax - ymin) * 0.5

    # Center camera horizontally and vertically on the asset
    cmds.setAttr(f"{camera_name}.translateX", center_x)
    cmds.setAttr(f"{camera_name}.translateY", center_y)

    h_fov, v_fov = _get_fov(camera_name)
    if h_fov is None or v_fov is None:
        return

    # Compute distance required to fit both width and height
    d_h = half_width / math.tan(math.radians(h_fov * 0.5)) if h_fov > 0 else 0
    d_v = half_height / math.tan(math.radians(v_fov * 0.5)) if v_fov > 0 else 0
    distance = max(d_h, d_v)

    # Place camera in front of the asset along +Z, assuming default orientation
    cmds.setAttr(f"{camera_name}.translateZ", center_z + distance)


    


    

    
import sys
sys.path.append(r"D:\code\turnaround_distance")
import view_frustum_crv_generator
main()
view_frustum_crv_generator.make_camera_frustum_curves()
