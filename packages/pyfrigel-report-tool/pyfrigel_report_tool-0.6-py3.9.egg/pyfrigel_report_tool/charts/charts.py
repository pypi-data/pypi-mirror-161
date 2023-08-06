from pyfrigel_report_tool.consts import DEFAULT_STROKE_COLOR, WORKING_MODES_COLORS, DEFAULT_FONT

from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.colors import PCMYKColor
from reportlab.lib.formatters import DecimalFormatter


class ChartPieWithLegend(_DrawingEditorMixin, Drawing):
    '''
        creates a pie chart with a legend
    '''
    def __init__(self, data: list, seriesNames: list, colors: list=list(), width: int=270, height: int=100, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        self._add(self, Pie(), name='pie', validate=None, desc=None)
        self.pie.data = data
        if colors:
            self._colors = colors
        self.pie.height = 100
        self.pie.width = 100
        self.pie.x = 0
        self.pie.strokeWidth = 1
        self.pie.slices.strokeColor = DEFAULT_STROKE_COLOR
        self.pie.slices.strokeWidth = 0
        self._seriesNames = seriesNames
        self._add(self, Legend(), name='legend', validate=None, desc=None)
        self.legend.y = self.height/2
        self.legend.columnMaximum  = 6
        self.legend.y = self.height/2 + 10
        self.legend.x = 120
        self.legend.fontName = DEFAULT_FONT
        self.legend.strokeWidth = 0
        self.legend.strokeColor = DEFAULT_STROKE_COLOR
        self.legend.fontSize = 14
        self.legend.alignment='right'
        self.legend.subCols.rpad = 40
        for i, _ in enumerate(self.pie.data): self.pie.slices[i].fillColor = self._colors[i]
        self.legend.colorNamePairs = list(zip(self._colors, list(zip(self._seriesNames, map(lambda x: "{}{}".format(x, '%'), self.pie.data)))))
        
        
class ChartBar(_DrawingEditorMixin,Drawing):
    """
        creates a chart bar
        
        input:
            data (list)
            category_names (list): x axys names
            colors (list): bar colors
            width (float)
            height (float)
            
    """
    def __init__(self, data: list, category_names: list, colors: list, width=500, height=200, style='parallel', *args, **kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self._add(self,VerticalBarChart(),name='chart',validate=None,desc=None)
        self.chart.x = 30
        self.chart.y = 20
        self.chart.width=self.width - self.chart.x -10
        self.chart.height=self.height - self.chart.y -10
        self.chart.reversePlotOrder = 0
        
        self.chart.valueAxis.strokeWidth = 0.5
        self.chart.categoryAxis.strokeWidth = 0.5
        self.chart.categoryAxis.style = style
        self.chart.valueAxis.valueMin = 0
        self.chart.valueAxis.valueMax = 24
        self.chart.valueAxis.valueStep= 6
        self.chart.valueAxis.labelTextFormat= '%0.0f h'
        self.chart.data = data
        for index, color in enumerate(colors): self.chart.bars[index].fillColor = color 
        self.chart.bars.strokeWidth = 0.25
        self.chart.bars.strokeColor = DEFAULT_STROKE_COLOR
        self.chart.categoryAxis.categoryNames = category_names
        

class PieChartWorkingModes(_DrawingEditorMixin,Drawing):
    """
        creates a chart bar
        
        input:
            data (list)
            category_names (list): x axys names
            colors (list): bar colors
            width (float)
            height (float)
            
    """
    def __init__(self, data, data_trend, header_names: tuple, series_names: tuple, width=500, height=125, *args, **kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self._colors = WORKING_MODES_COLORS
        # font
        fontSize = 12
        fontName = DEFAULT_FONT
        self._add(self, Pie(), name='chart', validate=None, desc=None)
        # pie
        self.chart.y = 0
        self.chart.x = 0
        self.chart.height = 100
        self.chart.width = 100
        self.chart.slices.strokeColor = DEFAULT_STROKE_COLOR
        self.chart.slices.strokeWidth = 0.5
        self._add(self, Legend(), name='legend', validate=None, desc=None)
        self._add(self, Legend(), name='legendHeader', validate=None, desc=None)
        self.legendHeader.x = 150
        self.legendHeader.y = self.height - 10
        self.legendHeader.fontSize = fontSize
        self.legendHeader.fontName = fontName
        self.legendHeader.subCols[0].minWidth = 200
        self.legendHeader.subCols[0].align = 'left'
        self.legendHeader.subCols[1].minWidth = 80
        self.legendHeader.subCols[1].align = 'right'
        self.legendHeader.subCols[2].minWidth = 160
        self.legendHeader.subCols[2].align = 'right'
        self.legendHeader.subCols[3].minWidth = 1000 # needed to remove black rectangle
        black = PCMYKColor(0, 0, 0, 100)
        self.legendHeader.colorNamePairs = [(black, header_names + ('', ))]
        self.legend.x = 150
        self.legend.y = 90
        self.legend.fontSize = fontSize
        self.legend.fontName = fontName
        self.legend.dx = 8
        self.legend.dy = 8
        self.legend.dxTextSpace = 10
        self.legend.yGap = 0
        self.legend.deltay = 24
        self.legend.strokeColor = PCMYKColor(0,0,0,0)
        self.legend.strokeWidth = 0
        self.legend.columnMaximum = 99
        self.legend.alignment = 'right'
        self.legend.variColumn = 0
        self.legend.dividerDashArray = None
        self.legend.dividerWidth = 0.5
        self.legend.dividerOffsX = (0, 0)
        self.legend.dividerLines = 7
        self.legend.dividerOffsY = 12
        self.legend.subCols[0].align = 'left'
        self.legend.subCols[0].minWidth = 200
        self.legend.subCols[1].align = 'right'
        self.legend.subCols[1].align='numeric'
        self.legend.subCols[1].dx = -30
        self.legend.subCols[1].minWidth = 80
        self.legend.subCols[2].align = 'right'
        self.legend.subCols[2].align='numeric'
        self.legend.subCols[2].dx = -10
        self.legend.subCols[2].minWidth = 160
        # sample data
        self._seriesNames = series_names
        self._seriesData1 = data
        self._seriesData2 = data_trend
        formatter_time = DecimalFormatter(places=1, thousandSep=',', decimalSep='.', suffix=' h')
        formatter_trend = lambda x: DecimalFormatter(places=0, thousandSep=',', decimalSep='.', suffix=' %').format(x) if x != None else x
        sign_adder = lambda x: '-' if x== None else x if x.startswith('-') else '+{}'.format(x)
        names = list(zip(self._seriesNames,
        map(formatter_time, self._seriesData1),
        map(sign_adder, map(formatter_trend, self._seriesData2))))
        self.legend.colorNamePairs = list(zip(self._colors, names))
        self.chart.data  = self._seriesData1
        # apply colors to slices
        for i, _ in enumerate(self.chart.data): self.chart.slices[i].fillColor = self._colors[i]
        self.legend.deltax = 75
        self.legendHeader.subCols[0].minWidth = 100
        self.legend.subCols[0].minWidth = 90