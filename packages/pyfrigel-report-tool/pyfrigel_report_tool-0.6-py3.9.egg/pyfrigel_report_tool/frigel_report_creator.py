from .consts import *

from reportlab.platypus import Image, Paragraph
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm, cm

from abc import abstractclassmethod
from typing import Union
from io import BytesIO


class FrigelReportCreator():
    '''
    Base class for the creation of machine reports
    '''
    
    def __init__(self):
        self.logo = DEFAULT_LOGO_PATH


    @abstractclassmethod
    def generatePDF(self, dest_path=None, language: str='en') -> Union[BytesIO, str]:
        '''
        generate PDF file
        
        input:
            dest_path (str): save path, if None the PDF will be saved into a ByetsIO buffer
            language (str): translation language
            
        output:
            dest_path if is not None, else the buffer containing the PDF
        '''
        pass
    

    def getPDFAsBuffer(self, language: str='en') -> BytesIO:
        '''
        returns a buffer containing the PDF
        
        input:
            language (str): translation language
        
        output:
            buffer (BytesIO): buffer containing the PDF
        '''
        return self.generatePDF(language=language)
    
    
    def savePDF(self, dest_path: str, language: str='en') -> str:
        '''
        generates and saves the PDF to a file
        
        input:
            dest_path (str): save path
            language (str): translation language
            
        output:
            dest_path (str)
        '''
        return self.generatePDF(dest_path=dest_path, language=language)
    
    
    def get_image(self, path: str, width: float=1*cm) -> Image:
        '''
        returns image object mantaining aspect ratio
        
        input:
            path (str): image path
            width (float): expected width of the object
            
        output:
            image (reportlab.platypusImage)
        '''
        
        image = ImageReader(path)
        iw, ih = image.getSize()
        aspect = ih / float(iw)
        return Image(path, width=width, height=(width * aspect))
    
    
    def addSpacing(self, spacing: float) -> None:
        '''
        adds vertical spacing to the PDF
        
        input:
            spacing (float)
        '''
        self.lastPositionY += spacing
        
        
    def newPage(self) -> None:
        '''
        creates a new pdf page
        '''
        self.canvas.showPage()
        self.lastPositionX = 0
        self.lastPositionY = DEFAULT_STARTING_POSITION
        self.drawLogo()
        
    
    def drawOnCanvas(self, object: any, x: float, y: float) -> None:
        '''
        draws an object on canvas based on current position
        
        input:
            object (any): any reportlab object
            x (float): x offset
            y (float): y offset
        '''
        width, height = object.wrapOn(self.canvas, self.width, self.height)
        object.drawOn(self.canvas, *self.coord(self.horizontalMargin + x, self.lastPositionY + y, mm))
        self.lastPositionX = width/mm + self.horizontalMargin + x
        self.lastPositionY += height/mm + y
        
        
    def drawLogo(self) -> None:
        '''
        draws the logo on the page
        '''
        logo_object = self.get_image(self.logo, 3*cm)
        logo_object.wrapOn(self.canvas, self.width, self.height)
        logo_object.drawOn(self.canvas, *self.coord(self.logoPositionX, self.logoPositionY + logo_object.drawHeight/2, mm))
        
        
    def coord(self, x, y, unit=1) -> None:
        '''
        returns the coordinates relative to the pdf file
        
        input:
            x (float): x
            y (float): y
            
        output:
            x, y (float, float)
        '''
        x, y = x * unit, self.height -  y * unit
        return x, y    
    
    
    def createParagraph(self, text, x: float, y: float, style: any=None) -> None:
        '''
        add a paragraph to the PDF file
        
        input:
            text (str): paragraph text
            x (float): x position
            y (float): y position
            style (reportlab.lib.styles.StyleSheet1): optional stylesheet
        '''
        if not style:
            style = self.styles["Normal"]
        p = Paragraph(text, style=style)
        p.wrapOn(self.canvas, self.width, self.height)
        p.drawOn(self.canvas, *self.coord(x, y, mm))