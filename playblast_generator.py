import maya.cmds as cmds
import maya.mel as mel


class PlayblastGenerator:
    """Helper to generate Maya playblasts with configurable options.

    Usage:
    - Set options via properties or `options` dict.
    - Optionally override template hooks in subclasses:
      - `_coerce_frame_range(first, last)` to validate/adjust input range
      - `_on_frame_range_changed(first, last)` to react to range changes
    - Call `run(path=..., frame_range=(first, last))`.
    """

    def __init__(self):
        self._playblast_options = {
            'startTime': 0,
            'endTime': 0,
            "format": "qt",
            "filename": "",
            "forceOverwrite": True,
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
        self._camera = None

    @property
    def path(self):
        """Output filepath for the playblast."""
        return self._playblast_options['filename']

    @path.setter
    def set_path(self, path):
        """Setter kept for compatibility; sets `filename` in options."""
        self._playblast_options['filename'] = path

    @property
    def options(self):
        """Raw options dict passed to `cmds.playblast` (read)."""
        return self._playblast_options

    @options.setter
    def options(self, options):
        """Replace the options dict entirely (write)."""
        self._playblast_options = options

    @property
    def resolution(self):
        """Return (width, height)."""
        return self._playblast_options['widthHeight']

    @resolution.setter
    def resolution(self, width, height):
        """Set output resolution as (width, height)."""
        self._playblast_options['widthHeight'] = (width, height)

    @property
    def camera(self):
        return self._camera
    
    @camera.setter
    def camera(self, camera):
        self._camera = camera

    def set_frame_range(self, first_frame, last_frame):
        """Set frame range, then trigger subclass hook for side-effects."""
        first_frame, last_frame = self._coerce_frame_range(first_frame, last_frame)
        self._playblast_options['startTime'] = first_frame
        self._playblast_options['endTime'] = last_frame
        self._on_frame_range_changed(first_frame, last_frame)

    @property
    def frame_range(self):
        """Get or set (first_frame, last_frame)."""
        return self._playblast_options['startTime'], self._playblast_options['endTime']

    @frame_range.setter
    def frame_range(self, value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            return
        self.set_frame_range(value[0], value[1])

    def _on_frame_range_changed(self, first_frame, last_frame):
        """Hook: after range updates; subclasses sync dependent state here."""
        pass

    def _coerce_frame_range(self, first_frame, last_frame):
        """Hook: validate/adjust incoming frame range if needed.

        Default behavior casts to int and swaps if last < first.
        """
        try:
            f = int(first_frame)
            l = int(last_frame)
        except Exception:
            # Leave as-is if conversion fails
            return first_frame, last_frame
        if l < f:
            f, l = l, f
        return f, l

    def get_persp_camera(self):
        """Return camera used by the perspective model panel (modelPanel4)."""
        try:
            camera = cmds.modelPanel('modelPanel4', query=True, camera=True)
            return camera
        except Exception:
            print('AnimCam not found')
            return None

    def set_persp_camera(self, camera):
        """Assign the given camera name to the perspective panel.

        Args:
            camera (str): Camera transform to look through.
        """
        try:
            mel.eval('setNamedPanelLayout "Single Perspective View"')
            cmds.lookThru(camera, "modelPanel4")
        except Exception:
            print('AnimCam not found')
            return

    def pre_process(self):
        """Prepare scene"""
        if self.camera:
            self.set_persp_camera(self._camera)

    def post_process(self):
        """Cleanup after playblast"""
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

    def run(self, path=None, frame_range=None):
        """Execute the playblast with optional overrides.

        Args:
            path (str | None): Output path override.
            frame_range (tuple[int, int] | None): (first, last) override.
        """
        if frame_range:
            self.set_frame_range(frame_range[0], frame_range[1])

        if path:
            self._playblast_options['filename'] = path

        user_camera = self.get_persp_camera()

        self.pre_process()
        self.playblast()
        self.post_process()

        self.set_persp_camera(user_camera)
