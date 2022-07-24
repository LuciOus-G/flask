from flask.ext.appsfoundry.parsers import SqlAlchemyFilterParser, ParserBase
from flask.ext.appsfoundry.parsers.standardinputs import InputField
from flask.ext.appsfoundry.parsers.filterinputs import IntegerFilter, \
    DateTimeFilter, EnumFilter, StringFilter, BooleanFilter
from flask.ext.appsfoundry.parsers.converters import naive_datetime_from_iso8601
from flask.ext.restful.inputs import boolean

from . import models


class EmployeeParserBase(ParserBase):
    id = InputField(type=int)
    #years_experience = InputField(type=int, default=0, store_missing=False)
    #dob = InputField(type=naive_datetime_from_iso8601)
    first_name = InputField()
    #is_active = InputField(type=boolean)


class EmployeeListParser(SqlAlchemyFilterParser):
    __model__ = models.Employee
    id = IntegerFilter(multi_format='multiarg')
    years_experience = IntegerFilter()  # defaults to: multi_format='csv')
    dob = DateTimeFilter()
    job = EnumFilter(enum=models.EMPLOYEE_JOBS)
    first_name = StringFilter()
    is_active = BooleanFilter()
    preferred_shift_ids = IntegerFilter()


class EmployeeAlternateListParser(SqlAlchemyFilterParser):
    __model__ = models.Employee
    job_id = EnumFilter(enum=models.EMPLOYEE_JOBS, dest='job')
