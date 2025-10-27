import maya.cmds as cmds
from playblast_generator import PlayblastGenerator
from camera_creator import TurnAroundCameraCreator


class TurnAroundPlayblastGenerator(PlayblastGenerator):
    """Create a turnaround camera and generate a playblast with it."""

    def __init__(self, target, padding=1.3, camera_name="publishcamera", group_name="publishcamera_group"):
        super().__init__()
        if not isinstance(target, str) or not cmds.objExists(target):
            cmds.warning("Target node not found: {}".format(target))
            return
        self._target = target
        self._padding = padding
        # Default frame range: 1 ~ 120
        self._playblast_options['startTime'] = 1
        self._playblast_options['endTime'] = 119

        # Encapsulated camera creator (composition)
        self._camera_creator = TurnAroundCameraCreator(camera_name, group_name)
    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, name):
        if not isinstance(name, str) or not name:
            return
        self._target = name

    def pre_process(self):
        """Prepare scene: create camera and set it to the persp view."""
        start_frame = self._playblast_options['startTime']
        end_frame = self._playblast_options['endTime']
        self._camera_creator.create(
            target=self._target,
            start_frame=start_frame,
            end_frame=end_frame,
            padding=self._padding
        )
        target_cam = self._camera_creator.camera
        self.set_persp_camera(target_cam)
        return

    def post_process(self):
        """Cleanup after playblast by removing the temporary camera."""
        self._camera_creator.delete()

    def _on_frame_range_changed(self, first_frame, last_frame):
        self._camera_creator.update_frame_range(first_frame, last_frame)
    
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    target = "asset"
    TurnAroundPlayblastGenerator(target).run()
