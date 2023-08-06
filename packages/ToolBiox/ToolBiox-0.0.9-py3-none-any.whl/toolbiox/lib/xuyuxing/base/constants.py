from datetime import date
import calendar
from Bio.Data import CodonTable

# Time
day_name = list(calendar.day_name)
day_abbr = list(calendar.day_abbr)

month_name = list(calendar.month_name)
month_abbr = list(calendar.month_abbr)

# codon table




if __name__ == '__main__':

    # get today
    print(date.today())

    # print a calendar for 2019
    print(calendar.calendar(2019))

    #
