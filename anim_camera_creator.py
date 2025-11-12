import maya.cmds as cmds
from position_calculator import get_TurnTable_camera_pos


class AnimCameraCreator:
    """Encapsulates creation/deletion and setup of a TurnTable camera.

    Responsibilities:
    - Create a camera transform and a parent group
    - Position camera using asset-driven framing
    - Keyframe group rotateY for a full 360 spin
    - Delete created nodes for cleanup
    """

    def __init__(self, 
                 camera_name="publishcamera",
                 group_name="publishcamera_group"):
        # Unified identifiers: hold current or intended names
        self._camera = camera_name
        self._group = group_name

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, name):
        if not isinstance(name, str) or not name:
            return
        if self._camera and cmds.objExists(self._camera) and name != self._camera:
            try:
                self._camera = cmds.rename(self._camera, name)
            except Exception:
                # If rename fails, still update intended name
                self._camera = name
                return
        else:
            self._camera = name

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, name):
        if not isinstance(name, str):
            return
        if self._group and cmds.objExists(self._group) and name != self._group:
            try:
                self._group = cmds.rename(self._group, name)
            except Exception:
                self._group = name
                return
        else:
            self._group = name

    def create(self):
        """Create and set up the TurnTable camera and group."""
        
        # Clean up any existing nodes with the same names
        self.delete()

        # Create camera
        self.create_camera()

        # Create group
        self.create_group()

        # Animate group
        self.animate_group()

        return self.camera

    def delete(self):
        """Delete the created TurnTable camera and group if they exist."""
        if self._camera and cmds.objExists(self._camera):
            try:
                cmds.delete(self._camera)
            except Exception:
                pass
        if self._group and cmds.objExists(self._group):
            try:
                cmds.delete(self._group)
            except Exception:
                pass

    def create_camera(self):
        self._camera = cmds.camera(n=self._camera)[0]

    def create_group(self):
        cmds.select(clear=True)
        self._group = cmds.group(name=self._group, empty=True)
        cmds.parent(self._camera, self._group)

    def animate_group(self):
        pass
    
    @staticmethod
    def autoframing(camera, target, padding=1.3):
        if not isinstance(target, str) or not cmds.objExists(target):
                cmds.warning("Target object not found: {}".format(target))
                return
        
        # Position camera based on asset size
        cam_pos = get_TurnTable_camera_pos(camera, target, padding)
        if cam_pos is not None:
            cmds.setAttr(f"{camera}.translateX", cam_pos[0])
            cmds.setAttr(f"{camera}.translateY", cam_pos[1])
            cmds.setAttr(f"{camera}.translateZ", cam_pos[2])