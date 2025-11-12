import maya.cmds as cmds
from playblast_generator import PlayblastGenerator
from turntable_camera_creator import TurnTableCameraCreator

class AnimPlayblastGenerator(PlayblastGenerator):
    """Create a TurnTable camera and generate a playblast with it."""

    def __init__(self, 
                 camera_creator):
        super().__init__()
        self._set_camera_creator(camera_creator)

    @property
    def camera_creator(self):
        return self._camera_creator

    @camera_creator.setter
    def camera_creator(self, camera_creator):
        self._set_camera_creator(camera_creator)

    def _set_camera_creator(self, camera_creator):
        self._camera_creator = camera_creator
        self._set_frame_range(self._camera_creator.frame_range)

    def pre_process(self):
        """Prepare scene: create camera and set it to the persp view."""
        start_frame = self._playblast_options['startTime']
        end_frame = self._playblast_options['endTime']

        # Encapsulated camera creator (composition)
        self._camera = self._camera_creator.create()
        super().pre_process()
        return

    def post_process(self):
        """Cleanup after playblast by removing the temporary camera."""
        self._camera_creator.delete()
    
if __name__ == "__main__":
    AnimPlayblastGenerator(TurnTableCameraCreator("publishcamera")).run()