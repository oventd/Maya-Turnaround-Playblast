import maya.api.OpenMaya as om
import maya.cmds as cmds
import math
import sys
import imp
sys.path.append(r"D:\code\turnaround_distance")
import view_frustum_crv_generator
imp.reload(view_frustum_crv_generator)

def get_dagpath_if_exists(name):
    """Return MDagPath if node exists, otherwise None."""
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return sel.getDagPath(0)
    except RuntimeError:
        return None
    
def _get_fov(cam_shape):
    h_fov = cmds.camera(cam_shape, q=True, hfv=True)
    v_fov = cmds.camera(cam_shape, q=True, vfv=True)
    return h_fov, v_fov

def key_turnaround_camera(camera):
    if not cmds.objExists(camera):
        return
    cam_grp = cmds.group(camera, n="turnaround_camera_grp",r=False)

    for frame, value in [(1,0), (120,360)]:    
        cmds.setKeyframe(cam_grp, attribute='rotateY',t=frame,v=value)
        cmds.selectKey(cam_grp, time=(1, 120), attribute="rotateY")
        cmds.keyTangent(inTangentType="linear", outTangentType="linear")

def place_turnaround_camera(*args):
    camera_name = "camera1"
    camera_dag = get_dagpath_if_exists(camera_name)
    if not camera_dag:
        return

    dag = get_dagpath_if_exists("asset")
    if not dag:
        return
    
    fn_dag = om.MFnDagNode(dag)
    bbox = fn_dag.boundingBox
    
    cmds.setAttr(f"{camera_name}.translateY", bbox.center.y)

    max_bbox_v = bbox.height/2
    max_bbox_h = 0
    for size in [bbox.width/2, bbox.depth/2]:
        if abs(size) > max_bbox_h:
            max_bbox_h = abs(size)
    
    h_fov, v_fov = _get_fov(camera_name)
    distance = 0

    for fov, size, dis  in [(h_fov, max_bbox_h, max_bbox_v), (v_fov, max_bbox_v, max_bbox_h)]:
        d = size / math.tan(math.radians(fov * 0.5))
        if d > distance:
            distance = d+ dis*2 
    offset = 1.5
    cmds.setAttr(f"{camera_name}.translateZ", distance*offset)


cam_name = "camera1"
place_turnaround_camera()
cam_dist = cmds.getAttr(f"{cam_name}.translateZ")
view_frustum_crv_generator.make_camera_frustum_curves(far_distance=cam_dist)
cmds.select(cam_name, r=True)
# key_turnaround_camera(cam_name)