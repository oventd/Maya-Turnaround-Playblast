import maya.cmds as cmds
from position_calculator import get_turnaround_camera_pos


class TurnAroundCameraCreator:
    """Encapsulates creation/deletion and setup of a turnaround camera.

    Responsibilities:
    - Create a camera transform and a parent group
    - Position camera using asset-driven framing
    - Keyframe group rotateY for a full 360 spin
    - Delete created nodes for cleanup
    """

    def __init__(self, camera_name="publishcamera", group_name="publishcamera_group"):
        # Unified identifiers: hold current or intended names
        self._camera = camera_name
        self._group = group_name

    # Unified camera identifier (string). Setter renames existing node if needed.
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

    # Unified group identifier (string). Setter renames existing node if needed.
    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, name):
        if not isinstance(name, str) or not name:
            return
        if self._group and cmds.objExists(self._group) and name != self._group:
            try:
                self._group = cmds.rename(self._group, name)
            except Exception:
                self._group = name
                return
        else:
            self._group = name

    def create(self, target, start_frame=1, end_frame=119, padding=1.3):
        """Create and set up the turnaround camera and group."""
        # Clean up any existing nodes with the same names
        self.delete()

        # Create camera
        self._camera = cmds.camera(n=self._camera)[0]

        # Position camera based on asset size
        cam_pos = get_turnaround_camera_pos(self._camera, target, padding=1.3)
        if cam_pos is not None:
            cmds.setAttr(f"{self._camera}.translateX", cam_pos[0])
            cmds.setAttr(f"{self._camera}.translateY", cam_pos[1])
            cmds.setAttr(f"{self._camera}.translateZ", cam_pos[2])

        # Create group and parent camera under it
        cmds.select(clear=True)
        self._group = cmds.group(name=self._group, empty=True)
        cmds.parent(self._camera, self._group)

        # Animate rotateY for a full 360 spin
        cmds.setKeyframe(self._group, attribute="rotateY", value=0, time=start_frame)
        cmds.setKeyframe(self._group, attribute="rotateY", value=360, time=end_frame + 1)
        cmds.selectKey(self._group, time=(start_frame, end_frame), attribute="rotateY")
        cmds.keyTangent(inTangentType="linear", outTangentType="linear")

    def delete(self):
        """Delete the created turnaround camera and group if they exist."""
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
        # Keep last known names as intended identifiers

    def update_frame_range(self, start_frame, end_frame):
        """Update the turnaround rotation keys for the group if it exists."""
        if not self._group or not cmds.objExists(self._group):
            return
        try:
            # Remove existing keys on rotateY
            cmds.cutKey(self._group, attribute="rotateY", clear=True)
            # Re-create linear 360 spin over the new range
            cmds.setKeyframe(self._group, attribute="rotateY", value=0, time=start_frame)
            cmds.setKeyframe(self._group, attribute="rotateY", value=360, time=end_frame + 1)
            cmds.selectKey(self._group, time=(start_frame, end_frame), attribute="rotateY")
            cmds.keyTangent(inTangentType="linear", outTangentType="linear")
        except Exception:
            pass
