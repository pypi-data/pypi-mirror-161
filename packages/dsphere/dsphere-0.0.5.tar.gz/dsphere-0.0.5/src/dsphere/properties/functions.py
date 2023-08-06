import numpy as np
import pandas as pd
import locale
from locale import atof, atoi
locale.setlocale(locale.LC_NUMERIC, '')
import datetime
from dateutil import tz
from typing import Optional, Union
import dateutil.parser as date_parser
import pytz

# Helper function needed everywhere below:
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
def getDtype(high_val):
    possible_dtypes = [(2**8/2, np.int8),
                       (2**16/2, np.int16),
                       (2**32/2, np.int32),
                       (2**64/2, np.int64)]
    if pd.isnull(high_val):
        return np.int8
    for (max_possible_value, possible_dtype) in possible_dtypes:
        if high_val <= max_possible_value:
            return possible_dtype

    return None #np.complex128

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
# From: https://stackoverflow.com/questions/12734517/json-dumping-a-dict-throws-typeerror-keys-must-be-a-string 
def fill_nulls_in_dict(d):
    """Convert a dict's keys to strings if they are not."""
    for key in d.keys():

        # check inner dict
        if isinstance(d[key], dict):
            value = fill_nulls_in_dict(d[key])
        elif d[key]=='"+=+NONE+=+"':
            value = None
        else:
            value = d[key]

        # convert nonstring to string if needed
        #if key is None:
        #    d['"+=+NONE+=+"'] = value
        #    del d[key]
        #el
        if key=='"+=+NONE+=+"':
            d[None] = value
            del d[key]
        elif not isinstance(key, str):
            try:
                d[str(key)] = value
            except Exception:
                try:
                    d[repr(key)] = value
                except Exception:
                    raise

            # delete old key
            del d[key]
    return d

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
def dict_to_json(d):
    json_string = "{"
    num_keys = 0
    for key in d.keys():
        if key is None:
            key_string = '"+=+NONE+=+"'
        elif isinstance(key, str):
            key_string = '"{}"'.format(str(key))
        else:
            key_string = str(key)
            
        if isinstance(d[key], dict):
            value_string = dict_to_json(d[key])
        elif isinstance(d[key], str):
            value_string = '"{}"'.format(d[key])
        elif d[key] is None:
            value_string = '"+=+NONE+=+"'
        else:
            value_string = str(d[key])
        
        if num_keys > 0:
            json_string += ', '
        json_string += key_string + ':' + value_string
        num_keys += 1
    json_string += "}"
    return json_string


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Convert the $XX.XX amount values to floats
def convert_amount(val, type='int', fillna=False):
    try:
        if val!=val or val is None or (isinstance(val, str) and val==''):
            # Null or blank case
            if fillna:
                if type=='int':
                    return 0
                else:
                    return 0.0
            else:
                return val
        elif isinstance(val, str):
            # String
            val_stripped = val.strip('$')
            if type=='int':
                return atoi(val_stripped)
            else:
                return atof(val_stripped)
        elif isinstance(val, int):
            # Int
            if type=='int':
                return val
            else:
                return float(val)
        elif isinstance(val, float):
            # Float
            if type=='int':
                return np.round(val)
            else:
                return val
        else:
            return val
    except:
        return None
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Return a list of the numeric columns in the given dataframe, excluding the given list and all index 'IX' columns
# TODO: Tie this IX flag to the function inside __init__.py
def get_numeric_cols(all_features, exclude=None):
    import pandas as pd
    all_features_types = all_features.dtypes
    all_features_types_df = pd.DataFrame(all_features_types, columns=['types'])
    all_features_types_df['nulls'] = (all_features!=all_features).sum(axis=0)

    # Get numeric cols
    all_features_types_df_numeric = all_features_types_df[all_features_types_df['types'].apply(lambda x:x in ['float16', 'float32', 'float64', 'int8', 'int16', 'int32', 'int64'])].reset_index(drop=False)

    # Take out IX columns
    all_features_types_df_numeric2 = all_features_types_df_numeric[all_features_types_df_numeric['index'].apply(lambda x: 'IX::' not in x)]

    # Take out columns that are only null
    num_rows = all_features.shape[0]
    #print("# rows:", num_rows)
    all_features_types_df_numeric3 = all_features_types_df_numeric2[all_features_types_df_numeric2['nulls']<num_rows]

    # Take out exclude cols
    if exclude is not None:
        all_features_types_df_numeric4 = all_features_types_df_numeric3[~all_features_types_df_numeric3['index'].isin(exclude)]
    else:
        all_features_types_df_numeric4 = all_features_types_df_numeric3
        
    final_parent_feature_cols = list(all_features_types_df_numeric4['index'].values)
    print("Have {} numeric cols".format(len(final_parent_feature_cols)))
    return final_parent_feature_cols


def convert_timezone(dt_in: Optional[datetime.datetime], tz_in: str, tz_out: str, keep_tz: bool = False) -> Optional[datetime.datetime]:
    """Given input datetime and corresponding in + out timezones, converts from tz_in to tz_out"""
    if dt_in:
        dt = dt_in.replace(tzinfo=tz.gettz(tz_in))
        dt_out = dt.astimezone(tz.gettz(tz_out))
        if not keep_tz:
            dt_out = dt_out.replace(tzinfo=None)
        return dt_out
    return None


def get_latest_date_for_day_of_week(day_of_week: str, timezone: str = 'UTC', str_format: Optional[str] = None) -> Union[datetime.date, str]:
    """Starting from current date (for a given timezone), finds most recent date for the specified day of week
    (i.e., within the last week)"""
    # NOTE: these are the correct numbers for python datetime weekday() (not isoweekday())
    # [note also that these are different from cron, where sunday = 0]
    dayofweek_nums = {
        0: ['monday', 'mon', 'm'],
        1: ['tuesday', 'tues', 't'],
        2: ['wednesday', 'wed', 'w'],
        3: ['thursday', 'thur', 'thurs', 'th'],
        4: ['friday', 'fri', 'f'],
        5: ['saturday', 'sat', 'sa'],
        6: ['sunday', 'sun', 's'],
    }
    dayofweek_num = [num for num, daystrings in dayofweek_nums.items() if day_of_week.lower() in daystrings][0]
    print("Converted {} to {}".format(day_of_week, dayofweek_num))
    # start with current client date
    latest_date = convert_timezone(datetime.datetime.utcnow(), 'UTC', timezone).date()
    print("Starting date={} (dow={})".format(latest_date, latest_date.weekday()))
    while latest_date.weekday() != dayofweek_num:
        latest_date = latest_date - datetime.timedelta(days=1)
    print("Found latest date={} (dow={})".format(latest_date, latest_date.weekday()))
    if str_format is not None:
        latest_date = latest_date.strftime(str_format)
    return latest_date

# base_timezone: Your timezone that all dates should be converted into (default=UTC, can be US/Pacific, US/Eastern, etc.)
# See: pytz.all_timezones for a full list of possible inputs
# If no timezone information like '-0800Z' is detected, then the time information is not converted across timezones
# TODO: Figure out what happens if you pass None here to leave all timezones as-is...will this crash FeatureSpace?
# ignore_bad_dates: If True, then when a bad date is parsed (such as 13/36/1) then None will be returned, errors will be suppressed
# If False, then an error will be raised and the function calling parse_date will fail, to show these bad dates to the user.
# This includes when the year is <=1677 or >=2622 because pyarrow has an overflow error if the date goes beyond the range
# specified here: https://github.com/pandas-dev/pandas/blob/master/pandas/_libs/tslibs/dsphere.datetime/np_datetime.c
# (see _NS_MIN_DTS and _NS_MAX_DTS)
def parse_date(x, base_timezone='UTC', ignore_bad_dates=True):
    if isinstance(x, str):
        if x!=x or x=='' or x==' ':
            return None
        try:
            parse_date = date_parser.parse(x)
            # Handle years that are out of range for what datetime values pyarrow can store
            # See: https://stackoverflow.com/questions/54202896/how-to-work-around-out-of-bounds-nanosecond
            if parse_date.year<=1677 or parse_date.year>=2622:
                if ignore_bad_dates:
                    return None
                else:
                    print("ERROR: Parsed date '{}' contains a year {} that cannot be saved to disk correctly.".format(x, 
                                                                                                               parse_date.year))
                    raise
                    
            # Handle timezones if parsed in the date strings
            if parse_date.tzinfo is not None:
                # If timezone is parsed from the date string, convert the time to the given base_timezone
                base_timezone_pytz = pytz.timezone(base_timezone)
                parse_date_in_base_timezone = parse_date.astimezone(base_timezone_pytz)
                
                # Then remove all timezone info before returning, so the datetime.datetime object can be saved to pyarrow
                return parse_date_in_base_timezone.replace(tzinfo=None)
            return parse_date
        except ValueError:
            if ignore_bad_dates:
                return None
            else:
                print("ERROR: Bad date value found that cannot be parsed:", x)
                raise ValueError
    else:
        return x


def fix_zip_code(val):
    if val != val or val is None or val == '0' or val == '1':
        return None
    if len(val) >= 5:
        return val[:5]
    if val.isdigit() and len(val) == 4:
        return '0' + val
    if val.isdigit() and len(val) == 3:
        return '00' + val
    return val


from dateutil import relativedelta
def get_age(dob, cutoff):
    age_delta = relativedelta.relativedelta(cutoff, dob)
    return age_delta.years + age_delta.months/12.

def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
