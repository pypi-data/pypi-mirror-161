MISSING_STRING = '__missing__'
AVAILABLE_LANGUAGES = ['en']

REPORT_TRANSLATIONS ={
    'Machine operation': {
        'en': 'Machine operation'
    },
    
    'ON Time': {
        'en': 'ON Time'
    },
    
    'vs {}h (prev 7 days)': {
        'en': 'vs {}h (prev 7 days)'
    },
    
    'ON': {
        'en': 'ON'
    },
    
    'OFF': {
        'en': 'OFF'
    },
 
    'Working hours (last 7 days)': {
        'en': 'Working hours (last 7 days)'
    },
    
    'Working modes': {
        'en': 'Working modes'
    },

    'Phases': {
        'en': 'Phases'
    },
    
    'Time': {
        'en': 'Time'
    },
    
    'Trend (prev. week)': {
        'en': 'Trend (prev. week)'
    },
    
    'Standard': {
        'en': 'Standard'
    },
    
    'Production': {
        'en': 'Production'
    },
    
    'Maintenance': {
        'en': 'Maintenance'
    },
    
    'Phases hours (last 7 days)': {
        'en': 'Phases hours (last 7 days)'
    },
    'Molds used':{
         'en': 'Molds used'
    },
    'Mold name':{
         'en': 'Mold name'
    }, 
    'Time on':{
         'en': 'Time on'
    },
    'Original cycle':{
         'en': 'Original cycle'
    },
    'Average cycle':{
         'en': 'Average cycle'
    }, 
    'KPI syncro':{
         'en': 'KPI syncro'
    },
    'KPI standard':{
         'en': 'KPI standard'
    },
    'Recipes':{
         'en': 'Recipes'
    },
    'Recipe name':{
         'en': 'Recipe name'
    },

}



class Translations():
    
    def __init__(self, language):
        '''
        
        '''
        self.language = language
        
    def getTranslation(self, id) -> str:
        try:
            return REPORT_TRANSLATIONS[id][self.language]
        except:
             try:
                 return REPORT_TRANSLATIONS[id][self.language]
             except:
                 return MISSING_STRING