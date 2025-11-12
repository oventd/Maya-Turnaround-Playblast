import maya.cmds as cmds
import maya.mel as mel
from pathlib import Path

class PlayblastGenerator:
    """Helper to generate Maya playblasts with configurable options.

    Usage:
    - Set options via properties or `options` dict.
    - Optionally override template hooks in subclasses:
      - `_validate_frame_range(first, last)` to validate/adjust input range
      - `_on_frame_range_changed(first, last)` to react to range changes
    - Call `run(path=..., frame_range=(first, last))`.
    """

    def __init__(self):
        self._playblast_options = {
            "clearCache": True,
            "compression": "png",
            "endTime": 0,
            "filename": "",
            "forceOverwrite": True,
            "framePadding": 4,
            "format": "qt",
            "offScreen": True,  # Use offscreen viewport
            "percent": 100,  # Render scale percent
            "quality": 100,
            "sequenceTime": False,
            "showOrnaments": False,  # Hide UI ornaments
            "startTime": 0,
            "viewer": False,  # Prevent auto playback
            "widthHeight": (1280, 720),  # Output resolution
        }
        self._camera = None
        
    @property
    def format(self):
        return self._playblast_options['format']
    
    @format.setter
    def format(self, format):
        format = format.lower()
        self._playblast_options["format"] = format
        if format == "image":
            self._playblast_options["compression"] = "jpg"

    @property    
    def compression(self):
        return self._playblast_options['compression']
    
    @compression.setter
    def compression(self, compression):
        self._playblast_options['compression'] = compression

    @property
    def path(self):
        """Output filepath for the playblast."""
        return self._playblast_options['filename']

    @path.setter
    def path(self, path):
        """Sets `filename` in options."""
        self._set_path(path)

    @property
    def options(self):
        """Raw options dict passed to `cmds.playblast` (read)."""
        return self._playblast_options

    @options.setter
    def options(self, options):
        """Replace the options dict entirely (write)."""
        self._playblast_options = options.copy()

    @property
    def resolution(self):
        """Return (width, height)."""
        return self._playblast_options['widthHeight']

    @resolution.setter
    def resolution(self, value):
        """Set output resolution as (width, height)."""
        width, height = value
        self._playblast_options['widthHeight'] = (width, height)

    @property
    def camera(self):
        return self._camera
    
    @camera.setter
    def camera(self, camera):
        self._camera = camera

    @property
    def frame_range(self):
        """Get or set (first_frame, last_frame)."""
        return self._playblast_options['startTime'], self._playblast_options['endTime']

    @frame_range.setter
    def frame_range(self, value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            return
        self._set_frame_range(value)
    
    def _set_path(self, path):
        """Setter kept for compatibility; sets `filename` in options."""
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix == ".png":
            self._playblast_options["format"] = "image"
            self._playblast_options["compression"] = "png"
        else:
            self._playblast_options["format"] = "qt"

        clean_name = str(path.with_suffix("")) if suffix else str(path)
        self._playblast_options["filename"] = clean_name

    def _set_frame_range(self, frame_range):
        """Set frame range, then trigger subclass hook for side-effects."""
        first_frame, last_frame = self._validate_frame_range(frame_range)
        first_frame, last_frame = int(first_frame), int(last_frame)
        self._playblast_options['startTime'] = first_frame
        self._playblast_options['endTime'] = last_frame
        self._on_frame_range_changed(frame_range)

    def _on_frame_range_changed(self, frame_range):
        """Hook: after range updates; subclasses sync dependent state here."""
        pass

    def _validate_frame_range(self, frame_range):
        """Hook: validate/adjust incoming frame range if needed.

        Default behavior casts to int and swaps if last < first.
        """
        first_frame, last_frame = frame_range
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
        if path:
            self._set_path(path)
        if frame_range:
            self._set_frame_range(frame_range)

        user_camera = self.get_persp_camera()

        self.pre_process()
        self.playblast()
        self.post_process()

        self.set_persp_camera(user_camera)
