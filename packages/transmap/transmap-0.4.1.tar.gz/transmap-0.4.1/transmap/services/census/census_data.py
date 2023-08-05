from .constants import TABLES_LIST1, TABLES_LIST2
from census import Census

class TransmapCensus(Census):

    def __init__(self,Census,year=None):
        self.c = Census
        self.year = year

    def acs5_block_group(self, stateFips=Census.ALL, tableName=None):
        ''' 
        With no arguments, this retrieves a list of all predefined tables 
        for the most recent year, for all states. 
 
        Args: 
            stateFips (str): The fips code for the state, e.g. "01" 
                 for Alabama. 
            tableName (str): The full table name, e.g. "B25024_001E". 
                Defaults to predifined list of tables. 
                 
 
        Returns: 
            # A list of Dicts, one per block group. 
                [ 
                    { 
                        'NAME': 'Block Group 5, Census Tract 10.01, Sebastian County, Arkansas', 
                        'GEO_ID': '1500000US051310010015', 
                        'state': '05', 
                        'county': '131', 
                        'tract': '001001', 
                        'block group': '5', 
                        'B25024_001E': 314.0, 
                        'B25024_002E': 152.0, 
                        'B25024_003E': 18.0, 
                        'B25024_004E': 25.0, 
                        'B25024_005E': 0.0, 
                        ...... 
                    }, 
                ] 
 
        ''' 
        results = [] 
 
        if tableName: 
            code = tableName + ",GEO_ID" 
            results = self.c.acs5.state_county_blockgroup(('NAME', code), stateFips, Census.ALL, Census.ALL) 
        else: 
            results = self.c.acs5.state_county_blockgroup(('NAME', TABLES_LIST1), stateFips, Census.ALL, Census.ALL) 
            results2 = self.c.acs5.state_county_blockgroup(('NAME', TABLES_LIST2), stateFips, Census.ALL, Census.ALL) 
 
            # Combine results 
            for index, item in enumerate(results2): 
                if results[index]['GEO_ID'] == item['GEO_ID']: 
                    results[index].update(item) 
                else: 
                    for block_group in results: 
                        if block_group['GEO_ID'] == item['GEO_ID']: 
                            block_group.update(item) 
 
        for item in results: 
            item['block_group'] = item.pop('block group')
            item['year'] = self.year
            item['type'] = 'acs5' 
            item['level'] = 'Block Group' 
 
        return results 

    def acs5_county(self, stateFips=Census.ALL, tableName=None):
        ''' 
        With no arguments, this retrieves a list of all predefined tables 
        for the most recent year, for all states. 
 
        Args: 
            stateFips (str): The fips code for the state, e.g. "01" 
                 for Alabama. 
            tableName (str): The full table name, e.g. "B25024_001E". 
                Defaults to predifined list of tables. 
                 
 
        Returns: 
            # A list of Dicts, one per county. 
                [ 
                    { 
                        'NAME': 'Sebastian County, Arkansas', 
                        'GEO_ID': '0500000US05131', 
                        'state': '05', 
                        'county': '131', 
                        'tract': null, 
                        'block group': null, 
                        'B25024_001E': 56841.0, 
                        'B25024_002E': 39715.0, 
                        'B25024_003E': 1519.0, 
                        'B25024_004E': 3669.0, 
                        'B25024_005E': 2455.0, 
                        ...... 
                    }, 
                ] 
 
        ''' 
        results = [] 
 
        if tableName: 
            code = tableName + ",GEO_ID" 
            results = self.c.acs5.state_county(('NAME', code), stateFips, Census.ALL) 
        else: 
            results = self.c.acs5.state_county(('NAME', TABLES_LIST1), stateFips, Census.ALL) 
            results2 = self.c.acs5.state_county(('NAME', TABLES_LIST2), stateFips, Census.ALL) 
 
            # Combine results 
            for index, item in enumerate(results2): 
                if results[index]['GEO_ID'] == item['GEO_ID']: 
                    results[index].update(item) 
                else: 
                    for county in results: 
                        if county['GEO_ID'] == item['GEO_ID']: 
                            county.update(item) 
 
        for item in results: 
            item['tract'] = None
            item['block_group'] = None
            item['year'] = self.year
            item['type'] = 'acs5' 
            item['level'] = 'County' 
 
        return results 


    def acs5_tract(self, stateFips=Census.ALL, tableName=None):
        ''' 
        With no arguments, this retrieves a list of all predefined tables 
        for the most recent year, for all states. 
 
        Args: 
            stateFips (str): The fips code for the state, e.g. "01" 
                 for Alabama. 
            tableName (str): The full table name, e.g. "B25024_001E". 
                Defaults to predifined list of tables. 
                 
 
        Returns: 
            # A list of Dicts, one per block group. 
                [ 
                    { 
                        'NAME': 'Census Tract 10.01, Sebastian County, Arkansas', 
                        'GEO_ID': '1400000US05131001001', 
                        'state': '05', 
                        'county': '131', 
                        'tract': '001001', 
                        'block group': null, 
                        'B25024_001E': 2514.0, 
                        'B25024_002E': 1797.0, 
                        'B25024_003E': 101.0, 
                        'B25024_004E': 199.0, 
                        'B25024_005E': 161.0, 
                        ...... 
                    }, 
                ] 
 
        ''' 
        results = [] 
 
        if tableName: 
            code = tableName + ",GEO_ID" 
            results = self.c.acs5.state_county_tract(('NAME', code), stateFips, Census.ALL, Census.ALL) 
        else: 
            results = self.c.acs5.state_county_tract(('NAME', TABLES_LIST1), stateFips, Census.ALL, Census.ALL) 
            results2 = self.c.acs5.state_county_tract(('NAME', TABLES_LIST2), stateFips, Census.ALL, Census.ALL) 
 
            # Combine results 
            for index, item in enumerate(results2): 
                if results[index]['GEO_ID'] == item['GEO_ID']: 
                    results[index].update(item) 
                else: 
                    for county in results: 
                        if county['GEO_ID'] == item['GEO_ID']: 
                            county.update(item) 
 
        for item in results: 
            item['block_group'] = None
            item['year'] = self.year
            item['type'] = 'acs5' 
            item['level'] = 'Tract' 
 
        return results 

    def acs1_county(self, stateFips=Census.ALL, tableName=None):
            ''' 
            With no arguments, this retrieves a list of all predefined tables 
            for the most recent year, for all states. 
 
            Args: 
                stateFips (str): The fips code for the state, e.g. "01" 
                    for Alabama. 
                tableName (str): The full table name, e.g. "B25024_001E". 
                    Defaults to predifined list of tables. 
                     
 
            Returns: 
                # A list of Dicts, one per county 
                    [ 
                        { 
                            'NAME': 'Sebastian County, Arkansas', 
                            'GEO_ID': '0500000US05131', 
                            'state': '05', 
                            'county': '131', 
                            'B25024_001E': 314.0, 
                            'B25024_002E': 152.0, 
                            'B25024_003E': 18.0, 
                            'B25024_004E': 25.0, 
                            'B25024_005E': 0.0, 
                            ...... 
                        }, 
                    ] 
 
            ''' 
            results = [] 
 
            if tableName: 
                code = tableName + ",GEO_ID" 
                results = self.c.acs1.state_county(('NAME', code), stateFips, Census.ALL) 
            else: 
                results = self.c.acs1.state_county(('NAME', TABLES_LIST1), stateFips, Census.ALL) 
                results2 = self.c.acs1.state_county(('NAME', TABLES_LIST2), stateFips, Census.ALL) 
                 
                # Combine results 
                for index, item in enumerate(results2): 
                    if results[index]['GEO_ID'] == item['GEO_ID']: 
                        results[index].update(item) 
                    else: 
                        for result in results: 
                            if result['GEO_ID'] == item['GEO_ID']: 
                                result.update(item) 
 
            for item in results: 
                item['type'] = 'acs1'
                item['year'] = self.year 
                item['level'] = 'County' 
 
            return results