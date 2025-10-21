import maya.cmds as cmds
import sys
from playblast_generator import PlayblastGenerator
from position_calculator import get_turnaround_camera_pos


class TurnAroundPlayblastGenerator(PlayblastGenerator):
    """Create a turnaround camera and generate a playblast with it."""

    def __init__(self):
        super().__init__()
        self.camera = "publishcamera"  # Turnaround camera name
        self.camera_group = "publishcamera_group"  # Turnaround camera group name
        self.user_camera_name = ""  # User's current persp camera name

        # Default frame range: 1 ~ 120
        self._playblast_options['startTime'] = 1
        self._playblast_options['endTime'] = 119

    def create_camera(self):
        """Create the turnaround camera and its group, then keyframe spin."""
        self.delete_camera()

        # Create camera
        self.camera = cmds.camera(n=self.camera)[0]

        # Position camera based on asset size
        cam_pos = get_turnaround_camera_pos(self.camera)
        cmds.setAttr(f"{self.camera}.translateX", cam_pos[0])
        cmds.setAttr(f"{self.camera}.translateY", cam_pos[1])
        cmds.setAttr(f"{self.camera}.translateZ", cam_pos[2])

        # Create group for the camera
        cmds.select(clear=True)
        self.camera_group = cmds.group(name=self.camera_group, empty=True)
        cmds.parent(self.camera, self.camera_group)

        # Animate rotateY for a full 360 spin
        start_frame = self._playblast_options['startTime']
        end_frame = self._playblast_options['endTime']
        cmds.setKeyframe(self.camera_group, attribute="rotateY", value=0, time=start_frame)
        cmds.setKeyframe(self.camera_group, attribute="rotateY", value=360, time=end_frame + 1)
        cmds.selectKey(self.camera_group, time=(1, 120), attribute="rotateY")
        cmds.keyTangent(inTangentType="linear", outTangentType="linear")

    def delete_camera(self):
        """Delete the created turnaround camera and group if they exist."""
        if cmds.objExists(self.camera):
            cmds.delete(self.camera)
        if cmds.objExists(self.camera_group):
            cmds.delete(self.camera_group)

    def pre_process(self):
        """Prepare scene: create camera and set it to the persp view."""

        # Create the turnaround camera and assign to persp view
        self.create_camera()
        self.set_persp_camera(self.camera)
        return

    def post_process(self):
        """Cleanup after playblast by removing the temporary camera."""
        # Delete the turnaround camera
        self.delete_camera()


if __name__ == "__main__":
    import sys

