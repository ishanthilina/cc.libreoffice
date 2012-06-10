import unohelper

from com.sun.star.awt import XActionListener

class CC0ClickListener(XActionListener,unohelper.Base):
    """Show Creative Commons tab.
    """
    
    def __init__(self, dialog):
        """
        """
        self.dialog=dialog


    def actionPerformed(self, aEvent):
        """
        
        Arguments:
        - `aEvent`:ActionEvent
        """
        self.dialog.setLicenseType(2)

    #@Override
    def disposing(self, eObject):
        """
        
        Arguments:
        - `eObject`:EventObject
        """
        pass
