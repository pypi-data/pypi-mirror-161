import pandas as pd
import random
import datetime

class process_file():
    def __init__(self,
                 process_dict,
                 rename_dict,
                 format_dict,
                 group_dict
                 ):
        '''path is a filepath,
        rename_dict is a dict constructed to map incoming file col names (keys) to our standard col names (vals),
        group_dict is a dict constructed to map incomping file group numbers (keys) to our group numbers (values),
        filetype is the file extension without a "." as a string (depending on ext, you may need more args to the method)
        '''
        self.process_dict = process_dict
        self.rename_dict = rename_dict
        self.format_dict = format_dict
        self.group_dict = group_dict
        
        
    def process_834(self):
        
        # read string
        with open(self.path) as f:
            wholefile = f.read().replace('\n', '')

        # separate segments, this may take more work as we develop more needs
        # or as we see more delimiters...
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
        
        # get only segments for the members, ignoring other file info...
        # could also need more work as more 834 files come in
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
        
        # convert to df
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
        
        if self.rename_dict:
            df_members = self.rename_cols(df_members)
        
        if self.format_dict:
            df_members = self.format_values(df_members)
            
        if self.group_dict:
            df_members = self.format_groups(df_members)

        if self.process_dict.get('term_by_date') is True:
            df_members = self.term_by_date(df_members)
        
        return df_members
    
    
    def process_txt(self):
        '''Takes self,
        utilizing self.process_dict["path"] and ["delim"],
        attempts to return a well-standardized pandas df of members
        '''
        
        df_members = pd.read_csv(self.process_dict['path'],
                                 sep=self.process_dict['delim'],
                                 dtype=str)
        
        if self.rename_dict:
            df_members = self.rename_cols(df_members)
        
        if self.format_dict:
            df_members = self.format_values(df_members)

        if self.group_dict:
            df_members = self.format_groups(df_members)

        if self.process_dict.get('term_by_date') is True:
            df_members = self.term_by_date(df_members)

        return df_members


    def term_by_date(self, df_members):
        '''Takes a df of members,
        and attempts to filter out all inactive members
        using cols 'Effective Date' and 'Expiration Date',
        returns pandas df of members
        '''
        
        remove_idx = df_members[datetime.datetime.today() > df_members['Expiration Date']].index
        df_members.drop(remove_idx, axis=0, inplace=True)
        remove_idx = df_members[datetime.datetime.today() < df_members['Effective Date']].index
        df_members.drop(remove_idx, axis=0, inplace=True)
        
        return df_members


    def rename_cols(self, df_members, print_all=True):
        '''takes self and a pandas dataframe of members,
        drops cols not in self.rename_dict, renames the remaining cols,
        optionally adds a col for printing all cards (default True),
        sets new col 'File Order Key' to match df_members.index,
        returns df_members
        '''
        
        # key is external col name, value is our col name
        df_members.drop([col for col in df_members.columns if col not in self.rename_dict.keys()],
                axis=1, inplace=True)
        df_members.rename(columns=self.rename_dict, inplace=True)
        if print_all is True:
            df_members['Print Card'] = 'Y'
        df_members['File Order Key'] = df_members.index
        try:
            df_members['Original Cardholder Number'] = df_members['Cardholder Number']
        except KeyError as e:
            print('Cardnum Error:', e)
            print('Acailable cols:', df_members.columns)
            pass
        
        return df_members
        
    
    def format_values(self, df_members):
        '''takes self and a pandas dataframe of members,
        performs various operations on the row values of the df,
        operations performed based on col names in self.rename_dict
        and row values specified within self.format_dict,
        returns reformatted pandas df of the members
        '''
        
        try:
            df_members['Date of Birth'] = pd.to_datetime(df_members['Date of Birth'],
                                                         format=self.format_dict['Date of Birth'])
        except KeyError as e:
            print('DOB Error:', e)
            print('Acailable cols:', df_members.columns)
            pass
        
        for col in ['Expiration Date', 'Effective Date']:
            try:
                df_members[col] = pd.to_datetime(df_members[col],
                                                 errors='coerce',
                                                 format=self.format_dict[col])
            except KeyError as e:
                print('Effective/Expiration Error:', e)
                print('Acailable cols:', df_members.columns)
                continue
            
        try:
            df_members['Subscriber Indicator'] = ''
            df_members.loc[df_members['Relationship'].isin(self.format_dict['Dependent']),
                           ['Subscriber Indicator', 'Relationship']] = ['N', '19']
            df_members.loc[df_members['Relationship'].isin(self.format_dict['Spouse']),
                           ['Subscriber Indicator', 'Relationship']] = ['N', '01']
            df_members.loc[df_members['Relationship'].isin(self.format_dict['Subscriber']),
                           ['Subscriber Indicator', 'Relationship']] = ['Y', '18']
        except KeyError as e:
            print('Relationship Error:', e)
            print('Acailable cols:', df_members.columns)
            pass
        
        return df_members
    
    
    def format_groups(self, df_members):
        '''takes self and pandas dataframe of members,
        attempts to reformat group rows as specified in self.groups_dict,
        changes external group numbers to our group numbers
        and drops unspecified groups,
        returns reformatted pandas df of the members
        '''
        
        if self.group_dict.get('GENERATE') is not None:
            df_members['Group Number'] = str(self.group_dict['GENERATE'][0])
            df_members['Original Group Number'] = df_members['Group Number']
        else:
            try:
                # key is external group id, value is a list of [internal group id, group abbreviation]
                df_members['Original Group Number'] = df_members['Group Number']
                for outside_id, internal_id in self.group_dict.items():
                    df_members.loc[df_members['Group Number'] == outside_id, 'Group Abbreviation'] = internal_id[1]
                    df_members.loc[df_members['Group Number'] == outside_id, 'Group Number'] = internal_id[0]
                remove_idx = df_members[~df_members['Group Number'].isin([groupnum for groupnum, group_abbr in self.group_dict.values()])].index
                df_members.drop(remove_idx, axis=0, inplace=True)
            except Exception as e:
                print('Group Numbers Error:', e)
                print('If Key Error... Available cols:', df_members.columns)
                pass
        
        return df_members
    
    
    def filetype_pointer(self):
        '''Takes self,
        exmatches self.process_dict["filetype"] for a string matching file extension,
        points to the proper processing method,
        attempts to return a pandas df of the members
        '''
        
        if self.process_dict['filetype'].lower() == 'txt':
            df_members = self.process_txt()
            
        elif self.process_dict['filetype'].lower() == '834':
            df_members = self.process_834()
            
        return df_members
    
    
class no_personcodes(process_file):
    
    
    def get_cardnums_bycardnum(self, generate_id=True):
        '''Assigns randomly generated IDs without person codes using the external/original cardnumbers, returning df with new IDs.
        generate_id=True sets up the generation.
        False results in using the Subcriber Number as first 9 digits of ID (often subscriber number is subscriber SSN),
        returns pandas df with new Cardholder Number and Person Code cols
        '''
        
        df_members = self.filetype_pointer()

        if generate_id is True:
            df_members = self.generate_cardnum(df_members)
        else:
            # When they send us unique subscriber numbers that do not contain PHI
            df_members['Cardholder Number'] = df_members['Subscriber Number']
    
        return df_members
    
    
    def generate_cardnum(self, df_members, randmax=9):
        '''method for obtaining a randomly generated ID number from an external cardholder number,
        takes pandas df with a external cardholder number as input,
        takes max length of random ID number with default = 9,
        returns pandas df with replacement IDs as output
        '''
        
        # When they send us subscriber numbers containing PHI, like a SSN, then...
        # Here we need to replace the subscriber numbers with our own member IDs
        replacement_memberid = {}
        for card_numb in df_members['Original Cardholder Number'].unique():
            if type(card_numb) == str:
                group_abbr = df_members.loc[df_members['Original Cardholder Number'] == card_numb, 'Group Abbreviation'].unique()[0]
            else:
                group_abbr = 'NA'
            replacement_memberid[card_numb] = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
        # Check for non-unique strings
        while len(pd.Series(list(replacement_memberid.values())).unique()) < len(df_members['Original Cardholder Number'].unique()):
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
                    if type(dupe) == str:
                        group_abbr = df_members.loc[df_members['Original Cardholder Number'] == dupe, 'Group Abbreviation'].unique()[0]
                    else:
                        group_abbr = 'NA'
                    replacement_memberid[dupe] = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
        else:
            for card_numb, memberid in replacement_memberid.items():
                df_members.loc[df_members['Original Cardholder Number'] == card_numb, 'Cardholder Number'] = memberid
        
        return df_members
    
    
    def get_cardnums_bycsv(self, csvpath, csvlog=True, randmax=9):
        '''Takes the members df for today,
        takes the previously created CSV path as an argument and makes another df,
        and merges the two with members df for today on the left when csvlog=False,
        or merges the two with outer join when csvlog=True.
        When csvlog=True, and the path is to an old log file, then...
        attempts to keep all old values for member IDs but adds new member IDs for new records.
        All the above necessitates making a new log file first, then using that to 
        ensure the cardholer numbers are assigned correctly 
        (outer vs left joining/overwriting behavior makes this a little tricky).
        '''
        
        df_members_now = self.get_cardnums_bycardnum()
        
        df_members_before = pd.read_csv(csvpath, dtype=str)
        df_members_before['Date of Birth'] = pd.to_datetime(df_members_before['Date of Birth'], format='%Y-%m-%d')
        
        # Need to drop the audit column '_merge' (we'll remake it)
        # Also need to create a merge ID as a coalesce of og cardnum, janky-ID
        for df in [df_members_now, df_members_before]:
            # drop _merge audit col
            for col in ['_merge', 'merge_id']:
                try:
                    del df[col]
                except KeyError:
                    continue
            # create an ID col for merges, first prep/clean...
            merge_headers = ['Original Cardholder Number', 'Subscriber Number', 'Group Number', 'Relationship', 'Date of Birth', 'Last Name', 'First Name']
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
            # reassigning names this way to guarantee we not mess with the cols themselves during cleaning            
            df['merge_id'] = df[merge_ids[0]].combine_first(df[merge_ids[1]].str.cat(df[merge_ids[2:]]))
            # null and duplicate issues...
            for i in range(3,7):
                df.loc[(df['merge_id'].isnull()) |
                       (df['merge_id'] == 'NAN') |
                       (df['merge_id'].duplicated(keep=False)),
                       'merge_id'] = df[merge_ids[1]].str.cat(df[merge_ids[i:]])
            # drop the intermediary cols
            for col in merge_ids:
                try:
                    del df[col]
                except KeyError:
                    continue

        # We need to check for duplicates again, this time by way of comparing to the past
        # the worry here is some 1 in a billion chance that a newly generated ID is equal to some old inactive one :P
            # New subscribers as determined by group's codings...
            new_families = df_members_now.loc[~df_members_now['Original Cardholder Number'].isin(df_members_before['Original Cardholder Number']),
                                              ['Cardholder Number']]
            # ... who also have generated ID that matches one assigned to someone else before...
            dupe_ids = new_families.loc[new_families['Cardholder Number'].isin(df_members_before['Cardholder Number']), :]
            dupe_ids_index = dupe_ids.index
            while len(dupe_ids) > 0:
            # ... get a new ID ...
                for card_numb in dupe_ids['Cardholder Number'].unique():
                    group_abbr = df_members_now.loc[df_members_now['Cardholder Number'] == card_numb, 'Group Abbreviation'].unique()[0]
                    new_id = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
                    # this re-checks that the ID isn't in the new batch
                    while pd.Series(new_id).isin(pd.concat((df_members_now['Cardholder Number'], df_members_before['Cardholder Number']))):
                        new_id = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
                    new_families.loc[new_families['Cardholder Number'] == card_numb, 'Cardholder Number'] = new_id
                    dupe_ids = new_families.loc[new_families['Cardholder Number'].isin(df_members_before['Cardholder Number']), :]
            else:
                for idx in dupe_ids_index:
                    df_members_now.loc[idx, ['Cardholder Number']] = new_families.loc[idx, ['Cardholder Number']]

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
            print('Check for Duplicated Merge Keys:')
            dupe_merge = df_members_merged[df_members_merged['merge_id'].duplicated(keep=False)][['File Order Key_x','Group Number_x','merge_id']]
            print(dupe_merge)
            if len(dupe_merge) > 0:
                print('Dropping Above Members. Please contact input provider!')
                df_members_merged.drop(dupe_merge.index, axis=0, inplace=True)

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
        
        # I want to preserve the original/external group numbers but fill with new generated numbers for new members
        for col in ['Original Group Number', 'Original Cardholder Number', 'Cardholder Number']:
            try:
                df_members_merged[col] = df_members_merged[col + '_y'].fillna(df_members_merged[col + '_x'])
                df_members_now[col] = df_members_merged[col]
            except KeyError:
                pass
            try:
                df_members_merged.drop(columns=[col + '_y'], inplace=True)
                df_members_merged.drop(columns=[col + '_x'], inplace=True)
            except Exception:
                pass

                
        if csvlog is True:
            # cleaning the log file col names
            for col in df_members_merged.columns:
                if col.endswith('_x'):
                    df_members_merged[col[:-2]] = df_members_merged[col].fillna(df_members_merged[col[:-2] + '_y'])
                    df_members_merged.drop(columns=[col, col[:-2] + '_y'], inplace=True)
                elif col 
                
            # I realized this would act as an easy spot to add a print flag, so here's that :)
            df_members_merged['Print Card'] = 'N'
            print_me = df_members_merged.loc[~df_members_merged['Cardholder Number'].isin(df_members_before['Cardholder Number']), :].index
            df_members_merged.loc[print_me, 'Print Card'] = 'Y'
            
            return df_members_merged
            
        else:
            # csvlog=False for now meant to be a generator for EHO standard files
            # I realized this would act as an easy spot to add a print flag, so here's that :)
            # this relies on us creating the same-day print flag via log file boolean above
            try:
                df_members_now['Print Card'] = df_members_merged['Print Card']
            except KeyError:
                pass
            
            # return the current df when csvlog = False (left joined on current and dependent codes indexed back in)
            return df_members_now

    
class add_personcodes(process_file):
    
    
    def generate_id(self, df_members, randmax=7):
        '''method for obtaining a randomly generated ID number from a subscriber number,
        takes pandas df with a subscriber number as input,
        takes max length of random ID number with default = 7,
        returns pandas df with replacement IDs as output
        '''
        
        # When they send us subscriber numbers containing PHI, like a SSN, then...
        # Here we need to replace the subscriber numbers with our own member IDs
        replacement_memberid = {}
        for sub_numb in df_members['Subscriber Number'].unique():
            if type(sub_numb) == str:
                group_abbr = df_members.loc[df_members['Subscriber Number'] == sub_numb, 'Group Abbreviation'].unique()[0]
            else:
                group_abbr = 'NA'
            replacement_memberid[sub_numb] = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
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
                    if type(dupe) == str:
                        group_abbr = df_members.loc[df_members['Subscriber Number'] == dupe, 'Group Abbreviation'].unique()[0]
                    else:
                        group_abbr = 'NA'
                    replacement_memberid[dupe] = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
        else:
            for sub_numb, memberid in replacement_memberid.items():
                df_members.loc[df_members['Subscriber Number'] == sub_numb, 'Generated Subscriber ID'] = memberid
            
            df_members['Cardholder Number'] = df_members['Generated Subscriber ID'] + df_members['Person Code']
        
        return df_members


    def get_personcodes_bycardnum(self, generate_id=True, dep_adj=0):
        '''Assigns person codes using existing cardholder numbers in sent data (useful when someone already sending IDs with person codes),
        takes a boolean generate_id as input where True results in a random str by subscriber number for first 9 indicies of ID,
        False results in using the Subcriber Number as first 9 digits of ID (often subscriber number is subscriber SSN),
        returns pandas df with new Cardholder Number and Person Code cols
        '''
        
        df_members = self.filetype_pointer()
        df_members.loc[(df_members['Subscriber Indicator'] == 'Y') &
                       (df_members['Relationship'] == '18'),
                       'Person Code'] = '00'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '01'),
                       'Person Code'] = '01'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '19'),
                       'Person Code'] = df_members['Cardholder Number'].str[-2:].astype(int) + dep_adj
        df_members['Person Code'] = df_members['Person Code'].astype(str).apply(lambda x: x.replace('.0','')).str.pad(2, 'left', '0')
        
        if generate_id is True:
            df_members = self.generate_id(df_members)
        else:
            # When they send us unique subscriber numbers that do not contain PHI
            df_members['Cardholder Number'] = df_members['Subscriber Number'] + df_members['Person Code']
    
        return df_members
    
    
    def get_personcodes_byrank(self, generate_id=True):
        '''Takes the members df and assigns person codes, returns df.
        Follows this logic:
        if sub_ind = 'Y' and rel_code = '18', person code = '00',
        if sub_ind = 'N' and rel_code = '01', person code = '01',
        if sub_ind = 'N' and rel_code = '19', person code = '02':'xx' by desc birthdate.
        This should be used explicitly the first time ever processing an 834 without a CSV log.
        '''
        
        df_members = self.filetype_pointer()
        df_members.loc[(df_members['Subscriber Indicator'] == 'Y') &
                       (df_members['Relationship'] == '18'),
                       'Person Code'] = '00'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '01'),
                       'Person Code'] = '01'
        df_members.loc[(df_members['Subscriber Indicator'] == 'N') &
                       (df_members['Relationship'] == '19'),
                       'Person Code'] = '02'
        # Moving the following line to upstream, but haven't handled 834 yet. still a sep class.
        # df_members['Date of Birth'] = pd.to_datetime(df_members['Date of Birth'], format='%Y%m%d')
        grouping = df_members[df_members['Person Code'] == '02'].sort_values(['Date of Birth']).groupby(['Subscriber Number',
                                                                                                         'Relationship']).cumcount(ascending=False)
        df_members.loc[df_members['Person Code'] == '02', 'Person Code'] = df_members['Person Code'].astype(int) + grouping
        df_members['Person Code'] = df_members['Person Code'].astype(str).apply(lambda x: x.replace('.0','')).str.pad(2, 'left', '0')
        
        if generate_id is True:
            df_members = self.generate_id(df_members)
        else:
            # When they send us unique subscriber numbers that do not contain PHI
            df_members['Cardholder Number'] = df_members['Subscriber Number'] + df_members['Person Code']

        return df_members
    
    
    def get_personcodes_bycsv(self, csvpath, csvlog=True, generate_id=True, how='byrank', randmax=7):
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
        for details/examples of dual-running where first csvlog=True and then csvlog=False.
        '''
        
        if how=='bycardnum':
            df_members_now = self.get_personcodes_bycardnum()
            
        elif how=='byrank':
            df_members_now = self.get_personcodes_byrank()
        
        df_members_before = pd.read_csv(csvpath, dtype=str)
        df_members_before['Date of Birth'] = pd.to_datetime(df_members_before['Date of Birth'],
                                                            format='%Y-%m-%d', errors='coerce')
        
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
            if how=='bycardnum':
                merge_headers = ['Original Cardholder Number', 'Subscriber Number', 'Group Number', 'Relationship', 'Date of Birth', 'Last Name', 'First Name']
            elif how=='byrank':
                merge_headers = ['SSN', 'Subscriber Number', 'Relationship', 'Group Number', 'Date of Birth', 'Last Name', 'First Name']
            else:
                raise Exception("The how arg in this method must be one of 'bycardnum' or 'byrank'")

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
            # null and duplicate issues...
            for i in range(3,7):
                df.loc[(df['merge_id'].isnull()) |
                       (df['merge_id'] == 'NAN') |
                       (df['merge_id'].duplicated(keep=False)),
                       'merge_id'] = df[merge_ids[1]].str.cat(df[merge_ids[i:]])
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
                    group_abbr = df_members_now.loc[df_members_now['Subscriber Number'] == subscriber_number, 'Group Abbreviation'].unique()[0]
                    new_id = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
                    # this re-checks that the ID isn't in the new batch
                    while pd.Series(new_id).isin(pd.concat((df_members_now['Generated Subscriber ID'], df_members_before['Generated Subscriber ID']))):
                        new_id = group_abbr + str(random.randint(0, int('9'*randmax))).zfill(randmax)
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
            print('Check for Duplicated Merge Keys:')
            dupe_merge = df_members_merged[df_members_merged['merge_id'].duplicated(keep=False)][['File Order Key_x','Group Number_x','merge_id']]
            print(dupe_merge)
            if len(dupe_merge) > 0:
                print('Dropping Above Members. Please contact input provider!')
                df_members_merged.drop(dupe_merge.index, axis=0, inplace=True)

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
            try:
                df_members_merged.drop(columns=[col + '_y'], inplace=True)
                df_members_merged.drop(columns=[col + '_x'], inplace=True)
            except Exception:
                pass
        
        # I want to preserve the original/external group numbers
        for col in ['Original Group Number', 'Original Cardholder Number']:
            try:
                df_members_merged[col] = df_members_merged[col + '_y'].fillna(df_members_merged[col + '_x'])
                df_members_now[col] = df_members_merged[col]
            except KeyError:
                pass
            try:
                df_members_merged.drop(columns=[col + '_y'], inplace=True)
                df_members_merged.drop(columns=[col + '_x'], inplace=True)
            except Exception:
                pass

        if how=='bycardnum':
            if generate_id is True:
                # If our own IDs are getting generated, then we need to keep the old ones...
                for col in ['Generated Subscriber ID', 'Cardholder Number']:
                    try:
                        df_members_merged[col] = df_members_merged[col + '_y'].fillna(df_members_merged[col + '_x'])
                        df_members_now[col] = df_members_merged[col]
                    except KeyError:
                        pass
                
            if csvlog is True:
                # cleaning the log file col names
                for col in df_members_merged.columns:
                    if col.endswith('_x'):
                        df_members_merged[col[:-2]] = df_members_merged[col].fillna(df_members_merged[col[:-2] + '_y'])
                        df_members_merged.drop(columns=[col, col[:-2] + '_y'], inplace=True)
                
                # I realized this would act as an easy spot to add a print flag, so here's that :)
                df_members_merged['Print Card'] = 'N'
                print_me = df_members_merged.loc[~df_members_merged['Cardholder Number'].isin(df_members_before['Cardholder Number']), :].index
                df_members_merged.loc[print_me, 'Print Card'] = 'Y'
                
                return df_members_merged
            
            else:
                # csvlog=False for now meant to be a generator for EHO standard files
                # I realized this would act as an easy spot to add a print flag, so here's that :)
                # this relies on us creating the same-day print flag via log file boolean above
                try:
                    df_members_now['Print Card'] = df_members_merged['Print Card']
                except KeyError:
                    pass
                
                # return the current df when csvlog = False (left joined on current and dependent codes indexed back in)
                return df_members_now

        elif how=='byrank':
            
            if generate_id is True:
                # If our own IDs are getting generated, then we need to keep the old ones...
                df_members_merged['Generated Subscriber ID'] = df_members_merged['Generated Subscriber ID_y'].fillna(df_members_merged['Generated Subscriber ID_x'])
                df_members_now['Generated Subscriber ID'] = df_members_merged['Generated Subscriber ID']
                df_members_merged['Cardholder Number'] = df_members_merged['Cardholder Number_y'].fillna(df_members_merged['Cardholder Number_x'])
                df_members_now['Cardholder Number'] = df_members_merged['Cardholder Number']
                
                # Grab old person codes as well...
                if csvlog is True:
                    dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                            ['merge_id',
                                                            'Subscriber Number',
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
                                                            ['merge_id',
                                                            'Subscriber Number',
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
                                                            ['merge_id',
                                                            'Subscriber Number',
                                                            'Relationship',
                                                            'Date of Birth',
                                                            'Person Code_x',
                                                            'Person Code_y']
                                                            ]
                else:
                    dependents_codes = df_members_merged.loc[df_members_merged['Relationship'] == '19',
                                                            ['merge_id',
                                                            'Subscriber Number',
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
                
                for col in ['Original Group Number', 'Original Cardholder Number', 'Cardholder Number',
                            'Generated Subscriber ID', "Person Code", 'Subscriber Number']:
                    try:
                        df_members_merged[col] = df_members_merged[col + '_y'].fillna(df_members_merged[col + '_x'])
                        df_members_now[col] = df_members_merged[col]
                    except KeyError:
                        pass
                    try:
                        df_members_merged.drop(columns=[col + '_y', col + '_x'], inplace=True)
                    except Exception:
                        pass
                
                # A little repititious but we're cleaning up before the merge to keep it simple...
                for col in df_members_merged.columns:
                    if col.endswith('_x'):
                        df_members_merged[col[:-2]] = df_members_merged[col].fillna(df_members_merged[col[:-2] + '_y'])
                        df_members_merged.drop(columns=[col, col[:-2] + '_y'], inplace=True)
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
                
                # return the merged df when csvlog = true (outer joined and dependent codes merged back in)
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
                
                # return the current df when csvlog = False (left joined on current and dependent codes indexed back in)
                return df_members_now


class eligibility_objects(add_personcodes, no_personcodes):
    
    def eho_standard(self,
                     df_members,
                     id_is_ssn=True,
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
        So it's great output but not preferred input for a faithful reproduction of 834
        '''
        
        df_members_eho = pd.DataFrame(columns=list(max_length_dict.keys()), dtype=str)
        for col in [col for col in df_members_eho if col in df_members.columns]:
            df_members_eho[col] = df_members[col]
        if id_is_ssn is True:
            df_members_eho['Cardholder SSN'] = df_members['Subscriber Number']
        df_members_eho['Date of Birth'] = df_members_eho['Date of Birth'].dt.strftime('%Y%m%d')
        df_members_eho.loc[df_members_eho['Relationship'] == '18', 'Relationship'] = '1'
        df_members_eho.loc[df_members_eho['Relationship'] == '01', 'Relationship'] = '2'
        df_members_eho.loc[df_members_eho['Relationship'] == '19', 'Relationship'] = '3'
        df_members_eho['Benefit Code'] = df_members_eho['Status']
        df_members_eho.loc[df_members_eho['Benefit Code'] == 'C', 'Benefit Code'] = 'COB'
        df_members_eho.loc[~df_members_eho['Status'].isin(['A', 'I']), 'Status'] = 'A'
        if self.process_dict['filetype'] == '834':
            df_members_eho['Effective Date'] = df_members_eho['Effective Date'].str[2:]
            df_members_eho['Expiration Date'] = df_members_eho['Expiration Date'].str[2:]
        else:
            df_members_eho['Effective Date'] = df_members_eho['Effective Date'].dt.strftime('%y%m%d')
            df_members_eho['Expiration Date'] = df_members_eho['Expiration Date'].dt.strftime('%y%m%d')
        df_members_eho['Address Use Flag'] = address_use_flag
        #df_members_eho['Address Line 3'] = df_members_eho['City'] + ', ' + df_members_eho['State'] + ' ' + df_members_eho['Patient Zip Code']
        df_members_eho['Zip Code'] = df_members_eho['Patient Zip Code']
        df_members_eho['Phone Number'] = df_members_eho['Phone Number'].str[0:3] + '-' + df_members_eho['Phone Number'].str[3:6] + '-' + df_members_eho['Phone Number'].str[6:]
        df_members_eho.loc[df_members_eho['Phone Number'] == '--', 'Phone Number'] = ''
        df_members_eho = df_members_eho.astype(str)
        for col, strip_index in max_length_dict.items():
            df_members_eho[col] = df_members_eho[col].replace('nan', '').str[:strip_index]
        
        return df_members_eho
        
    
    def write_csv(self):
        '''takes write_path as input, writes csv to this location.
        takes read_csvpath as optional input, default is None but it should be a path string.
        inputs passed in via self's format_dict and process_dicts.
        read_csvpath is necessary input when how = 'bycsv'.
        how parameter determines what kind of csv is written:
        how='plain' is a no person codes/Cardholder Numbers df
        how='byrank' is a person-code-df only considering the current day's file
        how='bycsv_rank' and 'bycsv_cardnum' is a person-code-df considering historical csv and current day's file
        eho_standard is just for EHO's benefit:
        DO NOT PASS EHO_STANDARD FILES AS INPUT ABOVE,
        THEIR FORMAT IS REPETITIVE COMPARED TO 834 AND MAX LENGTHS CAN CAUSE DATA LOSS
        It's a bit slow but I plan to run the whole thing twice for jobs
        '''
        
        if self.process_dict.get('how') is None:
            raise Exception("""The how param is not set; must be set as 'plain',
                            or for person code generators 'getpersoncodes_bycardnum', 'getpercondoes_byrank', 'getpersoncodes_bycsv_bycardnum', 'getpersoncodes_bycsv_byrank',
                            or for random generators based on external cardnums 'nopersoncodes', 'nopersoncodes_bycsv'""")
            return None
        if self.process_dict.get('generate_id') is None:
            print('generate_id not set, setting to True')
            self.process_dict['generate_id'] = True
        if self.process_dict.get('csvlog') is None:
            print('csvlog not set, setting to True')
            self.process_dict['csvlog'] = True
        
        if self.process_dict['how'] == 'plain':
            df_members = self.filetype_pointer()
            
        elif self.process_dict['how'] == 'getpersoncodes_bycardnum':
            if self.process_dict.get('dep_adj') is None:
                print('dep_adj not set, setting to 0')
                self.process_dict['dep_adj'] = 0
            df_members = self.get_personcodes_bycardnum(self.process_dict['generate_id'], self.process_dict['dep_adj'])
            
        elif self.process_dict['how'] == 'getpersoncodes_byrank':
            df_members = self.get_personcodes_byrank(self.process_dict['generate_id'])
            
        elif self.process_dict['how'].lower().startswith('bycsv_getpersoncodes'):
            if self.process_dict.get('read_csvpath') is None:
                raise Exception("The read_csvpath string must be defined to use how='bycsv_'")
                return None
            df_members = self.get_personcodes_bycsv(csvpath=self.process_dict['read_csvpath'], csvlog=self.process_dict['csvlog'], generate_id=self.process_dict['generate_id'], how=self.process_dict['how'][21:])
        
        elif self.process_dict['how'] == 'nopersoncodes_bycardnum':
            df_members = self.get_cardnums_bycardnum(self.process_dict['generate_id'])
        
        elif self.process_dict['how'].lower().startswith('bycsv_nopersoncodes'):
            if self.process_dict.get('read_csvpath') is None:
                raise Exception("The read_csvpath string must be defined to use how='bycsv_'")
                return None
            df_members = self.get_cardnums_bycsv(csvpath=self.process_dict['read_csvpath'], csvlog=self.process_dict['csvlog'])
        
        else:
            raise Exception("""The how param must be set as 'plain',
                            or for person code generators 'getpersoncodes_bycardnum', 'getpercondoes_byrank', 'bycsv_getpersoncodes_bycardnum', 'bycsv_getpersoncodes_byrank',
                            or for random generators based on external cardnums 'nopersoncodes_bycardnum', 'bycsv_nopersoncodes_bycardnum'""")
            return None
        
        if self.format_dict['eho_standard'] == True:
            if self.format_dict.get('id_is_ssn') is None:
                print('id_is_ssn not set, setting to True')
                self.format_dict['id_is_ssn'] = True
            if self.format_dict.get('address_use_flag') is None:
                print('address_use_flag not set, setting to P')
                self.format_dict['address_use_flag'] = 'P'
            df_members = self.eho_standard(df_members, id_is_ssn=self.format_dict['id_is_ssn'], address_use_flag=self.format_dict['address_use_flag'])
        
        df_members.to_csv(self.process_dict['write_path'], index=self.format_dict['index'], na_rep='')
        return print('CSV written to path: ' + self.process_dict['write_path'])
    
    
