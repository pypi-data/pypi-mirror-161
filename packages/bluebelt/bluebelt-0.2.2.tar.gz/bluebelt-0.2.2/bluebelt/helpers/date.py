import numpy as np
import datetime

def last_iso_week_in_year(year):
    return datetime.date(year, 12, 28).isocalendar()[1]

def year_with_most_iso_weeks(years):
    return years[np.argmax([last_iso_week_in_year(year) for year in years if isinstance(year, (np.uint32, int))])]