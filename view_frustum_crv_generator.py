import math
import maya.api.OpenMaya as om
import maya.cmds as cmds

def get_resolution():
    return cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")

def _get_fov(cam_shape):
    h_fov = cmds.camera(cam_shape, q=True, hfv=True)
    v_fov = cmds.camera(cam_shape, q=True, vfv=True)
    return h_fov, v_fov

def _get_camera_dagpath(camera):
    if not isinstance(camera, str):
        return
    if not cmds.objExists(camera):
        return
    sel = om.MSelectionList()
    sel.add(camera)
    dag = sel.getDagPath(0)
    return dag

def get_frustum_plane_half_size(distance, h_fov, v_fov):
    half_w = distance * math.tan(math.radians(h_fov * 0.5))
    half_h = distance * math.tan(math.radians(v_fov * 0.5))
    return half_w, half_h

def get_frustum_plane_points(distance, h_fov, v_fov):
    half_w, half_h = get_frustum_plane_half_size(distance, h_fov, v_fov)
    p1 = om.MPoint(half_w, half_h, -distance)
    p2 = om.MPoint(-half_w, half_h, -distance)
    p3 = om.MPoint(-half_w, -half_h, -distance)
    p4 = om.MPoint(half_w, -half_h, -distance)
    return p1, p2, p3, p4

def apply_camera_offset_to_points(cam_dag, points):
    for p in points:
        p = p * cam_dag.inclusiveMatrix()
    return
def make_camera_frustum_curves(camera_name="camera1",
                               near_distance=1.0,
                               far_distance=10.0):
    h_fov, v_fov = _get_fov(camera_name)
    cam_dag = _get_camera_dagpath(camera_name)

    near_points = get_frustum_plane_points(near_distance, h_fov, v_fov)
    far_points = get_frustum_plane_points(far_distance, h_fov, v_fov)

    near_w = [p*cam_dag.inclusiveMatrix() for p in near_points]
    far_w = [p*cam_dag.inclusiveMatrix() for p in far_points]

    def _make_closed_curve(points, crv_name):
        pts = [(p.x, p.y, p.z) for p in points] + [(points[0].x, points[0].y, points[0].z)]
        if cmds.objExists(crv_name):
            cmds.delete(crv_name)
        return cmds.curve(p=pts, d=1, n=crv_name)

    # Create group
    grp_name = f"{camera_name}_grp"
    if cmds.objExists(grp_name):
        grp = grp_name
    else:
        grp = cmds.group(em=True, n=grp_name)
    # Create crv
    near_crv  = _make_closed_curve(near_w,  "{}_near".format(camera_name))
    far_crv   = _make_closed_curve(far_w,   "{}_far".format(camera_name))
    top_crv   = _make_closed_curve([near_w[0], near_w[1], far_w[1],  far_w[0]],  "{}_top".format(camera_name))
    left_crv  = _make_closed_curve([near_w[1], near_w[2], far_w[2],  far_w[1]],  "{}_left".format(camera_name))
    bottom_crv= _make_closed_curve([near_w[2], near_w[3], far_w[3],  far_w[2]],  "{}_bottom".format(camera_name))
    right_crv = _make_closed_curve([near_w[3], near_w[0], far_w[0],  far_w[3]],  "{}_right".format(camera_name))
    # Parent
    for crv in (near_crv, far_crv, top_crv, left_crv, bottom_crv, right_crv):
        # curve command returns shape parent; ensure we parent the transform
        xform = cmds.listRelatives(crv, p=True, f=False) or [crv]
        cmds.parent(xform[0], grp)
    try:
        cmds.parent(grp, camera_name)
    except:
        pass

