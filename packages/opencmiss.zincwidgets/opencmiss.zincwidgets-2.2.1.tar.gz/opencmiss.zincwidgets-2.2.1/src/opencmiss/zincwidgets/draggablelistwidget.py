from PySide2 import QtCore, QtGui, QtWidgets

class DraggableListWidget(QtWidgets.QListWidget):
    def __init__(self,parent = None):
        super(DraggableListWidget,self).__init__(parent)
        self.setDragDropMode(self.InternalMove)
        self.onItemDropped = None

    def dropEvent(self,event):

        oldIndex = self.currentRow()
        dragItem = self.currentItem()

        super(DraggableListWidget,self).dropEvent(event)

        newIndex = self.currentRow()

        if self.onItemDropped:
            self.onItemDropped(oldIndex, newIndex)

    def registerDropCallback(self, onItemDroppedCallback):
        self.onItemDropped = onItemDroppedCallback
