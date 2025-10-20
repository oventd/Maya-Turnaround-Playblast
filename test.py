# -*- coding: utf-8 -*-
import math
import maya.api.OpenMaya as om
import maya.cmds as cmds

INCH_TO_MM = 25.4

def get_camera_dagpath(cam_name):
    """Return MDagPath to a camera shape from transform or shape name."""
    sel = om.MSelectionList()
    sel.add(cam_name)
    dag = sel.getDagPath(0)
    if dag.node().hasFn(om.MFn.kTransform):
        fn = om.MFnDagNode(dag)
        for i in range(fn.childCount()):
            child = fn.child(i)
            if child.hasFn(om.MFn.kCamera):
                return om.MDagPath.getAPathTo(child)
        raise RuntimeError("No camera shape under transform: {}".format(cam_name))
    if not dag.node().hasFn(om.MFn.kCamera):
        raise RuntimeError("Node is not a camera: {}".format(cam_name))
    return dag

def _effective_aperture_mm(cam_shape_dag, image_aspect):
    """Return (eff_width_mm, eff_height_mm) using 'fill' fit vs image_aspect."""
    fn_cam = om.MFnCamera(cam_shape_dag)
    ap_w_mm = fn_cam.horizontalFilmAperture * INCH_TO_MM
    ap_h_mm = fn_cam.verticalFilmAperture   * INCH_TO_MM
    sensor_aspect = ap_w_mm / ap_h_mm
    if image_aspect > sensor_aspect:
        eff_h, eff_w = ap_h_mm, ap_h_mm * image_aspect
    else:
        eff_w, eff_h = ap_w_mm, ap_w_mm / image_aspect
    return eff_w, eff_h

def _fov_from_aperture(focal_mm, eff_w_mm, eff_h_mm):
    """Return (hfov_rad, vfov_rad)."""
    hfov = 2.0 * math.atan((eff_w_mm * 0.5) / focal_mm)
    vfov = 2.0 * math.atan((eff_h_mm * 0.5) / focal_mm)
    return hfov, vfov

def make_camera_frustum_curves(camera, near_distance=1.0, far_distance=10.0,
                               image_aspect=16.0/9.0, name='camFrustum_CURVES'):
    """
    Create 6 closed degree-1 curves (near, far, top, left, bottom, right) that outline the camera frustum.
    - camera: camera transform or shape name
    - near_distance / far_distance: world units
    - image_aspect: width/height (e.g., 1920/1080)
    - name: group name to parent all curves under
    """
    cam_shape_dag = get_camera_dagpath(camera)
    fn_cam = om.MFnCamera(cam_shape_dag)

    focal_mm = fn_cam.focalLength
    eff_w_mm, eff_h_mm = _effective_aperture_mm(cam_shape_dag, image_aspect)
    hfov, vfov = _fov_from_aperture(focal_mm, eff_w_mm, eff_h_mm)

    # Half extents for near/far planes
    near_hw, near_hh = near_distance * math.tan(hfov * 0.5), near_distance * math.tan(vfov * 0.5)
    far_hw,  far_hh  = far_distance  * math.tan(hfov * 0.5), far_distance  * math.tan(vfov * 0.5)

    # Local-space corners (camera looks down -Z)
    near_pts = [
        om.MPoint(+near_hw, +near_hh, -near_distance),
        om.MPoint(-near_hw, +near_hh, -near_distance),
        om.MPoint(-near_hw, -near_hh, -near_distance),
        om.MPoint(+near_hw, -near_hh, -near_distance),
    ]
    far_pts = [
        om.MPoint(+far_hw, +far_hh, -far_distance),
        om.MPoint(-far_hw, +far_hh, -far_distance),
        om.MPoint(-far_hw, -far_hh, -far_distance),
        om.MPoint(+far_hw, -far_hh, -far_distance),
    ]

    # World transform
    mtx = cam_shape_dag.inclusiveMatrix()
    near_w = [p * mtx for p in near_pts]
    far_w  = [p * mtx for p in far_pts]

    # Helper to build a closed polyline curve (degree=1, start=end)
    def _make_closed_curve(points, crv_name):
        pts = [(p.x, p.y, p.z) for p in points] + [(points[0].x, points[0].y, points[0].z)]
        return cmds.curve(p=pts, d=1, n=crv_name)

    # Create group
    if cmds.objExists(name):
        grp = name
    else:
        grp = cmds.group(em=True, n=name)

    # Faces as closed curves (6 faces)
    # Order: near, far, top, left, bottom, right
    near_crv  = _make_closed_curve(near_w,  "{}_near".format(name))
    far_crv   = _make_closed_curve(far_w,   "{}_far".format(name))
    top_crv   = _make_closed_curve([near_w[0], near_w[1], far_w[1],  far_w[0]],  "{}_top".format(name))
    left_crv  = _make_closed_curve([near_w[1], near_w[2], far_w[2],  far_w[1]],  "{}_left".format(name))
    bottom_crv= _make_closed_curve([near_w[2], near_w[3], far_w[3],  far_w[2]],  "{}_bottom".format(name))
    right_crv = _make_closed_curve([near_w[3], near_w[0], far_w[0],  far_w[3]],  "{}_right".format(name))

    # Parent all
    for crv in (near_crv, far_crv, top_crv, left_crv, bottom_crv, right_crv):
        # curve command returns shape parent; ensure we parent the transform
        xform = cmds.listRelatives(crv, p=True, f=False) or [crv]
        cmds.parent(xform[0], grp)

    return {
        'group': grp,
        'curves': [near_crv, far_crv, top_crv, left_crv, bottom_crv, right_crv],
        'hfov_deg': math.degrees(hfov),
        'vfov_deg': math.degrees(vfov),
        'near_half_width': near_hw,
        'near_half_height': near_hh,
        'far_half_width': far_hw,
        'far_half_height': far_hh,
    }

# Example:
info = make_camera_frustum_curves('camera1', near_distance=1.0, far_distance=15.0, image_aspect=1920.0/1080.0, name='perspFrustum_CRV')
print(info)
