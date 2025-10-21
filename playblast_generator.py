import maya.cmds as cmds
import maya.mel as mel


class PlayblastGenerator:
    """Helper class to generate playblasts with configurable options."""

    def __init__(self):
        self._playblast_options = {
            'startTime': 0,
            'endTime': 0,
            "format": "qt",
            "filename": "",
            "sequenceTime": False,
            "clearCache": True,
            "viewer": False,  # Prevent auto playback
            "showOrnaments": False,  # Hide UI ornaments
            "framePadding": 4,
            "percent": 100,  # Render scale percent
            "compression": "png",
            "quality": 100,
            "widthHeight": (1280, 720),  # Output resolution
            "offScreen": True  # Use offscreen viewport
        }

    @property
    def path(self):
        return self._playblast_options['filename']

    @path.setter
    def set_path(self, path):
        self._playblast_options['filename'] = path

    @property
    def options(self):
        return self._playblast_options

    @options.setter
    def options(self, options):
        self._playblast_options = options

    @property
    def resolution(self):
        return self._playblast_options['widthHeight']

    @resolution.setter
    def resolution(self, width, height):
        self._playblast_options['widthHeight'] = (width, height)

    @property
    def frame_range(self):
        return self._playblast_options['startTime'], self._playblast_options['endTime']

    @frame_range.setter
    def frame_range(self, first_frame, last_frame):
        self._playblast_options['startTime'] = first_frame
        self._playblast_options['endTime'] = last_frame

    def get_persp_camera(self):
        """Return the camera currently used by the persp panel."""
        try:
            camera = cmds.modelPanel('modelPanel4', query=True, camera=True)
            return camera
        except Exception:
            print('AnimCam not found')
            return None

    def set_persp_camera(self, camera):
        """Assign the given camera name to the persp panel.

        camera: str
        """
        try:
            mel.eval('setNamedPanelLayout "Single Perspective View"')
            cmds.lookThru(camera, "modelPanel4")
        except Exception:
            print('AnimCam not found')
            return

    def pre_process(self):
        pass

    def post_process(self):
        pass

    def playblast(self):
        """Create a playblast with the current options."""
        # Store current frame
        current_frame = cmds.currentTime(query=True)

        # Create playblast
        cmds.playblast(**self._playblast_options)

        # Restore frame
        cmds.currentTime(current_frame)

        print(f'playblast completed : {self._playblast_options["filename"]}')

    def run(self, path=None, first_frame=None, last_frame=None):
        if first_frame:
            self._playblast_options['startTime'] = first_frame
        if last_frame:
            self._playblast_options['endTime'] = last_frame
        if path:
            self._playblast_options['filename'] = path

        user_camera = self.get_persp_camera()

        self.pre_process()

        self.playblast()

        self.post_process()

        self.set_persp_camera(user_camera)

