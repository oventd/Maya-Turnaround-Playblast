import math
import maya.api.OpenMaya as om
import maya.cmds as cmds
import numpy as np

def get_resolution():
    return cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")

def get_fov(cam_shape):
    h_fov = cmds.camera(cam_shape, q=True, hfv=True)
    v_fov = cmds.camera(cam_shape, q=True, vfv=True)
    return h_fov, v_fov

def get_camera_dagpath(camera):
    if not isinstance(camera, str):
        return
    if not cmds.objExists(camera):
        return
    sel = om.MSelectionList()
    sel.add(camera)
    dag = sel.getDagPath(0)
    return dag
    
def get_translate_rotate_from_dagpath(dag_path, return_degrees=True):
    m = dag_path.inclusiveMatrix()
    tm = om.MTransformationMatrix(m)
    t = tm.translation(om.MSpace.kWorld)
    q = tm.rotation()
    trans = (t.x, t.y, t.z)
    rot = (q.x, q.y, q.z)
    if return_degrees:
        rot = (math.degrees(rot[0]), math.degrees(rot[1]), math.degrees(rot[2]))
    return trans, rot

def get_frustum_plane_half_size(distance, h_fov, v_fov):
    half_w = distance * math.tan(math.radians(h_fov * 0.5))
    half_h = distance * math.tan(math.radians(v_fov * 0.5))
    return half_w, half_h

def get_frustum_plane_points(half_w, half_h, distance):
    p1 = (half_w, half_h, -distance)
    p2 = (-half_w, half_h, -distance)
    p3 = (-half_w, -half_h, -distance)
    p4 = (half_w, -half_h, -distance)
    return p1, p2, p3, p4

def apply_camera_offset_to_points(cam_dag, points):
    # cam_translate = 
    return

camera_name = "camera1"
h_fov, v_fov = get_fov(camera_name)
cam_dag = get_camera_dagpath(camera_name)
cam_fn_camera = om.MFnCamera(cam_dag)

cam_fn_transfrom = om.MFnTransform(cam_dag.transform())
cam_trans = cam_fn_transfrom.transformation()
# print(cam_trans.translation())
print(get_translate_rotate_from_dagpath(cam_dag, return_degrees=False))
print(get_translate_rotate_from_dagpath(cam_dag, return_degrees=True))
print(cmds.getAttr("camera1.translateX"), cmds.getAttr("camera1.translateY"), cmds.getAttr("camera1.translateZ"))
print(cmds.getAttr("camera1.rotateX"), cmds.getAttr("camera1.rotateY"), cmds.getAttr("camera1.rotateZ"))



near = 10
far = 100

print(get_frustum_plane_half_size(near, h_fov, v_fov))
print(get_frustum_plane_half_size(far, h_fov, v_fov))



