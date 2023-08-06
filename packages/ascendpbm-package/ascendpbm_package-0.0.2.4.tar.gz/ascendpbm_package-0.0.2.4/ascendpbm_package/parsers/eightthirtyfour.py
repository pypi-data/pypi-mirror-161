import pandas as pd
import random

class process_834():
    def __init__(self,
                 path,
                 rename_dict = {
                    'REF-0F-1':'Subscriber Number', # needs person code appended to end of id
                    'REF-1L-1':'Special ID', # placing plan codes here per Trents request
                    'DMG-2':'Gender',	# 1=Male, 2=Female |gender_dict = {'M':'1','F':'2','U':'3'}
                    'DMG-D8-1':'Date of Birth', # needs YYYYMMDD format
                    'NM1-2':'Last Name',	
                    'NM1-3':'First Name',	
                    'NM1-4':'Middle Initial',	# 1 character |'NM15'[0:1]
                    'NM1-8':'SSN',
                    'N3-0':'Address Line 1',	
                    'N3-1':'Address Line 2',
                    'N4-0':'City',	
                    'N4-1':'State',	
                    'N4-2':'Patient Zip Code',	
                    'INS-0':'Subscriber Indicator',
                    'INS-1':'Relationship', # 0=Cardholder 1=Spouse 2-9=Children |rel_dict = {'18':'0', '01':'1',#person_code:person_code[-1:]}
                    'INS-4':'Status', #EHo standard does not accept C for cobra in this field. |if 'INS5' == 'C': status = 'A'
                    'DTP-348-D8-2':'Effective Date', # longer than normal element qualifiers
                    'DTP-349-D8-2':'Expiration Date',	# longer than normal element qualifiers
                    'DTP-336-D8-2':'Hire Date', # longer than normal element qualifiers
                    'PER-IP--HP-3':'Phone Number', # WARNING THIS IS WEIRD - Labeled as NM1 in 834 specs but segment header is PER. Tindall is weird.
                    }
                 ):
        '''path is a filepath to the 834, rename_dict is a dict constructed to map 834 segment elements to col names'''
        self.path = path
        self.rename_dict = rename_dict
    
    def get_filestring(self):
        '''test file path, returns as a string'''
        
        with open(self.path) as f:
            wholefile = f.read().replace('\n', '')
        
        return wholefile
    
    def get_all_segments(self):
        '''Segmenting and nesting, returns as dict of lists
        key: index of segment as appearing in file
        value: list of strings split by delimeters ~, then *, then :'''
        
        wholefile = self.get_filestring()
        segments = dict(zip(range(1,len(wholefile.split('~'))+1), wholefile.split('~')))
        segment_nest = {}
        for key, value in segments.items():
            if ':' in value:
                segment_nest[key] = value.split('*')
                second_split = []
                for subval in segment_nest[key]:
                    second_split.append(subval.split(':'))
                segment_nest[key] = second_split
            else:
                segment_nest[key] = value.split('*')
        
        return segment_nest
    
    def get_member_segments(self):
        ''''grouping segments by members' INS segments, returns as dict
        key: index of members' INS segments as appearing in file
        value: list of dicts where key = segment identifier, value = other elements'''
        
        segment_nest = self.get_all_segments()
        segment_nest_bymember = {}
        count = 0
        for minkey, value in segment_nest.items():
            if segment_nest[minkey][0] == 'INS':
                break
        for key, value in segment_nest.items():
            if value[0] == 'SE':
                break
            elif key >= minkey:
                if value[0] == 'INS':
                    count += 1
                    segment_nest_bymember[count] = [{value[0]: value[1:]}]
                else:
                    segment_nest_bymember[count].append({value[0]: value[1:]})
        
        return segment_nest_bymember

    def get_member_df(self, rename=True):
        '''Pulling relevant fields from grouped segments and cleaning up,
        returns as pandas df with below col names (make sure they stay in order)
        '''
        #Cleaning got hard because of duplicate REF1L segments in some bad files.
        #I tupled out all entries in lists below using:
        #(ALL SEGMENT IDs '-' SEPARATED-0INDEX OF ELEMENT VALUE STARTING AT 2ND ELEMENT, ELEMENT VALUE)
        #The odd indexing makes more sense if you look at the segment_nest_bymember.
        #This rename dict maps those pseudo-keys to human-readable names.
        #This allows for overwriting or dropping of duplicates,
        #currently overwriting in final nested loop (slow)...
        
        segment_nest_bymember = self.get_member_segments()
        members = {}
        for key, dictlist in segment_nest_bymember.items():
            dictlist_nodupes = []
            for segmentdict in dictlist:
                if segmentdict not in dictlist_nodupes:
                    dictlist_nodupes.append(segmentdict)
            dictlist = dictlist_nodupes
            members[key] = [('File Order Key', key)]
            renamekeys = []
            for segmentdict in dictlist:
                for renamekey in self.rename_dict.keys():
                    split_renamekey = renamekey.split('-')
                    segment_id = split_renamekey[0]
                    if segmentdict.get(segment_id):
                        try:
                            if split_renamekey[1:-1] == segmentdict[segment_id][0:len(split_renamekey)-2]:
                                members[key].append((renamekey, segmentdict[segment_id][int(split_renamekey[-1])]))
                                renamekeys.append(renamekey)
                        except IndexError:
                            members[key].append((renamekey, ''))
                            renamekeys.append(renamekey)
            nullkeys = [nullkey for nullkey in self.rename_dict.keys() if nullkey not in renamekeys]  
            if len(nullkeys) > 0:
                for nullkey in nullkeys:
                    members[key].append((nullkey, ''))
        
        df_tuples = pd.DataFrame(members, dtype=str).T
        df_members = pd.DataFrame(index=df_tuples.index, dtype=str)
        for idx, row in df_tuples.iterrows(): # this is the slow part, could we make DF more directly above?
            for value in row:
                df_members.loc[idx, value[0]] = value[1]
                
        if rename is True:
            df_members.rename(columns=self.rename_dict, inplace=True)
        
        return df_members

    def get_personcodes_byrank(self, group_abbr, generate_id=True):
        '''Takes the members df and assigns person codes, returns df.
        Follows this logic:
        if sub_ind = 'Y' and rel_code = '18', person code = '00',
        if sub_ind = 'N' and rel_code = '01', person code = '01',
        if sub_ind = 'N' and rel_code = '19', person code = '02':'xx' by desc birthdate.
        This should be used explicitly the first time ever processing an 834 without a CSV log.'''
        
        df_members = self.get_member_df()
        df_members.loc[(df_members['Subscriber Indicator'] == 'Y') &
                       (df_members['Relationship'] == '18'),
                       'Person Code'] = '00'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '01'),
                       'Person Code'] = '01'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '19'),
                       'Person Code'] = '02'
        df_members['Date of Birth'] = pd.to_datetime(df_members['Date of Birth'], format='%Y%m%d')
        grouping = df_members[df_members['Person Code'] == '02'].sort_values(['Date of Birth']).groupby(['Subscriber Number',
                                                                                                         'Relationship']).cumcount(ascending=False)
        df_members.loc[df_members['Person Code'] == '02', 'Person Code'] = df_members['Person Code'].astype(int) + grouping
        df_members['Person Code'] = df_members['Person Code'].astype(str).apply(lambda x: x.replace('.0','')).str.pad(2, 'left', '0')
        
        if generate_id is True:
            # When they send us subscriber numbers containing PHI, like a SSN, then...
            # Here we need to replace the subscriber numbers with our own member IDs
            replacement_memberid = {}
            for sub_numb in df_members['Subscriber Number'].unique():
                replacement_memberid[sub_numb] = group_abbr + str(random.randint(0, 9999999)).zfill(7)
            # Check for non-unique strings
            while len(pd.Series(list(replacement_memberid.values())).unique()) < len(df_members['Subscriber Number'].unique()):
                # Flip the replacement memberid dict
                flipped = {}
                for key, value in replacement_memberid.items():
                    if value not in flipped:
                        flipped[value] = [key]
                    else:
                        flipped[value].append(key)
                dupe_lists = list(filter(lambda x: len(x)>1, flipped.values()))
                # Get new IDs for any in the list of dupe lists
                for dupe_list in dupe_lists:
                    for dupe in dupe_list:
                        replacement_memberid[dupe] = group_abbr + str(random.randint(0, 9999999)).zfill(7)
            else:
                for sub_numb, memberid in replacement_memberid.items():
                    df_members.loc[df_members['Subscriber Number'] == sub_numb, 'Generated Subscriber ID'] = memberid
                
                df_members['Cardholder Number'] = df_members['Generated Subscriber ID'] + df_members['Person Code']

        else:
            # When they send us unique subscriber numbers that do not contain PHI
            df_members['Cardholder Number'] = df_members['Subscriber Number'] + df_members['Person Code']

        return df_members
    
    def get_personcodes_bycsv(self, csvpath, group_abbr, csvlog=True, generate_id=True):
        '''Takes the members df for today with assigned person codes,
        takes the previously created CSV path as an argument and makes another df,
        and merges the two with members df for today on the left when csvlog=False,
        or merges the two with outer join when csvlog=True.
        When csvlog=True, and the path is to an old log file, then...
        overwrites new person codes with old personcodes for dependents,
        and assigns new person codes to null (newly added) dependents.
        All the above necessitates making a new log file first, then using that to 
        ensure the person codes/cardholer numbers are assigned correctly 
        (outer vs left joining/overwriting behavior makes this a little tricky).
        See implementation files such as tindall_eligibility.py
        for details/examples of dual-running where first csvlog=True and then csvlog=False.'''
        
        df_members_now = self.get_personcodes_byrank(group_abbr)
        df_members_before = pd.read_csv(csvpath, dtype=str)
        df_members_before['Date of Birth'] = pd.to_datetime(df_members_before['Date of Birth'], format='%Y-%m-%d')
        
        # We need to check for duplicates again, this time by way of comparing to the past
        # the worry here is some 1 in 10 million chance that a newly generated ID is equal to some old inactive one :P
        if generate_id is True:
            # New subscribers as determined by group's codings...
            new_families = df_members_now.loc[~df_members_now['Subscriber Number'].isin(df_members_before['Subscriber Number']),
                                              ['Subscriber Number', 'Generated Subscriber ID', 'Cardholder Number', 'Person Code']]
            # ... who also have generated ID that matches one assigned to someone else before...
            dupe_ids = new_families.loc[new_families['Generated Subscriber ID'].isin(df_members_before['Generated Subscriber ID']), :]
            dupe_ids_index = dupe_ids.index
            while len(dupe_ids) > 0:
            # ... get a new ID ...
                for subscriber_number in dupe_ids['Subscriber Number'].unique():
                    new_id = group_abbr + str(random.randint(0, 9999999)).zfill(7)
                    # this re-checks that the ID isn't in the new batch
                    while pd.Series(new_id).isin(pd.concat((df_members_now['Generated Subscriber ID'], df_members_before['Generated Subscriber ID']))):
                        new_id = group_abbr + str(random.randint(0, 9999999)).zfill(7)
                    new_families.loc[new_families['Subscriber Number'] == subscriber_number, 'Generated Subscriber ID'] = new_id
                    new_families.loc[new_families['Subscriber Number'] == subscriber_number, 'Cardholder Number'] = new_id + new_families.loc[new_families['Subscriber Number'] == subscriber_number, 'Person Code']
                    dupe_ids = new_families.loc[new_families['Generated Subscriber ID'].isin(df_members_before['Generated Subscriber ID']), :]
            else:
                for idx in dupe_ids_index:
                    df_members_now.loc[idx, ['Generated Subscriber ID', 'Cardholder Number']] = new_families.loc[idx, ['Generated Subscriber ID', 'Cardholder Number']]

        # We'll remake this so need to drop the audit column
        for df in [df_members_now, df_members_before]:
            try:
                del df['_merge']
            except KeyError:
                continue

        if csvlog is True:
            # CSV to now be a running log, requiring outer joins
            indexcol = 'index'
            df_members_merged = df_members_now.merge(df_members_before,
                                                    how='outer',
                                                    on=('Subscriber Number',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Last Name',
                                                        'First Name'),
                                                    indicator=True
                                                    )
            
        else:
            # If creating a standard EHO file rather than a log, we can just use left join
            # Requires we already created the log for today!
            indexcol = 'File Order Key_x'
            df_members_merged = df_members_now.merge(df_members_before,
                                                    how='left',
                                                    on=('Subscriber Number',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Last Name',
                                                        'First Name'),
                                                    indicator=True
                                                    ).set_index(indexcol, drop=False)

        if generate_id is True:
            # If our own IDs are getting generated, then we need to keep the old ones...
            df_members_merged['Generated Subscriber ID'] = df_members_merged['Generated Subscriber ID_y'].fillna(df_members_merged['Generated Subscriber ID_x'])
            df_members_now['Generated Subscriber ID'] = df_members_merged['Generated Subscriber ID']
            df_members_merged['Cardholder Number'] = df_members_merged['Cardholder Number_y'].fillna(df_members_merged['Cardholder Number_x'])
            df_members_now['Cardholder Number'] = df_members_merged['Cardholder Number']
            
            
            # Grab old person codes as well...
            if csvlog is True:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Generated Subscriber ID',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Last Name',
                                                        'First Name',
                                                        'Person Code_x',
                                                        'Person Code_y']
                                                        ]
            else:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Generated Subscriber ID',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Person Code_y',
                                                        indexcol,]
                                                        ]
            # Note that these Person Code_y values (old ones) will end up null if no one is
            # found in the old file using the matching criteria above
            # this is important to remember for the overwriting logic below
        else: # we can just skip all the above and use subcriber numbers if the client sends good (non-PHI) ones
            if csvlog is True:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Person Code_x',
                                                        'Person Code_y']
                                                        ]
            else:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Person Code_y',
                                                        indexcol,]
                                                        ]



        # Newly added dependents will have null values (I saw NaN initially),
        # need to fill in with new unique values
        # Taking max for the family, adding 1 to that, and adding cumulative counts for nulls to that
        dependents_codes.loc[dependents_codes['Person Code_y'].notnull(),
                             'Person Code'] = dependents_codes[dependents_codes['Person Code_y'].notnull()]['Person Code_y'].astype(int)
        max_codes = dependents_codes.groupby(['Subscriber Number'])['Person Code'].max()
        max_codes.name = 'Max Person Code'
        max_codes[max_codes.isnull()] = 1
        if csvlog is True:
            dependents_codes = dependents_codes.merge(max_codes, how='left', on=('Subscriber Number'))
        else:
            dependents_codes = dependents_codes.merge(max_codes, how='left', on=('Subscriber Number')).set_index(indexcol)
        dependents_codes.loc[dependents_codes['Person Code'].isnull(), 'Cum Counts'] = dependents_codes[dependents_codes['Person Code'].isnull()].sort_values(['Date of Birth']).groupby('Subscriber Number').cumcount(ascending=False)
        dependents_codes.loc[dependents_codes['Person Code'].isnull(), 'Person Code'] = dependents_codes['Cum Counts'] + dependents_codes['Max Person Code'] + 1
        dependents_codes['Person Code'] = dependents_codes['Person Code'].astype(str).apply(lambda x: x.replace('.0','')).str.pad(2, 'left', '0')
        if generate_id is True:
            dependents_codes['Cardholder Number'] = dependents_codes['Generated Subscriber ID'] + dependents_codes['Person Code']
        else:
            dependents_codes['Cardholder Number'] = dependents_codes['Subscriber Number'] + dependents_codes['Person Code']
        
        if csvlog is True: # if it's a log we have to merge back in cus indexes won't match
            # A little repititious but we're cleaning up before the merge to keep it simple...
            for col in df_members_merged.columns:
                if col.endswith('_y'):
                    df_members_merged[col[:-2]] = df_members_merged[col].fillna(df_members_merged[col[:-2]+'_x'])
                    df_members_merged.drop(columns=[col, col[:-2]+'_x'], inplace=True)
            # ... merging in the new dependent codes...
            df_members_merged.merge(dependents_codes,
                                    how='left',
                                    on=('Subscriber Number',
                                        'Relationship',
                                        'Date of Birth',
                                        'Last Name',
                                        'First Name')
                                    )
            # ... and we're cleaning up again for the new person code/cardholder number cols this time
            for col in df_members_merged.columns:
                if col.endswith('_y'):
                    df_members_merged[col[:-2]] = df_members_merged[col].fillna(df_members_merged[col[:-2]+'_x'])
                    df_members_merged.drop(columns=[col, col[:-2]+'_x'], inplace=True)
                    
            # I realized this would act as an easy spot to add a print flag, so here's that :)
            df_members_merged['Print Card'] = 'N'
            print_me = df_members_merged.loc[~df_members_merged['Cardholder Number'].isin(df_members_before['Cardholder Number']), :].index
            df_members_merged.loc[print_me, 'Print Card'] = 'Y'
            
            return df_members_merged
        else:
            # if we're creating EHO standard file,
            # then indexes will match so we can just use those instead of a messy/slow merge process
            df_members_now.loc[df_members_now['Relationship'] == '19',
                            ['Person Code', 'Cardholder Number']
                            ] = dependents_codes[['Person Code', 'Cardholder Number']]
            
            # I realized this would act as an easy spot to add a print flag, so here's that :)
            # this relies on us creating the same-day print flag via log file boolean above
            try:
                df_members_now['Print Card'] = df_members_merged['Print Card']
            except KeyError:
                pass
            
            return df_members_now

    def eho_standard(self,
                     df_members,
                     group_number,
                     id_is_ssn,
                     address_use_flag = 'P',
                     max_length_dict = {
                        'Group Number':8,
                        'Cardholder Number':11,
                        'Date of Birth':8,  
                        'Last Name':15,     
                        'First Name':12,    
                        'Middle Initial':1,     
                        'Patient Zip Code':5,   
                        'Gender':1,     
                        'Relationship':1,   
                        'Status':1,     
                        'Effective Date':6,     
                        'Expiration Date':6,    
                        'Special ID':15,    
                        'Alternate Insurance':1,    
                        'Smoke Count':1,    
                        'Location':9,   
                        'Print Card':1,     
                        'HICN':11,  
                        'Language':1,   
                        'Federal Employee':1,   
                        'Benefit Code':3,   
                        'Required NABP':7,  
                        'Required DEA':10,  
                        'Days Supply':4,    
                        'SSN':9,   
                        'Catastrophic Coverage':1,  
                        'Telephonic Code':2,    
                        'Restricted Flag':1,    
                        'Ignore Inactive WC':1,     
                        'Ignore WC ED':1,   
                        'Deceased':1 ,  
                        'Invoice Class':24,     
                        'Diagnosis':30,     
                        'Allow Compound':1,     
                        'Facility Type':1,  
                        'Cardholder SSN':9,     
                        'Address Use Flag':1,   
                        'Address Line 1':30,    
                        'Address Line 2':30,   
                        'Address Line 3':30,   
                        'City':15,  
                        'State':2,  
                        'Zip Code':10,  
                        'Phone Number':12,  
                        'Alt Address Line 1':30,    
                        'Alt Address Line 2':30,    
                        'Alt Address Line 3':30,    
                        'Alt City':15,  
                        'Alt State':2,  
                        'Alt Zip Code':10,  
                        'Alt Phone Number':12,  
                        'Email Address':50,     
                    }
                    ):
        '''This returns an EHO-standard df from the df passed into df_members parameter
        The EHO standard shouldn't be used as input in any other method...
        It's truncated and has extra/duplicate cols in it.
        So it's great output but not preferred input for a faithful reproduction of 834'''
        
        df_members_eho = pd.DataFrame(columns=list(max_length_dict.keys()), dtype=str)
        for col in [col for col in df_members_eho if col in df_members.columns]:
            df_members_eho[col] = df_members[col]
        if id_is_ssn is True:
            df_members_eho['Cardholder SSN'] = df_members['Subscriber Number']
        df_members_eho['Group Number'] = group_number
        df_members_eho['Date of Birth'] = df_members_eho['Date of Birth'].dt.strftime('%Y%m%d')
        df_members_eho.loc[df_members_eho['Relationship'] == '18', 'Relationship'] = '1'
        df_members_eho.loc[df_members_eho['Relationship'] == '01', 'Relationship'] = '2'
        df_members_eho.loc[df_members_eho['Relationship'] == '19', 'Relationship'] = '3'
        df_members_eho['Benefit Code'] = df_members_eho['Status']
        df_members_eho.loc[df_members_eho['Benefit Code'] == 'C', 'Benefit Code'] = 'COB'
        df_members_eho.loc[~df_members_eho['Status'].isin(['A', 'I']), 'Status'] = 'A'
        df_members_eho['Effective Date'] = df_members_eho['Effective Date'].str[2:]
        df_members_eho['Expiration Date'] = df_members_eho['Expiration Date'].str[2:]
        df_members_eho['Address Use Flag'] = address_use_flag
        #df_members_eho['Address Line 3'] = df_members_eho['City'] + ', ' + df_members_eho['State'] + ' ' + df_members_eho['Patient Zip Code']
        df_members_eho['Zip Code'] = df_members_eho['Patient Zip Code']
        df_members_eho['Phone Number'] = df_members_eho['Phone Number'].str[0:3] + '-' + df_members_eho['Phone Number'].str[3:6] + '-' + df_members_eho['Phone Number'].str[6:]
        df_members_eho.loc[df_members_eho['Phone Number'] == '--', 'Phone Number'] = ''
        for col, strip_index in max_length_dict.items():
            df_members_eho[col] = df_members_eho[col].str[:strip_index]
        
        return df_members_eho
        
    
    def write_csv(self, write_path, group_abbr, id_is_ssn=True,
                  how='plain', read_csvpath=None, eho_standard=False,
                  group_number=None, csvlog=True):
        '''takes write_path as input, writes csv to this location.
        takes read_csvpath as optional input, default is None but it should be a path string.
        read_csvpath is necessary input when how = 'bycsv'.
        how parameter determines what kind of csv is written:
        how='plain' is a no person codes/Cardholder Numbers df with 834 segment names
        how='byrank' is a person-code-df only considering the current day's 834
        how='bycsv' is a person-code-df considering historical csv and current day's 834
        eho_standard is just for EHO's benefit:
        group_number is a constant identifier passed into eho_standard()
        DO NOT PASS EHO_STANDARD FILES AS INPUT ABOVE,
        THEIR FORMAT IS REPETITIVE COMPARED TO 834 AND MAX LENGTHS CAN CAUSE DATA LOSS
        It's a bit slow but I plan to run the whole thing twice for jobs'''
        
        if how=='plain':
            df_members = self.get_member_df(rename=False)
        elif how=='byrank':
            df_members = self.get_personcodes_byrank(group_abbr)
        elif how=='bycsv':
            if read_csvpath is None:
                raise Exception("The read_csvpath param must be defined to use how='bycsv'")
            df_members = self.get_personcodes_bycsv(read_csvpath, group_abbr, csvlog)
        else:
            raise Exception("The how param must be one of 'plain', 'byrank', or 'bycsv'")
            return None
        
        if eho_standard == True:
            df_members = self.eho_standard(df_members, group_number, id_is_ssn)
        
        df_members.to_csv(write_path, index=False)
        return print('CSV written to path: ' + write_path)
    
# This one is a newer, & untested, version available starting in package version 0.0.1.49
# It tries to prefer SSN as join criteria when possible,
# but also fills in the holes with the alternative join criteria when SSN is blank/null by row.
# Alternative criteria: subscriber number, relationship, dob, names
# The idea is to prevent new IDs from getting generated whenever group realizes a mistake in those alternative criteria cols,
# but also the group is not sending us unique patient ID numbers we can use.
# Question: How do we fill in the null values of alternative criteria cols after joins
# when selectively using the SSN as join criteria yet needing full alternative criteria to set person codes?
# Note: This filling in occurs after the merges in get_personcodes_bycsv().
# Do we prefer new vs old? Probably new, right (to keep Tindall's currernt values)?
# Does the preference change if it's log or final output? Needs testing/auditing through multiple files to know for sure...
# Also not sure how to handle duplication in the logs due to previously using alternative critera.
# Testing would be easier on a fresh group.
# This is all patching over a kind of double-bind as much as possible, but it'll never be perfect as long as member IDs are null.
# Getting asked to move on to another project, so no time for this right now. :(
        
class process_834_test():
    def __init__(self,
                 path,
                 rename_dict = {
                    'REF-0F-1':'Subscriber Number', # needs person code appended to end of id
                    'REF-1L-1':'Special ID', # placing plan codes here per Trents request
                    'DMG-2':'Gender',	# 1=Male, 2=Female |gender_dict = {'M':'1','F':'2','U':'3'}
                    'DMG-D8-1':'Date of Birth', # needs YYYYMMDD format
                    'NM1-2':'Last Name',	
                    'NM1-3':'First Name',	
                    'NM1-4':'Middle Initial',	# 1 character |'NM15'[0:1]
                    'NM1-8':'SSN',
                    'N3-0':'Address Line 1',	
                    'N3-1':'Address Line 2',
                    'N4-0':'City',	
                    'N4-1':'State',	
                    'N4-2':'Patient Zip Code',	
                    'INS-0':'Subscriber Indicator',
                    'INS-1':'Relationship', # 0=Cardholder 1=Spouse 2-9=Children |rel_dict = {'18':'0', '01':'1',#person_code:person_code[-1:]}
                    'INS-4':'Status', #EHo standard does not accept C for cobra in this field. |if 'INS5' == 'C': status = 'A'
                    'DTP-348-D8-2':'Effective Date', # longer than normal element qualifiers
                    'DTP-349-D8-2':'Expiration Date',	# longer than normal element qualifiers
                    'DTP-336-D8-2':'Hire Date', # longer than normal element qualifiers
                    'PER-IP--HP-3':'Phone Number', # WARNING THIS IS WEIRD - Labeled as NM1 in 834 specs but segment header is PER. Tindall is weird.
                    }
                 ):
        '''path is a filepath to the 834, rename_dict is a dict constructed to map 834 segment elements to col names'''
        self.path = path
        self.rename_dict = rename_dict
    
    def get_filestring(self):
        '''test file path, returns as a string'''
        
        with open(self.path) as f:
            wholefile = f.read().replace('\n', '')
        
        return wholefile
    
    def get_all_segments(self):
        '''Segmenting and nesting, returns as dict of lists
        key: index of segment as appearing in file
        value: list of strings split by delimeters ~, then *, then :'''
        
        wholefile = self.get_filestring()
        segments = dict(zip(range(1,len(wholefile.split('~'))+1), wholefile.split('~')))
        segment_nest = {}
        for key, value in segments.items():
            if ':' in value:
                segment_nest[key] = value.split('*')
                second_split = []
                for subval in segment_nest[key]:
                    second_split.append(subval.split(':'))
                segment_nest[key] = second_split
            else:
                segment_nest[key] = value.split('*')
        
        return segment_nest
    
    def get_member_segments(self):
        ''''grouping segments by members' INS segments, returns as dict
        key: index of members' INS segments as appearing in file
        value: list of dicts where key = segment identifier, value = other elements'''
        
        segment_nest = self.get_all_segments()
        segment_nest_bymember = {}
        count = 0
        for minkey, value in segment_nest.items():
            if segment_nest[minkey][0] == 'INS':
                break
        for key, value in segment_nest.items():
            if value[0] == 'SE':
                break
            elif key >= minkey:
                if value[0] == 'INS':
                    count += 1
                    segment_nest_bymember[count] = [{value[0]: value[1:]}]
                else:
                    segment_nest_bymember[count].append({value[0]: value[1:]})
        
        return segment_nest_bymember

    def get_member_df(self, rename=True):
        '''Pulling relevant fields from grouped segments and cleaning up,
        returns as pandas df with below col names (make sure they stay in order)
        '''
        #Cleaning got hard because of duplicate REF1L segments in some bad files.
        #I tupled out all entries in lists below using:
        #(ALL SEGMENT IDs '-' SEPARATED-0INDEX OF ELEMENT VALUE STARTING AT 2ND ELEMENT, ELEMENT VALUE)
        #The odd indexing makes more sense if you look at the segment_nest_bymember.
        #This rename dict maps those pseudo-keys to human-readable names.
        #This allows for overwriting or dropping of duplicates,
        #currently overwriting in final nested loop (slow)...
        
        segment_nest_bymember = self.get_member_segments()
        members = {}
        for key, dictlist in segment_nest_bymember.items():
            dictlist_nodupes = []
            for segmentdict in dictlist:
                if segmentdict not in dictlist_nodupes:
                    dictlist_nodupes.append(segmentdict)
            dictlist = dictlist_nodupes
            members[key] = [('File Order Key', key)]
            renamekeys = []
            for segmentdict in dictlist:
                for renamekey in self.rename_dict.keys():
                    split_renamekey = renamekey.split('-')
                    segment_id = split_renamekey[0]
                    if segmentdict.get(segment_id):
                        try:
                            if split_renamekey[1:-1] == segmentdict[segment_id][0:len(split_renamekey)-2]:
                                members[key].append((renamekey, segmentdict[segment_id][int(split_renamekey[-1])]))
                                renamekeys.append(renamekey)
                        except IndexError:
                            members[key].append((renamekey, ''))
                            renamekeys.append(renamekey)
            nullkeys = [nullkey for nullkey in self.rename_dict.keys() if nullkey not in renamekeys]  
            if len(nullkeys) > 0:
                for nullkey in nullkeys:
                    members[key].append((nullkey, ''))
        
        df_tuples = pd.DataFrame(members, dtype=str).T
        df_members = pd.DataFrame(index=df_tuples.index, dtype=str)
        for idx, row in df_tuples.iterrows(): # this is the slow part, could we make DF more directly above?
            for value in row:
                df_members.loc[idx, value[0]] = value[1]
                
        if rename is True:
            df_members.rename(columns=self.rename_dict, inplace=True)
        
        return df_members

    def get_personcodes_byrank(self, group_abbr, generate_id=True):
        '''Takes the members df and assigns person codes, returns df.
        Follows this logic:
        if sub_ind = 'Y' and rel_code = '18', person code = '00',
        if sub_ind = 'N' and rel_code = '01', person code = '01',
        if sub_ind = 'N' and rel_code = '19', person code = '02':'xx' by desc birthdate.
        This should be used explicitly the first time ever processing an 834 without a CSV log.'''
        
        df_members = self.get_member_df()
        df_members.loc[(df_members['Subscriber Indicator'] == 'Y') &
                       (df_members['Relationship'] == '18'),
                       'Person Code'] = '00'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '01'),
                       'Person Code'] = '01'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '19'),
                       'Person Code'] = '02'
        df_members['Date of Birth'] = pd.to_datetime(df_members['Date of Birth'], format='%Y%m%d')
        grouping = df_members[df_members['Person Code'] == '02'].sort_values(['Date of Birth']).groupby(['Subscriber Number',
                                                                                                         'Relationship']).cumcount(ascending=False)
        df_members.loc[df_members['Person Code'] == '02', 'Person Code'] = df_members['Person Code'].astype(int) + grouping
        df_members['Person Code'] = df_members['Person Code'].astype(str).apply(lambda x: x.replace('.0','')).str.pad(2, 'left', '0')
        
        if generate_id is True:
            # When they send us subscriber numbers containing PHI, like a SSN, then...
            # Here we need to replace the subscriber numbers with our own member IDs
            replacement_memberid = {}
            for sub_numb in df_members['Subscriber Number'].unique():
                replacement_memberid[sub_numb] = group_abbr + str(random.randint(0, 9999999)).zfill(7)
            # Check for non-unique strings
            while len(pd.Series(list(replacement_memberid.values())).unique()) < len(df_members['Subscriber Number'].unique()):
                # Flip the replacement memberid dict
                flipped = {}
                for key, value in replacement_memberid.items():
                    if value not in flipped:
                        flipped[value] = [key]
                    else:
                        flipped[value].append(key)
                dupe_lists = list(filter(lambda x: len(x)>1, flipped.values()))
                # Get new IDs for any in the list of dupe lists
                for dupe_list in dupe_lists:
                    for dupe in dupe_list:
                        replacement_memberid[dupe] = group_abbr + str(random.randint(0, 9999999)).zfill(7)
            else:
                for sub_numb, memberid in replacement_memberid.items():
                    df_members.loc[df_members['Subscriber Number'] == sub_numb, 'Generated Subscriber ID'] = memberid
                
                df_members['Cardholder Number'] = df_members['Generated Subscriber ID'] + df_members['Person Code']

        else:
            # When they send us unique subscriber numbers that do not contain PHI
            df_members['Cardholder Number'] = df_members['Subscriber Number'] + df_members['Person Code']

        return df_members
    
    def get_personcodes_bycsv(self, csvpath, group_abbr, csvlog=True, generate_id=True):
        '''Takes the members df for today with assigned person codes,
        takes the previously created CSV path as an argument and makes another df,
        and merges the two with members df for today on the left when csvlog=False,
        or merges the two with outer join when csvlog=True.
        When csvlog=True, and the path is to an old log file, then...
        overwrites new person codes with old personcodes for dependents,
        and assigns new person codes to null (newly added) dependents.
        All the above necessitates making a new log file first, then using that to 
        ensure the person codes/cardholer numbers are assigned correctly 
        (outer vs left joining/overwriting behavior makes this a little tricky).
        See implementation files such as tindall_eligibility.py
        for details/examples of dual-running where first csvlog=True and then csvlog=False.'''
        
        df_members_now = self.get_personcodes_byrank(group_abbr)
        df_members_before = pd.read_csv(csvpath, dtype=str)
        df_members_before['Date of Birth'] = pd.to_datetime(df_members_before['Date of Birth'], format='%Y-%m-%d')
        
        # Need to drop the audit column '_merge' (we'll remake it)
        # Also need to create a merge ID as a coalesce of SSN, janky-ID
        for df in [df_members_now, df_members_before]:
            # drop _merge audit col
            for col in ['_merge', 'merge_id']:
                try:
                    del df[col]
                except KeyError:
                    continue
            # create an ID col for merges, first prep/clean...
            merge_headers = ['SSN', 'Subscriber Number', 'Relationship', 'Date of Birth', 'Last Name', 'First Name']
            merge_ids = []
            for idx, header in enumerate(merge_headers):
                merge_ids.append('merge_id' + str(idx))
                if header == 'Date of Birth':
                    df[merge_ids[idx]] = df[header].dt.strftime('%Y%m%d')
                else:
                    df[merge_ids[idx]] = df[header].astype(str).str.replace(' ', '').str.upper()
                df.loc[df[merge_ids[idx]] == '', merge_ids[idx]] = None
            # ... then create. Note these indices after merge_id must map to list given in above loop
            # SSN or some other unique ID for each patient must be the first element for this to be at all worthwhile
            # following headers make up an alternative ID that's concatenated, with no spaces, and all upper case
            # doing it this way, in part, to guarantee we not mess with the cols themselves during cleaning            
            df['merge_id'] = df[merge_ids[0]].combine_first(df[merge_ids[1]].str.cat(df[merge_ids[2:]]))
            # drop the intermediary cols
            for col in merge_ids:
                try:
                    del df[col]
                except KeyError:
                    continue
                
        # We need to check for duplicates again, this time by way of comparing to the past
        # the worry here is some 1 in 10 million chance that a newly generated ID is equal to some old inactive one :P
        if generate_id is True:
            # New subscribers as determined by group's codings...
            new_families = df_members_now.loc[~df_members_now['Subscriber Number'].isin(df_members_before['Subscriber Number']),
                                              ['Subscriber Number', 'Generated Subscriber ID', 'Cardholder Number', 'Person Code']]
            # ... who also have generated ID that matches one assigned to someone else before...
            dupe_ids = new_families.loc[new_families['Generated Subscriber ID'].isin(df_members_before['Generated Subscriber ID']), :]
            dupe_ids_index = dupe_ids.index
            while len(dupe_ids) > 0:
            # ... get a new ID ...
                for subscriber_number in dupe_ids['Subscriber Number'].unique():
                    new_id = group_abbr + str(random.randint(0, 9999999)).zfill(7)
                    # this re-checks that the ID isn't in the new batch
                    while pd.Series(new_id).isin(pd.concat((df_members_now['Generated Subscriber ID'], df_members_before['Generated Subscriber ID']))):
                        new_id = group_abbr + str(random.randint(0, 9999999)).zfill(7)
                    new_families.loc[new_families['Subscriber Number'] == subscriber_number, 'Generated Subscriber ID'] = new_id
                    new_families.loc[new_families['Subscriber Number'] == subscriber_number, 'Cardholder Number'] = new_id + new_families.loc[new_families['Subscriber Number'] == subscriber_number, 'Person Code']
                    dupe_ids = new_families.loc[new_families['Generated Subscriber ID'].isin(df_members_before['Generated Subscriber ID']), :]
            else:
                for idx in dupe_ids_index:
                    df_members_now.loc[idx, ['Generated Subscriber ID', 'Cardholder Number']] = new_families.loc[idx, ['Generated Subscriber ID', 'Cardholder Number']]

        if csvlog is True:
            # CSV to now be a running log, requiring outer joins
            indexcol = 'index'
            df_members_merged = df_members_now.merge(df_members_before,
                                                    how='outer',
                                                    on='merge_id',
                                                    indicator=True
                                                    )            
        else:
            # If creating a standard EHO file rather than a log, we can just use left join
            # Requires we already created the log for today!
            indexcol = 'File Order Key_x'
            df_members_merged = df_members_now.merge(df_members_before,
                                                    how='left',
                                                    on='merge_id',
                                                    indicator=True
                                                    ).set_index(indexcol, drop=False)

        # cleaning, preferring new values here, using header_looper cols above except SSN
        # not cleaning SSN because I didn't touch it in older code before creating the merge_id
        # print(df_members_merged.loc[df_members_merged.index.duplicated(keep=False), ['merge_id', 'Cardholder Number_x', 'Cardholder Number_y']])
        # print(df_members_now.loc[df_members_now.index.duplicated(keep=False), ['merge_id', 'Cardholder Number_x', 'Cardholder Number_y']])
        for header in merge_headers[1:]:
            try:
                df_members_merged[header] = df_members_merged[header + '_x'].fillna(df_members_merged[header + '_y'])
                df_members_now[header] = df_members_merged[header]
            except KeyError:
                continue

        if generate_id is True:
            # If our own IDs are getting generated, then we need to keep the old ones...
            df_members_merged['Generated Subscriber ID'] = df_members_merged['Generated Subscriber ID_y'].fillna(df_members_merged['Generated Subscriber ID_x'])
            df_members_now['Generated Subscriber ID'] = df_members_merged['Generated Subscriber ID']
            df_members_merged['Cardholder Number'] = df_members_merged['Cardholder Number_y'].fillna(df_members_merged['Cardholder Number_x'])
            df_members_now['Cardholder Number'] = df_members_merged['Cardholder Number']
            
            
            # Grab old person codes as well...
            if csvlog is True:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Generated Subscriber ID',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Last Name',
                                                        'First Name',
                                                        'Person Code_x',
                                                        'Person Code_y']
                                                        ]
            else:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Generated Subscriber ID',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Person Code_y',
                                                        indexcol,]
                                                        ]
            # Note that these Person Code_y values (old ones) will end up null if no one is
            # found in the old file using the matching criteria above
            # this is important to remember for the overwriting logic below
        else: # we can just skip all the above and use subcriber numbers if the client sends good (non-PHI) ones
            if csvlog is True:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Person Code_x',
                                                        'Person Code_y']
                                                        ]
            else:
                dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                        ['Subscriber Number',
                                                        'Relationship',
                                                        'Date of Birth',
                                                        'Person Code_y',
                                                        indexcol,]
                                                        ]

        # Newly added dependents will have null values (I saw NaN initially),
        # need to fill in with new unique values
        # Taking max for the family, adding 1 to that, and adding cumulative counts for nulls to that
        dependents_codes.loc[dependents_codes['Person Code_y'].notnull(),
                             'Person Code'] = dependents_codes[dependents_codes['Person Code_y'].notnull()]['Person Code_y'].astype(int)
        max_codes = dependents_codes.groupby(['Subscriber Number'])['Person Code'].max()
        max_codes.name = 'Max Person Code'
        max_codes[max_codes.isnull()] = 1
        if csvlog is True:
            dependents_codes = dependents_codes.merge(max_codes, how='left', on=('Subscriber Number'))
        else:
            dependents_codes = dependents_codes.merge(max_codes, how='left', on=('Subscriber Number')).set_index(indexcol)
        dependents_codes.loc[dependents_codes['Person Code'].isnull(), 'Cum Counts'] = dependents_codes[dependents_codes['Person Code'].isnull()].sort_values(['Date of Birth']).groupby('Subscriber Number').cumcount(ascending=False)
        dependents_codes.loc[dependents_codes['Person Code'].isnull(), 'Person Code'] = dependents_codes['Cum Counts'] + dependents_codes['Max Person Code'] + 1
        dependents_codes['Person Code'] = dependents_codes['Person Code'].astype(str).apply(lambda x: x.replace('.0','')).str.pad(2, 'left', '0')
        if generate_id is True:
            dependents_codes['Cardholder Number'] = dependents_codes['Generated Subscriber ID'] + dependents_codes['Person Code']
        else:
            dependents_codes['Cardholder Number'] = dependents_codes['Subscriber Number'] + dependents_codes['Person Code']
        
        if csvlog is True: # if it's a log we have to merge back in cus indexes won't match
            # A little repititious but we're cleaning up before the merge to keep it simple...
            for col in df_members_merged.columns:
                if col.endswith('_y'):
                    df_members_merged[col[:-2]] = df_members_merged[col].fillna(df_members_merged[col[:-2] + '_x'])
                    df_members_merged.drop(columns=[col, col[:-2] + '_x'], inplace=True)
            # ... merging in the new dependent codes...
            df_members_merged.merge(dependents_codes,
                                    how='left',
                                    on='merge_id'
                                    )
            # ... and we're cleaning up again for the new person code/cardholder number cols this time
            for col in df_members_merged.columns:
                if col.endswith('_y'):
                    df_members_merged[col[:-2]] = df_members_merged[col].fillna(df_members_merged[col[:-2] + '_x'])
                    df_members_merged.drop(columns=[col, col[:-2] + '_x'], inplace=True)
                    
            # I realized this would act as an easy spot to add a print flag, so here's that :)
            df_members_merged['Print Card'] = 'N'
            print_me = df_members_merged.loc[~df_members_merged['Cardholder Number'].isin(df_members_before['Cardholder Number']), :].index
            df_members_merged.loc[print_me, 'Print Card'] = 'Y'
            
            return df_members_merged
        else:
            # if we're creating EHO standard file,
            # then indexes will match so we can just use those instead of a messy/slow merge process
            df_members_now.loc[df_members_now['Relationship'] == '19',
                            ['Person Code', 'Cardholder Number']
                            ] = dependents_codes[['Person Code', 'Cardholder Number']]
            
            # I realized this would act as an easy spot to add a print flag, so here's that :)
            # this relies on us creating the same-day print flag via log file boolean above
            try:
                df_members_now['Print Card'] = df_members_merged['Print Card']
            except KeyError:
                pass
            
            return df_members_now

    def eho_standard(self,
                     df_members,
                     group_number,
                     id_is_ssn,
                     address_use_flag = 'P',
                     max_length_dict = {
                        'Group Number':8,
                        'Cardholder Number':11,
                        'Date of Birth':8,  
                        'Last Name':15,     
                        'First Name':12,    
                        'Middle Initial':1,     
                        'Patient Zip Code':5,   
                        'Gender':1,     
                        'Relationship':1,   
                        'Status':1,     
                        'Effective Date':6,     
                        'Expiration Date':6,    
                        'Special ID':15,    
                        'Alternate Insurance':1,    
                        'Smoke Count':1,    
                        'Location':9,   
                        'Print Card':1,     
                        'HICN':11,  
                        'Language':1,   
                        'Federal Employee':1,   
                        'Benefit Code':3,   
                        'Required NABP':7,  
                        'Required DEA':10,  
                        'Days Supply':4,    
                        'SSN':9,   
                        'Catastrophic Coverage':1,  
                        'Telephonic Code':2,    
                        'Restricted Flag':1,    
                        'Ignore Inactive WC':1,     
                        'Ignore WC ED':1,   
                        'Deceased':1 ,  
                        'Invoice Class':24,     
                        'Diagnosis':30,     
                        'Allow Compound':1,     
                        'Facility Type':1,  
                        'Cardholder SSN':9,     
                        'Address Use Flag':1,   
                        'Address Line 1':30,    
                        'Address Line 2':30,   
                        'Address Line 3':30,   
                        'City':15,  
                        'State':2,  
                        'Zip Code':10,  
                        'Phone Number':12,  
                        'Alt Address Line 1':30,    
                        'Alt Address Line 2':30,    
                        'Alt Address Line 3':30,    
                        'Alt City':15,  
                        'Alt State':2,  
                        'Alt Zip Code':10,  
                        'Alt Phone Number':12,  
                        'Email Address':50,     
                    }
                    ):
        '''This returns an EHO-standard df from the df passed into df_members parameter
        The EHO standard shouldn't be used as input in any other method...
        It's truncated and has extra/duplicate cols in it.
        So it's great output but not preferred input for a faithful reproduction of 834'''
        
        df_members_eho = pd.DataFrame(columns=list(max_length_dict.keys()), dtype=str)
        for col in [col for col in df_members_eho if col in df_members.columns]:
            df_members_eho[col] = df_members[col]
        if id_is_ssn is True:
            df_members_eho['Cardholder SSN'] = df_members['Subscriber Number']
        df_members_eho['Group Number'] = group_number
        df_members_eho['Date of Birth'] = df_members_eho['Date of Birth'].dt.strftime('%Y%m%d')
        df_members_eho.loc[df_members_eho['Relationship'] == '18', 'Relationship'] = '1'
        df_members_eho.loc[df_members_eho['Relationship'] == '01', 'Relationship'] = '2'
        df_members_eho.loc[df_members_eho['Relationship'] == '19', 'Relationship'] = '3'
        df_members_eho['Benefit Code'] = df_members_eho['Status']
        df_members_eho.loc[df_members_eho['Benefit Code'] == 'C', 'Benefit Code'] = 'COB'
        df_members_eho.loc[~df_members_eho['Status'].isin(['A', 'I']), 'Status'] = 'A'
        df_members_eho['Effective Date'] = df_members_eho['Effective Date'].str[2:]
        df_members_eho['Expiration Date'] = df_members_eho['Expiration Date'].str[2:]
        df_members_eho['Address Use Flag'] = address_use_flag
        #df_members_eho['Address Line 3'] = df_members_eho['City'] + ', ' + df_members_eho['State'] + ' ' + df_members_eho['Patient Zip Code']
        df_members_eho['Zip Code'] = df_members_eho['Patient Zip Code']
        df_members_eho['Phone Number'] = df_members_eho['Phone Number'].str[0:3] + '-' + df_members_eho['Phone Number'].str[3:6] + '-' + df_members_eho['Phone Number'].str[6:]
        df_members_eho.loc[df_members_eho['Phone Number'] == '--', 'Phone Number'] = ''
        for col, strip_index in max_length_dict.items():
            df_members_eho[col] = df_members_eho[col].str[:strip_index]
        
        return df_members_eho
        
    
    def write_csv(self, write_path, group_abbr, id_is_ssn=True,
                  how='plain', read_csvpath=None, eho_standard=False,
                  group_number=None, csvlog=True):
        '''takes write_path as input, writes csv to this location.
        takes read_csvpath as optional input, default is None but it should be a path string.
        read_csvpath is necessary input when how = 'bycsv'.
        how parameter determines what kind of csv is written:
        how='plain' is a no person codes/Cardholder Numbers df with 834 segment names
        how='byrank' is a person-code-df only considering the current day's 834
        how='bycsv' is a person-code-df considering historical csv and current day's 834
        eho_standard is just for EHO's benefit:
        group_number is a constant identifier passed into eho_standard()
        DO NOT PASS EHO_STANDARD FILES AS INPUT ABOVE,
        THEIR FORMAT IS REPETITIVE COMPARED TO 834 AND MAX LENGTHS CAN CAUSE DATA LOSS
        It's a bit slow but I plan to run the whole thing twice for jobs'''
        
        if how=='plain':
            df_members = self.get_member_df(rename=False)
        elif how=='byrank':
            df_members = self.get_personcodes_byrank(group_abbr)
        elif how=='bycsv':
            if read_csvpath is None:
                raise Exception("The read_csvpath param must be defined to use how='bycsv'")
            df_members = self.get_personcodes_bycsv(read_csvpath, group_abbr, csvlog)
        else:
            raise Exception("The how param must be one of 'plain', 'byrank', or 'bycsv'")
            return None
        
        if eho_standard == True:
            df_members = self.eho_standard(df_members, group_number, id_is_ssn)
        
        df_members.to_csv(write_path, index=False)
        return print('CSV written to path: ' + write_path)
    
    
