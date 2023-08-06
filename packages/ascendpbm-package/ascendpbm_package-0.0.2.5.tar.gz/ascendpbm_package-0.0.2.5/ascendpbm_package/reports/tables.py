import pandas as pd
import numpy as np
from datetime import datetime
from abc import ABC
import traceback

def add_rebate_dollarcol(df_claims, df_formulary, claim_ndc, claim_days, form_ndc='ndc',
                         form_id='formulary_id', form_status='formulary_status',
                         rebate_flag='rebate_flag', specialty_flag='specialty',
                         mony='mony_code', brand='brand_name_code', trademark='TRDMK',
                         days_flag='Days Supply > 84', cutoff=84, positive = 'Y',
                         exclude = 'EXCLUDED', rebate_amnt_flag="Rebate Amount - FLAG",
                         rebate_amnt_brand='Rebate Amount - BRAND',
                         rebate_guar = pd.DataFrame({'Formulary':['REMEDYONE HIGHLY MANAGED FORMULARY',
                                                                  'REMEDYONE MANAGED FORMULARY',
                                                                  'REMEDYONE OPEN FORMULARY']*2,
                                                     'rebate_method':['FLAG']*3 + ['BRAND']*3,
                                                     '<= 84 Days':[117.86, 109.66, 107.04] + [175.38, 142.72, 141.55],
                                                     '> 84 Days':[494.26, 475.25, 432.57] + [479.68, 367.25, 334.27],
                                                     'Specialty':[1859.00, 1836.19, 1255.54] + [1996.43, 1940.79, 1327.07]
                                                     }
                                                    )
                         ):
    '''
    Parameters
    ----------
    df_claims : pandas dataframe
        Pandas dataframe of claims including cols for ndc and days supply.
        Assumes ndcs have been cleaned to match formulary ndc.
    df_formulary : pandas dataframe
        Pandas dataframe of formulary with cols of ndc, rebate flag, specialty flag, and formulary IDs.
        Assumes positive indications on any flag match the positive argument string below.
    claim_ndc : str
        Column name for the df_claims ndc col.
    claim_days : str
        Column name for the df_claims days supply col.
        Assumes column has been cleaned for .astype(int) conversion.
    form_ndc : str, optional
        Column name for the df_formulary ndc col. The default is 'ndc'.
    form_id : str, optional
        Column name for the df_formulary formulary indicator col.
        rebate_guar 'Formulary' unique values should match the unique values in this col.
        The default is 'formulary_id'.
    form_status : str, optional
        Column name for the df_formulary formulary status col (preferred, excluded, etc).
        The default is 'formulary_status'.
    rebate_flag : str, optional
        Column name for the df_formulary rebate col. The default is 'rebate_flag'.
    specialty_flag : str, optional
        Column name for the df_formulary specialty col. The default is 'specialty'.
    mony : str, optional
        Column name for the df_formulary MONY col. The default is 'mony_code'.
    brand : str, optional
        Column name for the df_formulary brand/generic col. The default is 'brand_name_code'. 
    exclude : str, optional
        Although a string, could be anything that matches a trademark indication in the brand col.
        The default is "TRDMK".
    days_flag : TYPE, optional
        Highly readable column name for a created days supply indicator col.
        The default is 'Days Supply > 84'.
    cutoff : int, optional
        Although an int, could be any numeric object comparable with > and <= to df_claims days supply col.
        The default is 84.
    positive : str, optional
        Although a string, could be anything that matches a positive indication in the form_id col.
        The default is "Y".
    exclude : str, optional
        Although a string, could be anything that matches an excluded indication in the form_status col.
        The default is "EXCLUDED".
    rebate_amnt_flag : str, optional
        Highly readable column name for a created rebate $ amount float col rounded to two decimals.
        The default is "Rebate Amount - FLAG".
    rebate_amnt_brand : str, optional
        Highly readable column name for a created rebate $ amount float col rounded to two decimals.
        The default is "Rebate Amount - BRAND".
    rebate_guar : pandas dataframe, optional
        A dataframe for organizing rebate levels and rates.
        that the first list elements map to unique formulary indications in the form_id col,
        and that the rebate dollar amounts are given as float values in ascending order following the first elements.
        The default is pd.DataFrame({'Formulary':['REMEDYONE HIGHLY MANAGED FORMULARY', 'REMEDYONE MANAGED FORMULARY',
                                                                      'REMEDYONE OPEN FORMULARY']*2,
                                     'Rebate Method':['FLAG']*3 + ['BRAND']*3,
                                     '<= 84 Days':[117.86, 109.66, 107.04] + [175.38, 142.72, 141.55],
                                     '> 84 Days':[494.26, 475.25, 432.57] + [479.68, 367.25, 334.27],
                                     'Specialty':[1859.00, 1836.19, 1255.54] + [1996.43, 1940.79, 1327.07]
                                     }
                                    )

    Returns
    -------
    dict
        {'claims': rebates, 'summary': summary}
        rebates (key: 'claims'): like the original claims df, but left joined on ndc col
        with formulary on the right and expanded horizontally with highly readable
        cols for indicators and rebate amounts.
        summary (key: 'summary'): a groupby object which breaks down the above indicator
        columns in its multiindex, and which gives sums of rebate amounts and claim counts
        for all subcategories so created.
    '''
    
    # Merging claims and formulary
    rebates = pd.merge(left=df_claims, right=df_formulary, how="left",
                       left_on=claim_ndc, right_on=form_ndc)
    
    # Creating highly readable indicator cols
    rebates.loc[rebates[rebate_flag] == positive, 'Rebatable - FLAG'] = 'Y'
    rebates.loc[rebates['Rebatable - FLAG'].isnull(), 'Rebatable - FLAG'] = 'N'
    rebates.loc[rebates[specialty_flag] == positive, 'Specialty'] = 'Y'
    rebates.loc[rebates['Specialty'].isnull(), 'Specialty'] = 'N'
    rebates.loc[rebates[claim_days].astype(int) > cutoff, days_flag] = 'Y'
    rebates.loc[rebates[claim_days].astype(int) <= cutoff, days_flag] = 'N'
    rebates['Formulary'] = rebates[form_id]
    form_id = 'Formulary'
    rebate_flag = 'Rebatable - FLAG'
    rebate_brand = 'Rebatable - BRAND'
    specialty_flag = 'Specialty'
    rebates[rebate_brand] = np.nan
    rebates[rebate_amnt_brand] = np.nan
    
    # Logic corresponding to Remedyone's flat rebate rates
    for idx, row in rebate_guar.iterrows():
        if row['rebate_method'] == 'FLAG': # For the flag method
            rebates.loc[(rebates[rebate_flag] == 'Y') & (rebates[specialty_flag] == 'N')
                        & (rebates[days_flag] == 'Y') & (rebates[form_id] == row[form_id]),
                        rebate_amnt_flag] = row['> 84 Days']
            rebates.loc[(rebates[rebate_flag] == 'Y') & (rebates[specialty_flag] == 'N')
                        & (rebates[days_flag] == 'N') & (rebates[form_id] == row[form_id]),
                        rebate_amnt_flag] = row['<= 84 Days']
            rebates.loc[(rebates[rebate_flag] == 'Y') & (rebates[specialty_flag] == 'Y')
                        & (rebates[form_id] == row[form_id]),
                        rebate_amnt_flag] = row[specialty_flag]
        else: # for the "brand" method. We'll assign an extra indicator here for clean presentation.
            rebates.loc[(rebates[mony].isin(['M', 'N'])) & (rebates[specialty_flag] == 'N')
                        & (rebates[days_flag] == 'Y') & (rebates[form_id] == row[form_id])
                        & (rebates[brand] == trademark) & (rebates[form_status] != exclude),
                        [rebate_amnt_brand, rebate_brand]] = [row['> 84 Days'], 'Y']
            rebates.loc[(rebates[mony].isin(['M', 'N'])) & (rebates[specialty_flag] == 'N')
                        & (rebates[days_flag] == 'N') & (rebates[form_id] == row[form_id])
                        & (rebates[brand] == trademark) & (rebates[form_status] != exclude),
                        [rebate_amnt_brand, rebate_brand]] = [row['<= 84 Days'], 'Y']
            rebates.loc[(rebates[mony].isin(['M', 'N'])) & (rebates[specialty_flag] == 'Y')
                        & (rebates[form_id] == row[form_id]) & (rebates[brand] == trademark)
                        & (rebates[form_status] != exclude),
                        [rebate_amnt_brand, rebate_brand]] = [row[specialty_flag], 'Y']
    
    # extra cleaning for brand, would make more sense to two-part the brand logic and move this up...
    rebates.loc[rebates[rebate_brand].isnull(), rebate_brand] = 'N'
    
    # clean null projections and deduct fees
    rebates.loc[rebates[rebate_amnt_flag].isnull(), rebate_amnt_flag] = 0.00
    rebates.loc[rebates[rebate_amnt_brand].isnull(), rebate_amnt_brand] = 0.00
    rebates[rebate_amnt_flag] = (0.95*rebates[rebate_amnt_flag]).round(2)
    rebates[rebate_amnt_brand] = (0.95*rebates[rebate_amnt_brand]).round(2)
    
    # Creating summary multiindex df with rebate amount sums and claim counts by above categories
    summary_flag = rebates.groupby([form_id,
                                    rebate_flag,
                                    days_flag,
                                    specialty_flag]).agg(['sum',
                                                          'count'])[rebate_amnt_flag]
    summary_flag.rename(columns={'sum':'Projected Rebate Amount',
                                 'count':'Claim Count'},
                        inplace=True)
    summary_brand = rebates.groupby([form_id,
                                     rebate_brand,
                                     days_flag,
                                     specialty_flag]).agg(['sum',
                                                           'count'])[rebate_amnt_brand]
    summary_brand.rename(columns={'sum':'Projected Rebate Amount',
                                  'count':'Claim Count'},
                         inplace=True)
    summary_all = rebates.groupby('Formulary')[[rebate_amnt_flag, rebate_amnt_brand]].sum()
    
    # Returning dict of both modified/expanded claims df by formulary and above summary object
    return {'claims': rebates,
            'summary_flag': summary_flag,
            'summary_brand': summary_brand,
            'summary_all': summary_all}

def add_ndc_hyphens(ndc11):
    #print(ndc11)
    ndc11 = str(ndc11)
    #assert len(ndc11) == 11, "you need 11 digits for this to work bro"
    labler = ndc11[0:5]
    product = ndc11[5:9]
    package = ndc11[9:]

    ndc = labler + '-' + product + '-' + package
    return ndc

# get ordinal ranks
def make_ordinal(n):
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix

# special way to calculate member months
def get_member_months(start, end, data, activecolname="Effective Date", termcolname='Expiration Date       '):
    dfm = data.copy(deep=True)
    if type(start) == str:
        start = datetime.datetime.strptime(start, "%m/%d/%Y")
    if type(end) == str:
        end = datetime.datetime.strptime(end, "%m/%d/%Y")
    dfm.reset_index(drop=True,inplace=True)
    dfm["Active Days"] = None
    dfm[termcolname].fillna(end, inplace=True)
    dfm[termcolname] = pd.to_datetime(dfm[termcolname])
    dfm[activecolname] = pd.to_datetime(dfm[activecolname])
    dfm.loc[dfm[activecolname] > dfm[termcolname],[activecolname, termcolname]] = None
    dfm.loc[dfm[termcolname] > end,[termcolname]] = end
    dfm.loc[dfm[activecolname] < start,[activecolname]] = start
    dfm.loc[(dfm[activecolname] <= end) & (dfm[termcolname] >= start),["Active Days"]] = (dfm[termcolname] - dfm[activecolname]).apply(lambda x: x.days)
    membermonths = dfm["Active Days"].sum()/30
    return membermonths

# special way to calculate membership and member months
def get_avgmembers(start, end, data, activecolname="Effective Date", termcolname='Expiration Date       '):
    if type(start) == str:
        start = datetime.strptime(start, "%m/%d/%Y")
    if type(end) == str:
        end = end + " 23:59:59"
        end = datetime.strptime(end, "%m/%d/%Y %H:%M:%S")
    elif type(end) == datetime:
        end = end.strftime("%m/%d/%Y") + " 23:59:59"
        end = datetime.strptime(end, "%m/%d/%Y %H:%M:%S")

    timeperiod = ((end - start).days + 1) / 30
    membermonths = get_member_months(start, end, data, activecolname, termcolname)

    avgmembers = membermonths / timeperiod

    return (avgmembers, membermonths)

# function for comparing member ID to personcodes dict (excel/web)
def check_employee(memberid, groupnum, optimed, group_personcodes):
    if optimed == True:
        return True
    else:
        cardholder = group_personcodes[groupnum]

        personcode = memberid[len(memberid)-2:]
        #print(personcode)

        if personcode == cardholder:
            return True
        else:
            return False

# function for comparing member ID to personcodes dict (postgresdb)
def check_employee_sql(memberid, groupnum, optimed, group_personcodes):
    if optimed == True:
        return pd.Series(True, index=memberid.index, dtype=bool)
    else:
        # create an empty bool to return
        returnbool = pd.Series(index=memberid.index, dtype=bool)
        # iterate thru member IDs and group numbers
        for i, j in pd.concat((groupnum, memberid), axis=1).iterrows():
            # if the last 2 digits in personcode dictionary match the patient's at index i,
            # then the return boolean series at index i will be True.
            # If they don't match, then the return boolean series at index i will = False
            if group_personcodes[j[0]] == j[1][-2:]:
                returnbool[i] = True
            else:
                returnbool[i] = False
    return returnbool

def ranking_table(dff, n,
                  available_indicators= ['AWP', 'Client Savings', 'Copay', 'Days Supply', 'Disp Fee',
                                         'Drug Cost', 'Estimated Network Rate', 'Ingredient Cost',
                                         'Member Pay', 'Network Savings', 'Plan Pay', 'Quantity',
                                         'Sales Tax', 'Total Amount', 'U&C'],
                  ranker="Plan Pay", grouper="Drugs", subgrouper=None,
                  statistic="Sum", applyform = False, form = '${:,.0f}', percent = False):
    """
    ranking_table() takes a dataframe (required explicitly), it returns a nicely arranged table including an extra column "# Claims",
        which is the count given a specified grouping variable. Note that # Claims doesn't return when statistic is specified as a list
        (instead, you could just specify statistic = ['mean', 'count']).
    ranker: a numeric ranking variable
    grouper: a categorical grouping variable,
    subgrouper: a subgroup of interest (optional)
    statistic: an aggregate statistic ("Sum", "Mean", or a list of the sort ['sum', 'mean', 'count']),
    n: a number of ranks
    form: a desired format as a string. E.g.: default table is ranked sums of top ranknum (10?) plan pay by drug name,
        formatted as dollars. Includes a couple bonus tabulation rows.
    percent: a boolean where = True adds two columns of percentages. applyform=True will format these two columns as rounded strings with % signs.
    applyform: the combination of applyform = True and form = 'somestring' applies specified format to all columns except for percentage columns.
    """
    if type(statistic) == list and percent == True:
        return "Returning percentage columns is not currently supported while using a list of statistics."
    counts = dff[grouper].value_counts()
    counts.name = '# Claims'
    dff = dff.reset_index(drop=True).sort_values([ranker, grouper], ascending = False) # sort
    if subgrouper: # with a subgroup:
        dff.set_index(grouper, inplace=True, drop = False) # setting index to categorical grouping variable
        dff = dff.loc[subgrouper] # selecting only a specified subgroup
        dff = dff.reset_index(drop=True)
        dff = dff.reset_index(drop=True).sort_values([ranker, grouper], ascending = False) # sort
    if statistic == 'Mean': # user specifies mean
        dff = dff.groupby(grouper).mean()[available_indicators].round(2) # grouping by the user sepcified groups, averaging the value of user specified ranker
        dff.reset_index(level=0, inplace=True) # bringing specified grouperback into dataframe
        dff = dff.reset_index(drop=True).sort_values([ranker, grouper], ascending = False) # sort
        dff = dff.merge(counts, left_on = grouper, right_on = counts.index)
    elif statistic == 'Sum':
        dff = dff.groupby(grouper).sum()[available_indicators].round(2) # grouping by the user sepcified groups, averaging the value of user specified ranker
        dff.reset_index(level=0, inplace=True)
        dff = dff.reset_index(drop=True).sort_values([ranker, grouper], ascending = False) # sort
        dff = dff.merge(counts, left_on = grouper, right_on = counts.index)
    else:
        dff = dff.groupby(grouper).agg(statistic)[available_indicators].round(2) # grouping by the user sepcified groups, averaging the value of user specified ranker
        dff.reset_index(level=0, inplace=True)
        dff = dff.reset_index(drop=True).sort_values([(ranker, statistic[0]), grouper], ascending = False) # sort
    if dff.shape[0] > n: # with more than n rows:
        dff.reset_index(inplace=True, drop=True) # reset the index and drop it
        if statistic == 'Mean':
            rest = dff.iloc[n:dff.shape[0],1:dff.shape[1]].mean().round(2) # mean of the remaining rows
            abovecat = pd.Series('Mean of Above:', index = [grouper]) # extra category
            above = dff.iloc[0:n,1:dff.shape[1]].mean().round(2) # extra category values
        elif statistic == 'Sum':
            rest = dff.iloc[n:dff.shape[0],1:dff.shape[1]].sum().round(2) # sum of the remaining rows
            abovecat = pd.Series('Total of Above:', index = [grouper]) # extra category
            above = dff.iloc[0:n,1:dff.shape[1]].sum().round(2) # extra category values
        elif type(statistic) == list:
            index = pd.MultiIndex(levels=dff.columns.levels,
                             codes=dff.columns.codes)
            rest = pd.Series(index=index)
            above = pd.Series(index=index)
            for column, stat in dff[available_indicators]:
                rest.loc[(column,stat)] = round(dff.loc[n:dff.shape[0],(column,stat)].agg(stat), 2) # sum of the remaining rows
                above.loc[(column,stat)] = round(dff.loc[0:n-1,(column,stat)].agg(stat), 2) # sum of the remaining rows
            abovecat = 'Summary of Above:' # extra category
            remain = dff.shape[0] - n # remainder sample size
            dff = dff.iloc[0:n,:] # just n rows to present
            restcat = 'All Others: (' + str(remain) + ' ' + grouper + ')' # Extra category
            dff = dff.append(above, ignore_index = True) # appending extra summary row
            dff = dff.append(rest, ignore_index = True) # appending extra summary row
            dff.loc[n, grouper] = abovecat
            dff.loc[n+1, grouper] = restcat
        else:
            return 'Statistic should be one of the following: "Mean", "Sum", or a list of .agg() functions such as ["sum", "mean", "count"]'
        if type(statistic) != list:
            remain = dff.shape[0] - n # remainder sample size
            dff = dff.iloc[0:n,:] # n rows to the table
            restcat = pd.Series('All Others: (' + str(remain) + ' ' + grouper + ')', index = [grouper]) # Extra category
            dff = dff.append(pd.concat([abovecat, above]), ignore_index = True) # appending extra summary row
            dff = dff.append(pd.concat([restcat, rest]), ignore_index = True) # appending extra summary row
    elif len(dff.shape) == 1: # changing back to dataframe in case we're down to a one-row list
        dff = pd.DataFrame(dff).T
    else:
        dff.reset_index(inplace=True, drop=True) # reset the index and drop it
        if statistic == 'Mean':
            abovecat = pd.Series('Mean of Above:', index = [grouper]) # extra category
            above = dff.iloc[0:n,1:dff.shape[1]].mean().round(2) # extra category values
        elif statistic == 'Sum':
            abovecat = pd.Series('Total of Above:', index = [grouper]) # extra category
            above = dff.iloc[0:n,1:dff.shape[1]].sum().round(2) # extra category values
        elif type(statistic) == list:
            return 'Lists of statistics are not currently supported when final len(dff) < anticipated ranknum.'
        dff = dff.iloc[0:n,:] # n rows to the table
        dff = dff.append(pd.concat([abovecat, above]), ignore_index = True) # appending extra summary row
    if percent == True:
        if dff.shape[0] >= n+2: # with more than n rows
            percentwith = (dff[ranker]/dff.loc[n:n+1, ranker].sum())*100
            percentwithout = (dff[0:n][ranker]/dff[0:n][ranker].sum())*100
        else:
            percentwith = (dff[ranker]/dff.loc[dff.index[-1], ranker])*100
            percentwithout = (dff[:-1][ranker]/dff[:-1][ranker].sum())*100
        totalabove = 100
        totalothers = 0
        percentwithoutothers = pd.concat([percentwithout, pd.Series(totalabove), pd.Series(totalothers)], ignore_index=True)
        dff["Percent With Others"] = percentwith
        dff["Percent Without Others"] = percentwithoutothers
    # Reformatting to strings for $ format
    if applyform == True:
        if percent == False:
            for column in dff[available_indicators]:
                dff[column] = dff[column].map(form.format)
            if type(statistic) != list:
                dff["# Claims"] = dff["# Claims"].map('{0:,.10g}'.format)
        if percent == True:
            dff["Percent With Others"] = dff["Percent With Others"].map('{:,.2f}%'.format)
            dff["Percent Without Others"] = dff["Percent Without Others"].map('{:,.2f}%'.format)
            for column in dff[available_indicators]:
                dff[column] = dff[column].map(form.format)
            if type(statistic) != list:
                dff["# Claims"] = dff["# Claims"].map('{0:,.10g}'.format)
    return dff

def time_table(dff, n, start_date, end_date, df_members=None, df_employees=None,
               available_indicators=['AWP', 'Client Savings', 'Copay', 'Days Supply', 'Disp Fee',
                                     'Drug Cost', 'Estimated Network Rate', 'Ingredient Cost',
                                     'Member Pay', 'Network Savings', 'Plan Pay', 'Quantity',
                                     'Sales Tax', 'Total Amount', 'U&C'],
               rankfirst=False, ranker="Plan Pay", grouper = "Drugs", time = "Day",
               applyform = False, form = '${:,.0f}', avgmonth = False, timevar = 'Date Processed'):
    """
    time_table() creates a dataframe focused on time intervals like day, week, month, and year.
    dff: is a required dataframe including the available_indicators and the timevar.
    df_members and df_employees: required dataframes of all members and employees for a group, structured as in transforms.py (part of our reporting project)
    ranker: a numeric variable that we can sort and perform arithmetic operations (sum, mean) on such as Plan Pay.
    n: the number of ranks desired
    grouper: a categorical variable over which we aggregate, e.g., sum of Plan Pay by grouper="Drugs"
    rankfirst: a boolean that determines whether the function will find the ranked groups for the entire interval first, or...
        find the time intervals first, then aggregate and rank within each of those. Example: if ranker="Plan Pay, grouper="Drugs", and rankfirst=True...
        then you will be tracking the top n drugs for the entire dataframe by month. Otherwise if rankfirst=False, then you will track the top ten
        drugs for each month individually.
    applyform and form: respectively, a Boolean argument for applying formatting at all, and the format for mapping to the values.
        avgmonth is a boolean that only works when time="Month" or "Quarter" (untested for other cases).
        It adds the following columns: Members (a member count by month), Employees (the same for employees),
    PMPM: uses another function to calculate PMPM, and PEPM: uses another function to calculate PEPM. Setting avgmonth = True will also
        change most of the summary stats at the bottom of the table from sums to means.
    """
    if rankfirst == True:
        dff1 = dff.groupby(grouper).sum()[available_indicators].round(2) # grouping by the user sepcified category, summing the value of user specified numeric y
        dff1 = dff1.sort_values(ranker, ascending = False) # sorting
        dff1 = dff1.reset_index() # bringing the catindicator back to a column
        dff = dff[dff[grouper].isin(dff1[0:(n)][grouper])] # grabbing all individual values for the top subgroups

    if time == 'Day':
        dff[time] = dff[timevar]
    elif time == 'Week':
        dff[time] = dff[timevar].dt.to_period('W')
        dff[time] = dff[time].dt.to_timestamp(how = 'Start')
    elif time == 'Month':
        dff[time] = dff[timevar].dt.to_period('M')
        dff[time] = dff[time].dt.to_timestamp(how = 'Start')
        #dff[time] = pd.to_datetime(dff['Date Processed'], format = '%Y %m')
    elif time == 'Year':
        dff[time] = dff[timevar].dt.year
        dff[time] = pd.to_datetime(dff[time], format = '%Y')
    elif time == 'Quarter':
        dff[time] = dff[timevar].dt.quarter
    else:
        return "You must specify time as a string of 'Day', 'Week', 'Month', 'Quarter', or 'Year.'"

    dff = dff.groupby([time, grouper]).sum()[available_indicators].round(2) # grouping and summing by both catindicator and date
    dff = dff.reset_index() # bringing the dates and catindicator back to the columns
    if rankfirst == False:
        dff1 = pd.DataFrame()
        for times in dff[time].unique():
            dff1 = dff1.append(dff[dff[time] == times].sort_values([ranker, grouper], ascending=False).reset_index()[0:n], ignore_index = True)
        dff = dff1

    if time == 'Day': # cleaner looking timestamps for the table
        dff[time] = dff[time].dt.strftime('%m/%d/%Y')
    elif time == 'Week':
        dff[time] = dff[time].dt.strftime('%W/%Y')
    elif time == 'Month':
        dff[time] = dff[time].dt.strftime('%m/%Y')

    if avgmonth == False:
        # sums for the summary row:
        above = dff.groupby(grouper).sum()[available_indicators].round(2) # category summary values
        above.reset_index(inplace=True)
        above[grouper] = above[grouper].map('Total {:}'.format) # category name
        summarycat = pd.Series('Total All', index= [grouper])
        summary = dff.loc[:,available_indicators].sum().round(2) # final summary row
        summary = pd.concat([summarycat,summary])
        dff = dff.append(above, ignore_index = True) # appending category summary rows
        dff = dff.append(summary, ignore_index = True) # appending final summary row
    else:
        # using means instead of sums for summary row:
        above = dff.groupby(grouper).mean()[available_indicators].round(2) # extra category values
        above.reset_index(inplace=True)
        above[grouper] = above[grouper].map('Average {:}'.format) # category name
        dff = dff.append(above, ignore_index = True) # appending extra summary row
        # Here we need to build off time_table on brand/gen/spec across months
        # The goal is to get a dff that includes averages for plan pay by member count and employee count in a given month
        if time == 'Quarter':
            if datetime.now().month < 4:
                dates = [str(datetime.now().year - 1)]*len(dff[time][0:dff.shape[0]-above.shape[0]]) + ('Q' + dff[time][0:dff.shape[0]-above.shape[0]].astype(int).astype(str))
            else:
                dates = [str(datetime.now().year)]*len(dff[time][0:dff.shape[0]-above.shape[0]]) + ('Q' + dff[time][0:dff.shape[0]-above.shape[0]].astype(int).astype(str))
            dates = pd.to_datetime(dates).dt.to_period(time[0])
            start = dates.dt.to_timestamp(how="Start").unique()
            end = dates.dt.to_timestamp(how="End").unique()
            #months = [month.month for month in rrule(MONTHLY, dtstart=pd.to_datetime(start[0].astype(datetime)),
            #                                         until=pd.to_datetime(end[-1].astype(datetime)))]
            quarts = dff[time][0:dff.shape[0]-above.shape[0]].unique()
            df_members.reset_index(drop=True, inplace=True)
            df_members["Expiration Date       "] = pd.to_datetime(df_members["Expiration Date       "])
            df_members["Effective Date"] = pd.to_datetime(df_members["Effective Date"])
            df_members["Expiration Date       "].fillna(end[-1], inplace=True)
            membercount = pd.DataFrame(columns=quarts, index=["Count", "Membermonths"])
            for idx, quart in enumerate(quarts):
                start2 = str(start[idx])
                end2 = str(end[idx])
                start3 = datetime.strptime(start2[:19], "%Y-%m-%dT%H:%M:%S")
                end3 = datetime.strptime(end2[:19], "%Y-%m-%dT%H:%M:%S")
                x, y = get_avgmembers(start3, end3, df_members)
                membercount.loc["Count", quart] = x
                membercount.loc["Membermonths", quart] = y
            df_employees.reset_index(drop=True, inplace=True)
            df_employees["Expiration Date       "] = pd.to_datetime(df_employees["Expiration Date       "])
            df_employees["Effective Date"] = pd.to_datetime(df_employees["Effective Date"])
            df_employees["Expiration Date       "].fillna(end[-1], inplace=True)
            employeecount = pd.DataFrame(columns=quarts, index=["Count", "Membermonths"])
            for idx, quart in enumerate(quarts):
                start2 = str(start[idx])
                end2 = str(end[idx])
                start3 = datetime.strptime(start2[:19], "%Y-%m-%dT%H:%M:%S")
                end3 = datetime.strptime(end2[:19], "%Y-%m-%dT%H:%M:%S")
                x, y = get_avgmembers(start3, end3, df_employees)
                employeecount.loc["Count", quart] = x
                employeecount.loc["Membermonths", quart] = y
            for quart in quarts:
                dff.loc[dff[time] == quart, ranker + ' PMPM'] = dff.loc[dff[time] == quart, ranker]/membercount.loc["Membermonths",quart]
                dff.loc[dff[time] == quart, ranker + ' PEPM'] = dff.loc[dff[time] == quart, ranker]/employeecount.loc["Membermonths",quart]
                dff.loc[dff[time] == quart, 'Members'] = membercount.loc["Count",quart]
                dff.loc[dff[time] == quart, 'Employees'] = employeecount.loc["Count",quart]
        elif time == 'Month':
            dates = pd.to_datetime(dff[time][0:dff.shape[0]-above.shape[0]]).dt.to_period(time[0])
            start = dates.dt.to_timestamp(how="Start").unique()
            end = dates.dt.to_timestamp(how="End").unique()
            months = pd.to_datetime(dff[time][0:dff.shape[0]-above.shape[0]]).dt.month.unique()
            df_members.reset_index(drop=True, inplace=True)
            df_members["Expiration Date       "] = pd.to_datetime(df_members["Expiration Date       "])
            df_members["Effective Date"] = pd.to_datetime(df_members["Effective Date"])
            df_members["Expiration Date       "].fillna(end[-1], inplace=True)
            membercount = pd.DataFrame(columns=months, index=["Count", "Membermonths"])
            for idx, month in enumerate(months):
                start2 = str(start[idx])
                end2 = str(end[idx])
                start3 = datetime.strptime(start2[:19], "%Y-%m-%dT%H:%M:%S")
                end3 = datetime.strptime(end2[:19], "%Y-%m-%dT%H:%M:%S")
                x, y = get_avgmembers(start3, end3, df_members)
                membercount.loc["Count", month] = x
                membercount.loc["Membermonths", month] = y
            df_employees.reset_index(drop=True, inplace=True)
            df_employees["Expiration Date       "] = pd.to_datetime(df_employees["Expiration Date       "])
            df_employees["Effective Date"] = pd.to_datetime(df_employees["Effective Date"])
            df_employees["Expiration Date       "].fillna(end[-1], inplace=True)
            employeecount = pd.DataFrame(columns=months, index=["Count", "Membermonths"])
            for idx, month in enumerate(months):
                start2 = str(start[idx])
                end2 = str(end[idx])
                start3 = datetime.strptime(start2[:19], "%Y-%m-%dT%H:%M:%S")
                end3 = datetime.strptime(end2[:19], "%Y-%m-%dT%H:%M:%S")
                x, y = get_avgmembers(start3, end3, df_employees)
                employeecount.loc["Count", month] = x
                employeecount.loc["Membermonths", month] = y
            for month in months:
                dff.loc[pd.to_datetime(dff["Month"]).dt.month == month, ranker + ' PMPM'] = dff.loc[pd.to_datetime(dff["Month"]).dt.month == month, ranker]/membercount.loc["Membermonths",month]
                dff.loc[pd.to_datetime(dff["Month"]).dt.month == month, ranker + ' PEPM'] = dff.loc[pd.to_datetime(dff["Month"]).dt.month == month, ranker]/employeecount.loc["Membermonths",month]
                dff.loc[pd.to_datetime(dff["Month"]).dt.month == month, 'Members'] = membercount.loc["Count",month]
                dff.loc[pd.to_datetime(dff["Month"]).dt.month == month, 'Employees'] = employeecount.loc["Count",month]
        else:
            return 'time must be Month or Quarter while avgmonth==True.'
        above = dff[0:dff.shape[0]-above.shape[0]].groupby(grouper).mean()[['Members', 'Employees', ranker + ' PMPM', ranker + ' PEPM']].round(2) # aggregate category values
        above.index = above.index.map('Average {:}'.format)
        above.reset_index(inplace=True)
        above.set_index(dff.loc[dff[grouper].isin(above[grouper])].index, inplace=True)
        planpaysumsbymonth = dff[0:dff.shape[0]-above.shape[0]].groupby(time).sum()[['Plan Pay']]
        avgmembercnt, totalmembermonths = get_avgmembers(start_date, end_date, df_members)
        avgemployeecnt, totalemployeemonths = get_avgmembers(start_date, end_date, df_employees)
        summary = pd.Series(("", "Aggregate All", # final summary row values
                             planpaysumsbymonth.mean()[0],
                             avgmembercnt,
                             avgemployeecnt,
                             planpaysumsbymonth.sum()[0]/totalmembermonths,
                             planpaysumsbymonth.sum()[0]/totalemployeemonths
                             ),
                            index=(time, grouper, ranker, 'Members', 'Employees', ranker + ' PMPM', ranker + ' PEPM'))
        dff.loc[dff[grouper].isin(above[grouper]),
                ['Members', 'Employees', ranker + ' PMPM', ranker + ' PEPM']] = above.loc[dff[grouper].isin(above[grouper]),
                                                                                          ['Members', 'Employees', ranker + ' PMPM', ranker + ' PEPM']]
        dff = dff.append(summary, ignore_index=True)

    if applyform == True: # applying specified format
        for column in dff[available_indicators]:
            dff[column] = dff[column].map(form.format)
        if time == 'Quarter':
            dff[time] = dff.loc[0:dff.shape[0]-above.shape[0]-1,time].map('{0:,.10g}'.format)
        if avgmonth == True:
            for column in dff[[ranker + ' PMPM', ranker + ' PEPM']]:
                dff[column] = dff[column].map('${:,.2f}'.format)
            for column in dff[['Members', 'Employees']]:
                dff[column] = dff[column].apply(lambda x: round(x))
                dff[column] = dff[column].map('{0:,.10g}'.format)
    dff.loc[(dff[time].isnull()) | (dff[time].astype(str).str.lower() == 'nan'), time] = "" # replacing time variable's nan value for summary row
    return dff

class BaseDF(ABC):
    pass

class BaseClean(BaseDF):
    pass

class clean_member_dates(BaseClean):
    def __init__(self, df_members, start_date, end_date,
                 effective = 'Effective Date',
                 expiration = 'Expiration Date       ',
                 status = 'status',
                 active = 'A',
                 inactive = 'I',
                 lastupdate = 'lastehoupdate'):
        self.df_members = df_members
        self.start_date = start_date
        self.end_date = end_date
        self.effective = effective
        self.expiration = expiration
        self.status = status
        self.active = active
        self.inactive = inactive
        self.lastupdate = lastupdate

    def clean_effective(self):
        """Recursive method that cleans strange effective member dates and fills in null values
        PARAMETERS:
        self.df_members | pandas.DataFrame | dateframe of members
        self.effective | string | column name for member active dates, obj/str/date col type
        self.expiration | string | column name for member term dates, obj/str/date col type
        self.status | string | column name for member status, obj/str col type
        self.active | string | string value for active members beneath status col
        self.inactive | string | string value for inactive members beneath status col
        self.lastupdate | string | column name for lastupdate of database row, obj/str/date type
        self.start_date | string or date | the start date for the report
        RETURNS:
        df_members | pandas.DataFrame | DataFrame with col vals either date types or pd.to_datetime()
                                        compliant strings based on input values.
        """

        df_members = self.df_members
        effective = self.effective
        status = self.status
        active = self.active
        inactive = self.inactive
        lastupdate = self.lastupdate
        start_date = self.start_date

        try:
            pd.to_datetime(df_members[effective])
        except Exception as e:
            print('Erroneous active date for members detected...')
            fullstack = ''.join(traceback.format_exception(None, e, e.__traceback__))
            fullstack = fullstack.split('\n')
            for line in fullstack:
                if 'dateutil.parser._parser.ParserError:' in line:
                    wonky = line.split('month must be in 1..12: ')[1]
                    print(wonky)
            df_members.loc[(df_members[status] == inactive) & (df_members[effective] == wonky), effective] = start_date
            try:
                pd.to_datetime(df_members.loc[(df_members[status] == active) & (df_members[effective] == wonky), lastupdate])
                df_members.loc[(df_members[status] == active) & (df_members[effective] == wonky), effective] = df_members[lastupdate]
            except:
                df_members.loc[(df_members[status] == active) & (df_members[effective] == wonky), effective] = start_date
            self.clean_effective()
        df_members[effective] = df_members[effective].fillna(start_date)

        return df_members

    # recursive function built to check for odd term date values, grab those values on exception,
    # run again, and fill null values before closing out.
    def clean_expiration(self):
        """Recursive method that cleans strange expiration member dates and fills in null values
        PARAMETERS:
        self.df_members | pandas.DataFrame | dateframe of members
        self.expiration | string | column name for member term dates, obj/str/date col type
        self.status | string | column name for member status, obj/str col type
        self.active | string | string value for active members beneath status col
        self.inactive | string | string value for inactive members beneath status col
        self.lastupdate | string | column name for lastupdate of database row, obj/str/date type
        self.end_date | string or date | the end date for the report
        RETURNS:
        df_members | pandas.DataFrame | DataFrame with col vals either date types or pd.to_datetime()
                                        compliant strings based on input values.
        """
        df_members = self.df_members
        expiration = self.expiration
        status = self.status
        active = self.active
        inactive = self.inactive
        lastupdate = self.lastupdate
        end_date = self.end_date

        try:
            pd.to_datetime(df_members[expiration])
        except Exception as e:
            print('Erroneous term date for members detected...')
            fullstack = ''.join(traceback.format_exception(None, e, e.__traceback__))
            fullstack = fullstack.split('\n')
            for line in fullstack:
                if 'dateutil.parser._parser.ParserError:' in line:
                    wonky = line.split('month must be in 1..12: ')[1]
                    print(wonky)
            df_members.loc[(df_members[status] == active) & (df_members[expiration] == wonky), expiration] = end_date
            try:
                pd.to_datetime(df_members.loc[(df_members[status] == inactive) & (df_members[expiration] == wonky), lastupdate])
                df_members.loc[(df_members[status] == inactive) & (df_members[expiration] == wonky), expiration] = df_members[lastupdate]
            except:
                df_members.loc[(df_members[status] == inactive) & (df_members[expiration] == wonky), expiration] = end_date
            self.clean_expiration()
        df_members[expiration] = df_members[expiration].fillna(end_date)

        return df_members
