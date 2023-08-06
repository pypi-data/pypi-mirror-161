from xmlrpc.client import DateTime
from .frigel_report_creator import FrigelReportCreator
from .consts import *
from .translations import Translations
from .charts.charts import ChartPieWithLegend, ChartBar, PieChartWorkingModes

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.graphics.shapes import Circle, Drawing, _DrawingEditorMixin
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, Table, TableStyle, KeepInFrame, Frame
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from reportlab.lib.colors import PCMYKColor
from reportlab.lib.formatters import DecimalFormatter

from typing import Union
from io import BytesIO
from datetime import datetime, timedelta
import numpy as np

class SyncroReportWeeklyCreator(FrigelReportCreator):
    '''
    Class for the creation of Syncro RS reports
    '''
    
    def __init__(self, operation_hours: list, operation_hours_prev: list, working_modes_hours: dict, working_modes_hours_prev: dict, molds_info: dict, start_date: datetime):
        '''
        input:
            operation_hours (list): list with the operation hours of the week
            operation_hours_prev (list): list with the operation hours of the previous week
            working_modes_hours (dict): {'standard': [10, 20,..], 'production': [10, 20,..], 'maintenance': [10, 20,..]}
            molds_info (dict):  {'name_mold': {'recipe': {'name_recipe': 86.78106666666667,...}, 
                                                'original_cycle': '-', 'on': 111.0573682054, 'average_cycle': 236.0401693610941, 
                                                'energy_consumption_syncro': 0, 'material_produced_syncro': 0, 'energy_consumption_standard': 0, 
                                                'material_produced_standard': 0}, ...}, 
            start_date (datetime): starting day
        '''
        self.operation_hours = operation_hours
        self.total_operation_hours = np.sum([0 if x == None else x for x in self.operation_hours])
        self.operation_hours_prev = operation_hours_prev
        self.total_operation_hours_prev = None if all(x is None for x in self.operation_hours_prev) else np.sum([0 if x == None else x for x in self.operation_hours_prev])
        self.working_modes_hours = working_modes_hours
        self.working_modes_hours_prev = working_modes_hours_prev
        self.working_modes_trend = [np.sum([0 if x == None else x for x in self.working_modes_hours[mode]])/np.sum([0 if x == None else x for x in self.working_modes_hours_prev[mode]])-100 if np.sum(0 if x == None else x for x in self.working_modes_hours_prev[mode])>0 else None\
            for mode in WORKING_MODE_TYPES]
        self.molds_info = molds_info
        self.start_date = start_date
        FrigelReportCreator.__init__(self)
        
           
    def generatePDF(self, dest_path=None, language: str='en') -> Union[BytesIO, str]:
        '''
        generate PDF file
        
        input:
            dest_path (str): save path, if None the PDF will be saved into a ByetsIO buffer
            
        output:
            dest_path if is not None, else the buffer containing the PDF
        '''
        if dest_path:
            pdf_file = dest_path
        else:
            pdf_file = BytesIO()
    
        self.canvas = canvas.Canvas(pdf_file , pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.width, self.height = A4
        self.organization = 'Frigel Firenze S.p.A.'
        self.logoPositionX = 5
        self.logoPositionY = 0
        self.horizontalMargin = 10
        self.lastPositionX = 0
        self.lastPositionY = DEFAULT_STARTING_POSITION
        
        self.translations = Translations(language)
        
        self.drawLogo()
        
        self.__add_machine_operation_paragraph()
        self.__add_operation_hours_pie()
        
        self.__add_working_hours_paragraph()
        self.__add_working_hours_chart()
        
        
        self.newPage()
        
        self.__add_working_modes_paragraph()
        self.__add_working_modes_data()
        
        self.__add_modes_hours_paragraph()
        self.__add_modes_hours_chart()

        self.newPage()

        self.__add_molds_used_paragraph()
        self.__add_molds_used_data()

        self.newPage()

        self.__add_recipe_for_mold_paragraph()
        self.__add_recipe_for_mold_data()
        
        self.canvas.save()
        
        return pdf_file
    
    # helper functions to create syncro PDF report
    #----------------------------------------------------------------------
    def __add_machine_operation_paragraph(self):
        text_machine = """<font size="24">
        {}
        </font>
        """.format(self.translations.getTranslation('Machine operation'))
        self.addSpacing(DEFAULT_SPACING)
        p_machine = Paragraph(text_machine, self.styles["Heading1"])
        self.drawOnCanvas(p_machine, 0, 0)
        
        
    def __add_operation_hours_pie(self):
        pie_table_width = self.width/2-self.horizontalMargin - 20
        drawing_circle = Drawing(CIRCLE_SIZE,CIRCLE_SIZE)
        drawing_circle.add(Circle(CIRCLE_SIZE,CIRCLE_SIZE,CIRCLE_SIZE, fillColor=DEFAULT_ON_COLOR, strokeColor=DEFAULT_STROKE_COLOR))
        
        table_on_time = Table(data=[[drawing_circle, self.translations.getTranslation('ON Time')]], colWidths=[CIRCLE_SIZE+8, None])
        table_on_time.setStyle([("FONTSIZE", (1,0), (1,0), 14),
                                ("FONTNAME", (1,0), (1,0), DEFAULT_FONT_BOLD),
                                ("VALIGN", (0,0), (-1,-1), 'BOTTOM')])
        table_on_hours = Table(data=[['{} h'.format(int(self.total_operation_hours))]])
        table_on_hours.setStyle([("FONTSIZE", (0,0), (0,0), 42),
                                 ("FONTSIZE", (1,0), (1,0), 14),
                                 ("FONTNAME", (0,0), (-1,-1), DEFAULT_FONT),
                                 ("VALIGN", (0,0), (-1,-1), 'BOTTOM')])
        
        data_table_right = [[table_on_time],
                            [table_on_hours],
                            ['{}%'.format(round(int((self.total_operation_hours/self.total_operation_hours_prev),2) if self.total_operation_hours_prev > 0 else 0))\
                                if self.total_operation_hours_prev != None else ''],
                            [self.translations.getTranslation('vs {}h (prev 7 days)').format(self.total_operation_hours_prev)] if self.total_operation_hours_prev != None else '']
        table_pie_right = Table(data_table_right, colWidths=pie_table_width/2, rowHeights=[None, None, 50, None])
        table_pie_right.setStyle([("ALIGN", (0,0), (-1,-1), "LEFT"),
                                  ("FONTSIZE", (0,0), (0,0), 14),
                                  ("FONTSIZE", (0,1), (0,1),  42),
                                  ("FONTNAME", (0,0), (-1,-1), DEFAULT_FONT),
                                  ("FONTSIZE", (0,2), (0,2), 14)])
        
        hours_on_percentage = round(self.total_operation_hours*100/(24*7), 1)
        pie_data = [hours_on_percentage, 100-hours_on_percentage]
        pie_chart_hours = ChartPieWithLegend(data=pie_data, seriesNames=[self.translations.getTranslation('ON'), self.translations.getTranslation('OFF')], _colors=[DEFAULT_ON_COLOR, DEFAULT_OFF_COLOR])
        
        data_pie_hours = [[pie_chart_hours, table_pie_right]]
        table_pie_hours = Table(data_pie_hours, colWidths=pie_table_width)
        table_pie_hours.setStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                            ("ALIGN", (1,0), (1,0), "CENTRE")])
        _, table_height = table_pie_hours.wrap(0, 0)
        self.addSpacing(DEFAULT_SPACING)
        self.drawOnCanvas(table_pie_hours, 0, table_height/3)
        
        
    def __add_working_hours_paragraph(self):
        text_machine = """<font size="24">
        {}
        </font>
        """.format(self.translations.getTranslation('Working hours (last 7 days)'))
        self.addSpacing(-15)
        p_machine = Paragraph(text_machine, self.styles["Heading1"])
        self.drawOnCanvas(p_machine, 0, 0)
        
        
    def __add_working_hours_chart(self):
        chart_data = [tuple(self.operation_hours), tuple(24-x if x != None else 0 for x in self.operation_hours)]
        chart_working_hours = ChartBar(data=chart_data,
                                       category_names=[(self.start_date+timedelta(days=x)).strftime("%d / %m") for x in range(7)],
                                       colors=[DEFAULT_ON_COLOR, DEFAULT_OFF_COLOR],
                                       style='stacked')
        self.addSpacing(DEFAULT_SPACING)
        self.drawOnCanvas(chart_working_hours, 0, chart_working_hours.height/3)
        
        
    def __add_working_modes_paragraph(self):
        text_machine = """<font size="24">
        {}
        </font>
        """.format(self.translations.getTranslation('Working modes'))
        self.addSpacing(DEFAULT_SPACING)
        p_machine = Paragraph(text_machine, self.styles["Heading1"])
        self.drawOnCanvas(p_machine, 0, 0)
        
        
    def __add_working_modes_data(self):
        data_pie = [np.sum(0 if x is None else x for x in self.working_modes_hours[mode]) for mode in WORKING_MODE_TYPES]
        pie_working_modes = PieChartWorkingModes(data=data_pie,
                                                 data_trend=self.working_modes_trend,
                                                 header_names=(self.translations.getTranslation('Phases'), 
                                                               self.translations.getTranslation('Time'),
                                                               self.translations.getTranslation('Trend (prev. week)'),),
                                                 series_names=[self.translations.getTranslation('Standard'),
                                                               self.translations.getTranslation('Production'),
                                                               self.translations.getTranslation('Maintenance')],)
        self.drawOnCanvas(pie_working_modes, 0, pie_working_modes.height/3)
        
    def __add_modes_hours_paragraph(self):
        text_machine = """<font size="24">
        {}
        </font>
        """.format(self.translations.getTranslation('Phases hours (last 7 days)'))
        p_machine = Paragraph(text_machine, self.styles["Heading1"])
        self.addSpacing(-10)
        self.drawOnCanvas(p_machine, 0, 0)
        
    def __add_modes_hours_chart(self):
        chart_data = [self.working_modes_hours[mode] for mode in WORKING_MODE_TYPES]
        chart_working_hours = ChartBar(data=chart_data,
                                       category_names=[(self.start_date+timedelta(days=x)).strftime("%d / %m") for x in range(7)],
                                       colors=WORKING_MODES_COLORS,)
        
        self.addSpacing(DEFAULT_SPACING)
        self.drawOnCanvas(chart_working_hours, 0, chart_working_hours.height/3)

    def __add_molds_used_paragraph(self):
        text_machine = """<font size="24">
        {}
        </font>
        """.format(self.translations.getTranslation('Molds used'))
        self.addSpacing(DEFAULT_SPACING)
        p_machine = Paragraph(text_machine, self.styles["Heading1"])
        self.drawOnCanvas(p_machine, 0, 0)

    def __add_molds_used_data(self):
        table_width = self.width/6-self.horizontalMargin
        list_key = self.molds_info.keys()
        list_molds = [[self.translations.getTranslation('Mold name'),self.translations.getTranslation('Time on'),
                        self.translations.getTranslation('Original cycle'),self.translations.getTranslation('Average cycle'), 
                        self.translations.getTranslation('KPI syncro'),self.translations.getTranslation('KPI standard')]]
        
        styleN = self.styles['Normal']
        styleN.wordWrap = 'CJK'
        styleN.fontName = DEFAULT_FONT_BOLD
        styleN.fontSize = 12
        
        for key in list_key:
            mold_name = Paragraph(key, styleN)
            list_molds.append([mold_name, '{} {}'.format(round(self.molds_info[key]['on'],2) if type(self.molds_info[key]['on']) == float else self.molds_info[key]['on'], 'h'), 
                            '{} {}'.format(round(self.molds_info[key]['original_cycle'],2) if type(self.molds_info[key]['original_cycle']) == float else self.molds_info[key]['original_cycle'], 'sec'),
                            '{} {}'.format(round(self.molds_info[key]['average_cycle'],2) if type(self.molds_info[key]['average_cycle'])== float else self.molds_info[key]['average_cycle'], 'sec'), 
                            '{} {}'.format(round(self.molds_info[key]['energy_consumption_syncro']/self.molds_info[key]['material_produced_syncro'],2) if self.molds_info[key]['material_produced_syncro']> 0 else 0, 'kWh/kg'),
                            '{} {}'.format(round(self.molds_info[key]['energy_consumption_standard']/self.molds_info[key]['material_produced_standard'],2) if self.molds_info[key]['material_produced_standard']> 0 else 0, 'kWh/kg')])
        data_molds_used = list_molds
        table_molds_used = Table(data_molds_used, colWidths=table_width)
        table_molds_used.setStyle([("ALIGN", (0,0), (0,-1), "LEFT"),
                                    ("ALIGN", (2,0), (-1,-0), "CENTER"),
                                    ("ALIGN", (1,0), (5,0), "RIGHT"),
                                    ("ALIGN", (1,1), (5,-1), "RIGHT"),
                                    ("FONTNAME", (0,0), (-1,-0), DEFAULT_FONT_BOLD),
                                    ("FONTNAME", (0,0), (0,-1), DEFAULT_FONT_BOLD),
                                    ("TEXTCOLOR", (0,1), (0,-1), colors.black),
                                    ("FONTSIZE", (0,0), (0,-1), 12),
                                    ("FONTSIZE", (0,0), (-1,0), 12),
                                    ('LINEABOVE', (0,1), (-1,-1), 1, colors.black),
                                  ])
        _, table_height = table_molds_used.wrap(0, 0)
        self.addSpacing(12)
        self.drawOnCanvas(table_molds_used, 0, table_height/3)

    def __add_recipe_for_mold_paragraph(self):
        text_machine = """<font size="24">
        {}
        </font>
        """.format(self.translations.getTranslation('Recipes'))
        self.addSpacing(DEFAULT_SPACING)
        p_machine = Paragraph(text_machine, self.styles["Heading3"])
        self.drawOnCanvas(p_machine, 0, 0)
    
    def __add_recipe_for_mold_data(self):
        table_width = self.width/3-self.horizontalMargin - 20
        list_key = self.molds_info.keys()
        
        styleN = self.styles['Normal']
        styleN.wordWrap = 'CJK'
        styleN.fontName = DEFAULT_FONT_BOLD
        styleN.fontSize = 12
        y = 25
        for key in list_key:
            text_mold = """<font size="24">
            {}
            </font>
            """.format(key)
            mold = Paragraph(text_mold, self.styles["Heading2"])
            self.addSpacing(-20)
            self.drawOnCanvas(mold, 5, y)
            list_recipes = [[self.translations.getTranslation('Recipe name'),self.translations.getTranslation('Time on')]]
            for key,value in self.molds_info[key]['recipes'].items():
                recipe_name = Paragraph(key, styleN)
                list_recipes.append([recipe_name, '{} {}'.format(round(value,2) if type(value) == float else value, 'h')])
            data_recipes_used = list_recipes
            table_recipes_used = Table(data_recipes_used, colWidths=table_width)
            table_recipes_used.setStyle([("ALIGN", (0,0), (0,-1), "LEFT"),
                                        ("ALIGN", (2,0), (-1,-0), "CENTER"),
                                        ("ALIGN", (1,0), (5,0), "RIGHT"),
                                        ("ALIGN", (1,1), (5,-1), "RIGHT"),
                                        ("FONTNAME", (0,0), (-1,-0), DEFAULT_FONT_BOLD),
                                        ("FONTNAME", (0,0), (0,-1), DEFAULT_FONT_BOLD),
                                        ("TEXTCOLOR", (0,1), (0,-1), colors.black),
                                        ("FONTSIZE", (0,0), (0,-1), 12),
                                        ("FONTSIZE", (0,0), (-1,0), 12),
                                        ('LINEABOVE', (0,1), (-1,-1), 1, colors.black),
                                    ])
            _, table_height = table_recipes_used.wrap(20, 10)
            self.drawOnCanvas(table_recipes_used, 0, table_height/2)
            y=20
        
    #----------------------------------------------------------------------