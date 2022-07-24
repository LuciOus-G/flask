# from decimal import Decimal
# from unittest import TestCase
# import random
# from flask.ext.appsfoundry.parsers import DecimalFilter
#
# from tests.functional import EmployeeListParser, EMPLOYEE_JOBS, \
#     ParserTestCase
# from tests.fixtures.models import Employee
# from tests.fixtures.testutils.parsers import test_app
#
#
# class ScalarBooleanFieldTests(ParserTestCase):
#
#     def test_eq(self):
#         parser = EmployeeListParser()
#
#         with test_app.test_request_context('?is_active__eq=true'):
#             args = parser.parse_args().pop('filters')
#
#             q = self.session.query(Employee)
#             for expr in args:
#                 q = q.filter(expr)
#
#             self.assertEqual(q.count(), self.num_active)
#
#     def test_ne(self):
#         parser = EmployeeListParser()
#
#         with test_app.test_request_context('?is_active__ne=true'):
#             args = parser.parse_args().pop('filters')
#
#             q = self.session.query(Employee)
#             for expr in args:
#                 q = q.filter(expr)
#
#             self.assertEqual(q.count(), self.num_inactive)
#
#
# class ScalarIntegerFieldTests(ParserTestCase):
#
#     def test_eq(self):
#         emp = self.given_any_employee()
#         self.when_http_request_querystring_is("?id__eq={0.id}".format(emp))
#         self.then_database_query_should_return(lambda e: e.id == emp.id)
#
#     def test_ne(self):
#         emp = self.given_any_employee()
#         self.when_http_request_querystring_is("?id__ne={0.id}".format(emp))
#         self.then_database_query_should_return(lambda e: e.id != emp.id)
#
#     def test_lt(self):
#         emp = self.given_any_employee()
#         self.when_http_request_querystring_is("?id__lt={0.id}".format(emp))
#         self.then_database_query_should_return(lambda e: e.id < emp.id)
#
#     def test_lte(self):
#         emp = self.given_any_employee()
#         self.when_http_request_querystring_is("?id__lte={0.id}".format(emp))
#         self.then_database_query_should_return(lambda e: e.id <= emp.id)
#
#     def test_gt(self):
#         emp = self.given_any_employee()
#         self.when_http_request_querystring_is("?id__gt={0.id}".format(emp))
#         self.then_database_query_should_return(lambda e: e.id > emp.id)
#
#     def test_gte(self):
#         emp = self.given_any_employee()
#         self.when_http_request_querystring_is("?id__gte={0.id}".format(emp))
#         self.then_database_query_should_return(lambda e: e.id >= emp.id)
#
#     def test_in_multiarg(self):
#
#         emps = self.given_any_employee_list()
#
#         self.when_http_request_querystring_is(
#             "?" + "&".join(["id__in={0.id}".format(emp) for emp in emps]))
#         self.then_database_query_should_return(
#             lambda e: e.id in [emp.id for emp in emps])
#
#     def test_in_csv(self):
#
#         years_exp = self.given_any_years_of_experience()
#         emps = self.given_employees_with_years_of_experience(years_exp)
#
#         self.when_http_request_querystring_is(
#             "?years_experience__in={}".format(
#                 ",".join(str(emp.years_experience) for emp in emps)))
#
#         self.then_database_query_should_return(
#             lambda e: e.years_experience
#                       in [emp.years_experience for emp in emps])
#
#     def test_notin_multiarg(self):
#
#         emps = self.given_any_employee_list()
#
#         self.when_http_request_querystring_is(
#             "?" + "&".join(["id__notin={0.id}".format(emp) for emp in emps])
#         )
#         self.then_database_query_should_return(
#             lambda e: e.id not in [emp.id for emp in emps]
#         )
#
#     def test_notin_csv(self):
#
#         years_exp = self.given_any_years_of_experience()
#
#         self.when_http_request_querystring_is(
#             "?years_experience__notin={}".format(
#                 ",".join(str(exp) for exp in years_exp)))
#
#         self.then_database_query_should_return(
#             lambda e: e.years_experience not in years_exp)
#
#     def test_contains_multiarg(self):
#         self.skipTest("not implemented")
#
#     def test_contains_csv(self):
#
#         emp = self.given_any_employee()
#
#         self.when_http_request_querystring_is(
#             "?preferred_shift_ids__contains={}".format(
#                 ",".join(str(sid) for sid in emp.preferred_shift_ids)))
#
#         expected_ids = lambda e: any([shift_id in e.preferred_shift_ids for shift_id in emp.preferred_shift_ids])
#
#         self.then_database_query_should_return(expected_ids)
#
# class ScalarDecimalFieldTests(TestCase):
#
#     def test_type(self):
#
#         field = DecimalFilter()
#         self.assertEquals(field.type, Decimal)
#
#
#
# class ScalarStringFieldTests(ParserTestCase):
#
#     def test_eq(self):
#
#         any_first_name = self.employees[0].first_name
#         employees_with_name = len([emp for emp in self.employees
#                                    if emp.first_name == any_first_name])
#
#         with test_app.test_request_context('/?first_name__eq={}'.format(any_first_name)):
#             query = self.build_query()
#
#             self.assertEqual(employees_with_name, query.count())
#
#     def test_ne(self):
#
#         any_first_name = self.employees[0].first_name
#         emps_different_name = len([emp for emp in self.employees
#                                    if emp.first_name != any_first_name])
#
#         with test_app.test_request_context('/?first_name__ne={}'.format(any_first_name)):
#             query = self.build_query()
#             self.assertEqual(emps_different_name, query.count())
#
#     def test_ilike(self):
#         any_first_name = random.choice(self.employees).first_name
#         emps_with_name = len([emp for emp in self.employees
#                              if emp.first_name.upper()[1:] == any_first_name.upper()[1:]])
#
#         with test_app.test_request_context('/?first_name__ilike={}'.format("%" + any_first_name[1:].upper())):
#             query = self.build_query()
#             self.assertEqual(emps_with_name, query.count())
#
#     def test_like(self):
#         any_first_name = random.choice(self.employees).first_name
#         emps_with_name = len([emp for emp in self.employees
#                               if emp.first_name[1:] == any_first_name[1:]])
#
#         with test_app.test_request_context('?first_name__like={}'.format("%" + any_first_name[1:])):
#             query = self.build_query()
#             self.assertEqual(emps_with_name, query.count())
#
#
# class ScalarDateFieldTests(ParserTestCase):
#
#     def test_eq(self):
#         any_birthdate = random.choice(self.employees).dob
#         employees_with_birthdate = len([e for e in self.employees
#                                         if e.dob == any_birthdate])
#
#         with test_app.test_request_context('/?dob__eq={}'.format(any_birthdate.isoformat())):
#             query = self.build_query()
#             self.assertEqual(employees_with_birthdate, query.count())
#
#     def test_ne(self):
#         any_birthdate = random.choice(self.employees).dob
#         emps_with_different_birthdate = len([e for e in self.employees
#                                         if e.dob != any_birthdate])
#
#         with test_app.test_request_context('/?dob__ne={}'.format(any_birthdate.isoformat())):
#             query = self.build_query()
#             self.assertEqual(emps_with_different_birthdate, query.count())
#
#     def test_lt(self):
#         any_birthdate = random.choice(self.employees).dob
#         expected_count = len([e for e in self.employees
#                               if e.dob < any_birthdate])
#
#         with test_app.test_request_context('/?dob__lt={}'.format(any_birthdate.isoformat())):
#             query = self.build_query()
#             self.assertEqual(expected_count, query.count())
#
#     def test_lte(self):
#         any_birthdate = random.choice(self.employees).dob
#         expected_count = len([e for e in self.employees
#                               if e.dob <= any_birthdate])
#
#         with test_app.test_request_context('?dob__lte={}'.format(any_birthdate.isoformat())):
#             query = self.build_query()
#             self.assertEqual(expected_count, query.count())
#
#     def test_gt(self):
#         any_birthdate = random.choice(self.employees).dob
#         expected_count = len([e for e in self.employees
#                               if e.dob > any_birthdate])
#
#         with test_app.test_request_context('/?dob__gt={}'.format(any_birthdate.isoformat())):
#             query = self.build_query()
#             self.assertEqual(expected_count, query.count())
#
#     def test_gte(self):
#         any_birthdate = random.choice(self.employees).dob
#         expected_count = len([e for e in self.employees
#                               if e.dob >= any_birthdate])
#
#         with test_app.test_request_context('/?dob__gte={}'.format(any_birthdate.isoformat())):
#             query = self.build_query()
#             self.assertEqual(expected_count, query.count())
#
#     # test_in_multiarg
#     # test_in_csv
#     # test_notin_multiarg
#     # test_notin_csv
#
#
# class ScalarEnumFieldTests(ParserTestCase):
#
#     def test_eq(self):
#         job_id = random.choice(EMPLOYEE_JOBS.keys())
#         expected_count = len([e for e in self.employees
#                               if e.job == EMPLOYEE_JOBS[job_id]])
#
#         with test_app.test_request_context('?job__eq={}'.format(job_id)):
#             query = self.build_query()
#             self.assertEqual(expected_count, query.count())
#
#     def test_ne(self):
#         job_id = random.choice(EMPLOYEE_JOBS.keys())
#         expected_count = len([e for e in self.employees
#                               if e.job != EMPLOYEE_JOBS[job_id]])
#
#         with test_app.test_request_context('?job__ne={}'.format(job_id)):
#             query = self.build_query()
#             self.assertEqual(expected_count, query.count())
#
#     def test_in_multiarg(self):
#         job_ids = []
#         want_job_ids = random.randint(1, len(EMPLOYEE_JOBS))
#         while len(job_ids) < want_job_ids:
#             job_id = random.choice(EMPLOYEE_JOBS.keys())
#             if job_id not in job_ids:
#                 job_ids.append(job_id)
#
#         query_string = "&".join(["job__in={}".format(jid) for jid in job_ids])
#         query_string = "?" + query_string
#
#         expected_count = len([e for e in self.employees
#                               if e.job in [EMPLOYEE_JOBS[jid] for jid in job_ids]])
#
#         with test_app.test_request_context(query_string):
#             query = self.build_query()
#             self.assertEqual(expected_count, query.count())
#
#
#     # in_csv
#     # notin_multiarg
#     # notin_csv
#
