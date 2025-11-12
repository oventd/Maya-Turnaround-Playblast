import maya.cmds as cmds
from position_calculator import get_TurnTable_camera_pos
from TurntableGenerator.anim_camera_creator import AnimCameraCreator

class TurnTableCameraCreator(AnimCameraCreator):
    """Encapsulates creation/deletion and setup of a TurnTable camera.

    Responsibilities:
    - Create a camera transform and a parent group
    - Position camera using asset-driven framing
    - Keyframe group rotateY for a full 360 spin
    - Delete created nodes for cleanup
    """

    def __init__(self, 
                 target,
                 camera_name="publishcamera",
                 group_name="publishcamera_group",
                 padding=1.3,
                 frame_range=(1, 119)):
        super().__init__(camera_name, group_name)
        self._target = target
        self._padding = padding
        self._frame_range = frame_range

    def create_camera(self):
        super().create_camera()
        self.autoframing(self.camera, self._target, self._padding)

    def animate_group(self):
        start_frame = self._frame_range[0]
        end_animation = self._frame_range[1]

        # Animate rotateY for a full 360 spin
        cmds.setKeyframe(self._group, attribute="rotateY", value=0, time=start_frame)
        cmds.setKeyframe(self._group, attribute="rotateY", value=360, time=end_animation)
        cmds.keyTangent(self._group, itt='linear', ott='linear', t=(start_frame, end_animation))