"""
   Copyright 2015 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from PySide2 import QtCore, QtWidgets

from opencmiss.zincwidgets.ui.ui_timeeditorwidget import Ui_TimeEditorWidget
from opencmiss.argon.settings.mainsettings import FLOAT_STRING_FORMAT


class TimeEditorWidget(QtWidgets.QWidget):
    """
    Provides display and manipulation of the current time in a Zinc Context.
    """

    def __init__(self, parent=None):
        """
        Create a time editor widget.

        :param parent: Parent widget for this widget.
        """
        super(TimeEditorWidget, self).__init__(parent)
        self._ui = Ui_TimeEditorWidget()
        self._ui.setupUi(self)

        self._context = None
        self._timekeeper = None
        self._timer = QtCore.QTimer()
        self._play_direction = 0

        self._makeConnections()

    def _makeConnections(self):
        self._ui.pushButtonPlay.clicked.connect(self._playClicked)
        self._ui.pushButtonStop.clicked.connect(self._stopClicked)
        self._ui.pushButtonPlayReverse.clicked.connect(self._playReverseClicked)

        self._ui.doubleSpinBoxMinimumTime.valueChanged.connect(self._minimumTimeValueChanged)
        self._ui.doubleSpinBoxMaximumTime.valueChanged.connect(self._maximumTimeValueChanged)

        self._ui.horizontalSliderTime.valueChanged.connect(self._timeSliderValueChanged)

        self._ui.spinBoxNumberofSteps.valueChanged.connect(self._numberOfStepsValueChanged)

        self._timer.timeout.connect(self._updateTime)

    def _updateUi(self):
        active_timer = self._timer.isActive()
        self._ui.pushButtonPlay.setEnabled(not active_timer)
        self._ui.pushButtonPlayReverse.setEnabled(not active_timer)
        self._ui.pushButtonStop.setEnabled(active_timer)
        self._ui.doubleSpinBoxMinimumTime.setEnabled(not active_timer)
        self._ui.doubleSpinBoxMaximumTime.setEnabled(not active_timer)
        self._ui.lineEditTime.setEnabled(not active_timer)
        self._ui.spinBoxNumberofSteps.setEnabled(not active_timer)

    def _calcTimeFromSliderValue(self, time, num_steps=None, min_time=None, max_time=None):
        if num_steps is None:
            num_steps = self._ui.spinBoxNumberofSteps.value()
        if min_time is None:
            min_time = self._timekeeper.getMinimumTime()
        if max_time is None:
            max_time = self._timekeeper.getMaximumTime()

        return (max_time - min_time) / (num_steps - 1) * time + min_time

    def _calcSliderValueFromTime(self, time, num_steps=None, min_time=None, max_time=None):
        if num_steps is None:
            num_steps = self._ui.spinBoxNumberofSteps.value()
        if min_time is None:
            min_time = self._timekeeper.getMinimumTime()
        if max_time is None:
            max_time = self._timekeeper.getMaximumTime()

        if (max_time - min_time) < 1e-12:
            return round(min_time)
        return round((num_steps - 1) / (max_time - min_time) * time - (num_steps - 1) * min_time / (max_time - min_time))

    def _calcInterval(self, num_steps=None, min_time=None, max_time=None):
        if num_steps is None:
            num_steps = self._ui.spinBoxNumberofSteps.value()
        if min_time is None:
            min_time = self._timekeeper.getMinimumTime()
        if max_time is None:
            max_time = self._timekeeper.getMaximumTime()

        return (max_time - min_time) / (num_steps - 1)

    def _initUi(self):
        DEFAULT_NUM_STEPS = 10
        min_time = self._timekeeper.getMinimumTime()
        max_time = self._timekeeper.getMaximumTime()
        time = self._timekeeper.getTime()

        self._ui.spinBoxNumberofSteps.setValue(DEFAULT_NUM_STEPS)
        self._ui.lineEditTime.setText(str(time))
        self._ui.doubleSpinBoxMinimumTime.setValue(min_time)
        self._ui.doubleSpinBoxMaximumTime.setValue(max_time)
        self._ui.horizontalSliderTime.setMinimum(0)
        self._ui.horizontalSliderTime.setMaximum(DEFAULT_NUM_STEPS - 1)
        self._ui.horizontalSliderTime.setValue(self._calcSliderValueFromTime(time, DEFAULT_NUM_STEPS, min_time, max_time))

    def _updateTimes(self):
        min_time = self._timekeeper.getMinimumTime()
        max_time = self._timekeeper.getMaximumTime()
        self._ui.doubleSpinBoxMinimumTime.setValue(min_time)
        self._ui.doubleSpinBoxMaximumTime.setValue(max_time)
        self._setTime(self._timekeeper.getTime())

    def _minimumTimeValueChanged(self, value):
        if value > self._timekeeper.getMaximumTime():
            self._ui.doubleSpinBoxMinimumTime.setValue(self._timekeeper.getMinimumTime())
        else:
            self._timekeeper.setMinimumTime(value)
            displayed_time = float(self._ui.lineEditTime.text())
            if displayed_time < value:
                self._ui.lineEditTime.setText(FLOAT_STRING_FORMAT.format(value))

    def _maximumTimeValueChanged(self, value):
        if value < self._timekeeper.getMinimumTime():
            self._ui.doubleSpinBoxMaximumTime.setValue(self._timekeeper.getMaximumTime())
        else:
            self._timekeeper.setMaximumTime(value)
            displayed_time = float(self._ui.lineEditTime.text())
            if displayed_time > value:
                self._ui.lineEditTime.setText(FLOAT_STRING_FORMAT.format(value))

    def _timeSliderValueChanged(self, value):
        self._setTime(self._calcTimeFromSliderValue(value))

    def _numberOfStepsValueChanged(self, value):
        self._ui.horizontalSliderTime.setMaximum(value - 1)

    def _setTime(self, time):
        self._ui.lineEditTime.setText(FLOAT_STRING_FORMAT.format(time))
        self._ui.horizontalSliderTime.blockSignals(True)
        self._ui.horizontalSliderTime.setValue(self._calcSliderValueFromTime(time))
        self._ui.horizontalSliderTime.blockSignals(False)
        self._timekeeper.setTime(time)

    def _updateTime(self):
        increment = self._calcInterval()
        min_time = self._timekeeper.getMinimumTime()
        max_time = self._timekeeper.getMaximumTime()
        new_time = self._timekeeper.getTime() + self._play_direction * increment
        if new_time < min_time:
            new_time = max_time
        elif new_time > max_time:
            new_time = min_time

        self._setTime(new_time)

    def _play(self):
        self._timer.setInterval(int(self._calcInterval() * 1000))
        self._timer.start()
        self._updateUi()

    def _playClicked(self):
        self._play_direction = 1
        self._play()

    def _stopClicked(self):
        self._timer.stop()
        self._updateUi()

    def _playReverseClicked(self):
        self._play_direction = -1
        self._play()

    def setZincContext(self, zincContext):
        """
        Set the Zinc Context to the time editor.

        :param zincContext: An opencmiss.zinc.context.Context.
        """
        self._context = zincContext
        self._timekeeper = zincContext.getTimekeepermodule().getDefaultTimekeeper()
        self._initUi()
        self._updateUi()

    def showEvent(self, event):
        self._updateTimes()
