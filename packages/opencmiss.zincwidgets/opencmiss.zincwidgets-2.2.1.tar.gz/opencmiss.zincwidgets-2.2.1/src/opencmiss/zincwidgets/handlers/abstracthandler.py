from opencmiss.zincwidgets.definitions import BUTTON_MAP


class AbstractHandler(object):

    def __init__(self):
        self._scene_viewer = None
        self._zinc_sceneviewer = None
        self._ignore_mouse_events = False
        self._processing_mouse_events = False

    def get_mode(self):
        return self.__class__.__name__

    def set_ignore_mouse_events(self, value=True):
        self._ignore_mouse_events = value

    def set_scene_viewer(self, scene_viewer):
        self._scene_viewer = scene_viewer
        if self._scene_viewer.is_graphics_initialized():
            self._graphics_ready()
        else:
            self._scene_viewer.graphics_initialized.connect(self._graphics_ready)

    def enter(self):
        raise NotImplementedError()

    def leave(self):
        raise NotImplementedError()

    def mouse_press_event(self, event):
        self._processing_mouse_events = False
        if self._ignore_mouse_events:
            event.ignore()
            return

        if event.button() not in BUTTON_MAP:
            return

        event.accept()
        self._processing_mouse_events = True

    def mouse_move_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        event.accept()

    def mouse_release_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        if event.button() not in BUTTON_MAP:
            return

        event.accept()

    def mouse_enter_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        event.accept()

    def mouse_leave_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        event.accept()

    def _graphics_ready(self):
        self._zinc_sceneviewer = self._scene_viewer.get_zinc_sceneviewer()
