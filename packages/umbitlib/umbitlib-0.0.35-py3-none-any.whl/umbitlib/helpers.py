#################
# IMPORTS
#################
from ast import Add
import pandas as pd
import src.umbitlib.dates as mconst
import math
import numpy as np
import datetime
import calendar
from typing import Type, Union, List



#################
# FORMATTING FUNCTIONS
#################

def human_format(num):
    """
    Takes in a number and returns a truncated version with a suffix of ' ',K,M,B, or T.
    Dependent on numerical magnitude.
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


    
#################
# ARITHMETIC FUNCTIONS
#################

def check_nan(value):
    """
    Replaces NAN values with 0 so they can be passed into equations.
    """
    if math.isnan(value):
        return 0.0
    return value


def clean_division(dividend: Union[int, float], divisor: Union[int, float]):
    """
    Summary:
        Custom division function. Returns 0 if divisor is 0. Otherwise returns the actual result of division.

    Args:
        dividend (numerical)
        divisor (numerical)

    Returns:
        float: Result of division

    Raises:
        TypeError: If at least one of the parameters is neither int nor float

    Example:
        clean_division(45, 8.5) -> 5.294117647058823
        clean_division(45, 0) -> 0.0        
    """
    for var in [dividend, divisor]:        
        if not isinstance(var, int) and not isinstance(var, float):
            raise TypeError('Please make sure all inputs are type int or float.')

    try:
        if divisor == 0:
            return 0.0
        return check_nan(dividend/divisor)
    except:
        return 0.0

    
def up_down(value1: Union[int, float], value2: Union[int, float], text: str='up', rounded_inputs: bool=False, decimals: int=2):
    
    """
    Summary:
        Compares two numbers to see if the first is equal to or higher/lower than the second
        Allows for rounding and if rounding occurs it compares those two numbers prior to comparison
        Returns a string from the dictionary corresponding to the text argument

    Args:
        value1 (numerical): first number
        value2 (numerical): second number         
        text (str, optional): Specifies which string pair to return (see returns section). Defaults to 'up'. options are: ['greater','up','higher','increase','above','success','+']         
        rounded (boolean, optional): Defaults to False, if True value1 and value2 are rounded to the number of digits indicated by decimals parameter
        decimals (int, optional): Defaults to 2, Round value1 and value2 to the specified number of decimal places before comparing        
        
    Returns: 
        str: Either first or second item based on inputs 'greater'/'less', 'higher'/'lower', '+'/'-', 'increase'/'decrease', 'above'/'below', 'success'/'danger'

    Raises:
        typeError: If value1 and value2 aren't both type int or float

    Example: 
        up_down(2, 1, 'greater', round=True, decimals=2) -> 'less'  
    """
    dict = {
        'greater':'less',
        'up':'down',
        'higher':'lower',
        'increase':'decrease',
        'above':'below',
        'success':'danger',
        '+':'-'
    }
    
    for var in [value1, value2]:        
        if not isinstance(var, int) and not isinstance(var, float):
            raise TypeError('Please make sure all inputs are type int or float')

    if rounded_inputs:
        value1 = round(value1, decimals)
        value2 = round(value2, decimals)

    try:
        if value1 > value2:
            return(text)                
        elif value1 < value2:
            return(dict[text])            
        elif value1 == value2:
            return("in-line with")
    except:
        return(f"Error in up_down function value1: {value1}​ value2: {value2}​")


def delta(dividend: Union[int, float], divisor: Union[int, float], input_rounded: bool=False, input_decimals: int=2, output_rounded: bool=False, output_decimals: int=2):

    """
    Summary: 
        Returns the percentage difference between the dividend and the divisor.  Rounding can be done on dividend and divisor 
        prior to the percentage difference caluclation being performed. 

    Args:
        dividend (numerical): The value TO which you want to determine the percentage change (The dividend of the calcuation)
        divisor (numerical): The value FROM which you want to determine the percentage change (The divisor of the calculation)
        input_rounded (bool, optional): When True will round dividend and divisor prior to perfoming the percent change calculation. Defaults to 'False'
        input_decimals (int, optional): Sets the decimal places to which dividend and divisor will round if input_rounded=True. Defaults to 2
        output_rounded (bool, optional): When Treu will round the result to the decimals defined in output_decimals
        output_decimals (int, optional): Sets the decimal places to which result will round if output_rounded=True. Defaults to 2

    Returns:
        float: Will return the value of dividend / divisor - 1 using the clean_division function (This sets the result to 0 instead of resulting in a divide by zero error)
    """

    for var in [dividend, divisor]:        
        if not isinstance(var, int) and not isinstance(var, float):
            raise TypeError('Please make sure all inputs are type int or float')

    if input_rounded:
        dividend = round(dividend, input_decimals)
        divisor = round(divisor, input_decimals) 

    result = clean_division(dividend, divisor) - 1

    if output_rounded:
        result = round(result, output_decimals)
    
    return result
    

def evaluation(value1: Union[int, float], value2: Union[int, float], difference: bool=True, rounded_inputs: bool=True, decimals: int=0):
    """
    Summary: 
        Compares the difference (default) between the first input (value1) relative to the second input (value2)
        Or the difference (difference=False) between the first input (value1) relative to the second input divided by the second input (value2)
    
    Args:
        value1 (numerical): The value TO which you want to determine the difference or percentage change
        value2 (numerical): The value FROM which you want to determine the difference or percentage change
        difference (bool, optional): Defaults to True, determines if function will return the difference as a value (True) or percent change (False)
        rounded_inputs (bool, optional): Defaults to True, when True will round value1 and value2 prior to performing the percent change calculation
                                NOTE: The result of the percent change calculation is not rounded
        decimals (int, optional): Defaults to 0, Round value1 and value2 to the specified number of decimal places before comparing 
    
    Returns:        
        Dictionary of:
            value1 (numerical): User input
            value2 (numerical): User input
            val_delta (numerical): If difference=True, numerical difference between value1 and value2; If difference=False, percent change between value1 and value2
            val_up (str): Based on delta will be 'in-line with', 'above', or 'below'

    Raises:
        typeError: If value1 and value2 aren't both type int or float

    Example: 
        evaluation(1,2,False,False,2) -> {'value1': 1, 'value2': 2, 'val_delta': 0.5, 'val_up': 'below'}

    """

    for var in [value1, value2]:        
        if not isinstance(var, int) and not isinstance(var, float):
            raise TypeError('Please make sure all inputs are type int or float')

    if difference:
        if rounded_inputs:
            value1 = round(value1, decimals)
            value2 = round(value2, decimals)
        delta = value1 - value2
    else:
        if rounded_inputs:
            value1 = round(value1, decimals)
            value2 = round(value2, decimals)
        delta = clean_division((value1 - value2), value2)

    if delta == 0:
       val_up = 'in-line with'
    elif delta > 0:
       val_up = 'above'
    elif delta < 0:
       val_up = 'below'

    dict_out = {
        'value1' : value1,
        'value2' : value2,
        'val_delta' : abs(delta),
        'val_up' : val_up,
    }

    return dict_out


#################
# CLASS HELPING FUNCTIONS
#################

def trgt_month_total(object, metric, year='cur'):
    """
    Calculates the value for the target month based on desired metric and year. (prior = prior year, cur = current year)
    Default state is current year. ('cur') Pervious year = 'prev'  
    """
    if year == 'cur':
        year = 0
    elif year == 'prev':
        year = 1

    x = object[(object['cur_fy_flg'] == year) & (object['cur_fy_month_flg'] == 1)][metric].sum()
    return x


def trgt_month_total_ar(df: pd.DataFrame, metric: str):
    """
    Summary: Returns the sum of the given metric for the target post period (typically the last complete month).

    Args:
        df (pd.DataFrame): Pandas DataFrame with columns 'post_period' and metric to be summed
        metric (str): DataFrame column to sum

    Returns:
        numerical value: Sum of the metric column for the target post period

     Raises:
        TypeError: If parameter metric is not a string and/ or parameter df is not a Pandas DataFrame
        KeyError: If column metric or 'post_period' is not found in the DataFrame df

    Example:
        trgt_month_total_ar(df, 'payments')    
    """
    if not isinstance(metric, str):
        raise TypeError('metric variable must be a string.')

    if not isinstance(df, pd.DataFrame):
        raise TypeError('df variable must be a Pandas DataFrame.')

    if not metric in df.columns:
        raise KeyError('Column ' + metric + ' not found in DataFrame.')    

    if not 'post_period' in df.columns:
        raise KeyError('Column post_period not found in DataFrame.')

    x =  df[df['post_period']==mconst.TARGET_PD][metric].sum() 
    return x


def fytd_total(object, metric, year='cur'):
    """
    Calculates the value for a fiscal year based on desired metric and year.
    Default state is current year. ('cur') Pervious year = 'prev'
    """
    if year == 'cur':
        year = 0
    elif year == 'prev':
        year = 1

    x = object[(object['cur_fy_flg'] == year) & (object['fytd_flg'] == 1)][metric].sum()
    return x



def twelve_month_total(
        object: pd.DataFrame,
        metric: str,
        date_column: str = 'post_period',
        rolling_dates: list = mconst.LST_ROLLING_DATES,
    ) -> float:
    """
    Calculates the rolling 12 month total for the specified metric.  
    12 month rolling period is defined as the 12 months prior to the target month.

    Args:
        object (pd.DataFrame): Pandas Dataframe consisting of date column and metric needing to be summed
        metric (str): Column name in DataFrame consisting of number values that can be summed
        date_column (str): Default = 'post_period', column name in DataFrame consisting of string dates
        rolling_dates(list[str]): Default = mconst.LST_ROLLING_DATES, list of dates in string format to filter DataFrame date_column values by 

    Returns:
        (number): Sum total of metric for dates in rolling dates list
    """
    from pandera import DataFrameSchema, Column

    schema = DataFrameSchema(
        {
            date_column: Column(str),
            metric: Column(float, coerce=True, nullable=True)
        }
    )
    validated_df = schema(object)    
    return validated_df[validated_df[date_column].isin(rolling_dates)][metric].sum() #refactored ver.  needs checking



def twelve_month_avg(object, metric):
    """
    Summary: 
        Calculates the rolling 12 month avearge for the specified metric. 12 month rolling period is 
        defined as the 12 months prior to the target month (last completed month).

    Args:
        object (dataframe)
        metric (string) 
        
    Returns: 
        float or int

    Raises:
        typeError: If metric is not a of type int or float

    Example: 
        twelve_month_average(df,'charges')
    """
    #Needs a check to see if there are 12 months
    x = clean_division(object[object['post_period'].isin(mconst.LST_ROLLING_DATES)][metric].sum(), 12) #refactored ver.  needs checking
    return x



def lst_metric_postperiods(df:pd.DataFrame, metric:str)->pd.Series:
    """
    Summary: 
        Calculates monthly totals for the specified metric from the prior fiscal year begin date to the last completed month  
        PFYTD is defined as every month since the July before last i.e. if today is 6/8/2022 the list will span from 7/1/2020 to 5/1/2022

    Args:
        df (pandas Dataframe): a Dataframe with at least these 3 columns: ['cur_fy_flg', 'post_period', metric]
        metric (str): name of the metric column to sum up by month

    Returns:
        List (pandas.core.series.Series): A list of aggregated values, one for each month PFYTD with 0 for months where data wasn't present
    
    """
    # Conditional to allow pass through for missing data
    if df.empty == True: 
        result = df
    else:
        # Sum the dataframe 
        df = df[df['cur_fy_flg'].isin([0,1])].groupby('post_period')[metric].sum().reset_index() 
        # Matching date format so join will work
        df['post_period'] =  df['post_period'].dt.strftime('%m/%d/%Y') 
        # Left Join df to the date list and fill in any missing month values with 0's and extract just the summed up metric column
        result = pd.merge(pd.DataFrame(mconst.LST_PFY_FYTD_MONTHS, columns=['post_period']), pd.DataFrame(df, columns=['post_period',metric]), on='post_period',how = "left").fillna(0)[metric]
    return result


def cnt_unique(object, metric, col, year='cur', tmframe='trgtmon'):
    """
    Takes in a dataframe and a column.  Counts the target month unique occurences at the selected column's aggregate
    for the year specified.
    Default state is current year. ('cur') Pervious year = 'prev'
    tmframe can be set to the following: (trgtmon (default), year)
    metric = (sx_case, visit_cnt)
    """
    if year == 'cur':
        year = 0
    elif year == 'prev':
        year = 1

    if metric == 'sx_case':        
        if tmframe == 'trgtmon':
            x = object[(object['cur_fy_flg'] == year) & (
                object['cur_fy_month_flg'] == 1) & (object['surgical_case_flg'] == 1)][col].nunique()
            return x
        elif tmframe == 'year':
            x = object[(object['post_period'].isin(mconst.LST_ROLLING_DATES)) & (object['surgical_case_flg'] == 1)][col].nunique()
            return x
    elif metric == 'visit_cnt':
        if tmframe == 'trgtmon':
            x = object[(object['cur_fy_flg'] == year) & (
                object['cur_fy_month_flg'] == 1)][col].nunique()
            return x
        elif tmframe == 'year':
            x = object[(object['post_period'].isin(mconst.LST_ROLLING_DATES))][col].nunique()
            return x

###########################
# Custom Functions
##########################

def days_in_month(date: datetime.date):
    """
    Summary:
        Takes any datetime object and returns the number of days for the given month.

    Args:
        date (datetime): a valid date, whose month will be counted in its number of days.

    Returns: 
        int: number of days in the month.

    Raises:
        typeError: If date isn't of datetime type.

    Example: 
        days_in_month(date.fromisoformat('2022-05-01')) -> 31
    """
    if not isinstance(date, datetime.date):
        raise TypeError('Please make sure input date is of datetime type')
    
    results = calendar.monthrange(date.year, date.month)[1] 
    return results

def lst_sums_per_dttm(df, metric, date_grouper, include_dates_lst):
    """
    Dynamically sums a specified metric by a specified date grouper.  Only includes dates that are found in the include_dates_lst argument.
    metric: pass in any numerical column that you want to aggregate
    date_grouper: the date column by which the data should be grouped by
    include_dates_lst: a list of dates by which your df should be subset.  (i.e. a list of 12 months for a summing up column x by month for 12 months.)
    """
    result = df[pd.to_datetime(df[date_grouper]).isin(include_dates_lst)].groupby(date_grouper)[metric].sum().reset_index().sort_values(date_grouper, ascending = True).reset_index(drop=True).fillna(0)[metric].tolist() 
    return result


# %%
def add(a:int, b:int, c:int=0) -> int:
    """ Add two or three integers and return an integer result.

    Args:
        a (int) :            Your first number
        b (int) :            Your second number
        c (int, optional) :  Your third number

    Returns:
        int

    Raises:
        typeError: if a, b, & c aren't all integers

    Example:
        add(1, 2)        

    """
    for var in [a, b, c]:        
        if not isinstance(var, int) :
            raise TypeError('Please make sure all inputs are integers')
    
    result = a + b + c

    return result