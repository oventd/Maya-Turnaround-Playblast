import maya.api.OpenMaya as om
import maya.cmds as cmds

def get_dagpath_if_exists(name):
    """Return MDagPath if node exists, otherwise None."""
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return sel.getDagPath(0)
    except RuntimeError:
        return None
def main(*args):
    dag = get_dagpath_if_exists("asset")
    if not dag:
        return
    
    fn_dag = om.MFnDagNode(dag)
    local_bbox = fn_dag.boundingBox
    bb_list = [(local_bbox.min.x, local_bbox.min.y, local_bbox.min.z),
            (local_bbox.max.x, local_bbox.max.y, local_bbox.max.z)]
    print(bb_list)

main()
