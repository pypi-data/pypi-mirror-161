from opencmiss.zinc.sceneviewerinput import Sceneviewerinput
from opencmiss.zinchandlers.abstracthandler import AbstractHandler, BUTTON_MAP, modifier_map


class ZoomOnly(AbstractHandler):

    def __init__(self):
        super(ZoomOnly, self).__init__()
        self._zooming = False

    def enter(self):
        pass

    def leave(self):
        pass

    @staticmethod
    def _using_zoom_mouse_button(event):
        return BUTTON_MAP[event.button()] == Sceneviewerinput.BUTTON_TYPE_RIGHT

    def mouse_press_event(self, event):
        super(ZoomOnly, self).mouse_press_event(event)
        self._zooming = self._processing_mouse_events and self._using_zoom_mouse_button(event)
        if self._zooming:
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x(), event.y())
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            scene_input.setModifierFlags(modifier_map(event.modifiers()))
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)

    def mouse_move_event(self, event):
        super(ZoomOnly, self).mouse_move_event(event)
        if self._zooming:
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x(), event.y())
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)

    def mouse_release_event(self, event):
        super(ZoomOnly, self).mouse_release_event(event)
        if self._zooming:
            self._zooming = False
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            scene_input.setPosition(event.x(), event.y())
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)
