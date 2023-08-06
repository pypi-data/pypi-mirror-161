"""
   Copyright 2016 University of Auckland

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
from PySide2 import QtWidgets

from opencmiss.zinc.spectrum import Spectrum


class SpectrumChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self._nullObjectName = None
        self._spectrummodule = None
        self._spectrummodulenotifier = None
        self._spectrum = None

    def _spectrummoduleCallback(self, spectrummoduleevent):
        """
        Callback for change in spectrums; may need to rebuild spectrum list
        """
        changeSummary = spectrummoduleevent.getSummarySpectrumChangeFlags()
        #print("_spectrummoduleCallback changeSummary " + str(changeSummary))
        # Can't do this as may be received after new spectrum module is set!
        # if changeSummary == Spectrum.CHANGE_FLAG_FINAL:
        #    self.setSpectrummodule(None)
        if 0 != (changeSummary & (Spectrum.CHANGE_FLAG_IDENTIFIER | Spectrum.CHANGE_FLAG_ADD | Spectrum.CHANGE_FLAG_REMOVE)):
            self._buildSpectrumList()

    def _buildSpectrumList(self):
        """
        Rebuilds the list of items in the ComboBox from the spectrum module
        """
        self.blockSignals(True)
        self.clear()
        if self._spectrummodule:
            if self._nullObjectName:
                self.addItem(self._nullObjectName)
            spectrumiter = self._spectrummodule.createSpectrumiterator()
            spectrum = spectrumiter.next()
            while spectrum.isValid():
                name = spectrum.getName()
                self.addItem(name)
                spectrum = spectrumiter.next()
        self.blockSignals(False)
        self._displaySpectrum()

    def _displaySpectrum(self):
        """
        Display the currently chosen spectrum in the ComboBox
        """
        self.blockSignals(True)
        if self._spectrum:
            spectrumName = self._spectrum.getName()
            # following doesn't handle spectrum name matching _nullObjectName
            index = self.findText(spectrumName)
        else:
            index = 0
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def setNullObjectName(self, nullObjectName):
        """
        Enable a null object option with the supplied name e.g. '-' or '<select>'
        Default is None
        """
        self._nullObjectName = nullObjectName

    def setSpectrummodule(self, spectrummodule):
        """
        Sets the spectrum module that this widget chooses spectrums from
        """
        if spectrummodule and spectrummodule.isValid():
            self._spectrummodule = spectrummodule
            self._spectrummodulenotifier = spectrummodule.createSpectrummodulenotifier()
            self._spectrummodulenotifier.setCallback(self._spectrummoduleCallback)
        else:
            self._spectrummodule = None
            self._spectrummodulenotifier = None
        self._buildSpectrumList()

    def getSpectrum(self):
        """
        Must call this from currentIndexChanged() slot to get/update current spectrum
        """
        spectrumName = self.currentText()
        if self._nullObjectName and (spectrumName == self._nullObjectName):
            self._spectrum = None
        else:
            self._spectrum = self._spectrummodule.findSpectrumByName(spectrumName)
        return self._spectrum

    def setSpectrum(self, spectrum):
        """
        Set the currently selected spectrum; call after setConditional
        """
        if not spectrum or not spectrum.isValid():
            self._spectrum = None
        else:
            self._spectrum = spectrum
        self._displaySpectrum()
