# import unittest
# import random
# from os import environ
#
# from faker import Factory
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# from tests.fixtures.models import Base, Employee, EMPLOYEE_JOBS
# from tests.fixtures.parsers import EmployeeListParser
# from tests.fixtures.testutils.parsers import test_app
#
# engine = create_engine(environ.get('FEA_DATABASE_URI', None), echo=True)
# fake = Factory.create()
# Session = sessionmaker(bind=engine)
#
#
# def setUp():
#     Base.metadata.create_all(bind=engine)
#
#
# def tearDown():
#     Base.metadata.drop_all(bind=engine)
#
#
# class ParserTestCase(unittest.TestCase):
#
#     def build_query(self, parser=None):
#         if parser is None:
#             parser = EmployeeListParser()
#
#         args = parser.parse_args().pop('filters')
#
#         query = self.session.query(Employee)
#         for expr in args:
#             query = query.filter(expr)
#
#         return query
#
#     def setUp(self):
#
#         self.employees = [self.generate_employee() for _ in range(50)]
#
#         self.session = Session()
#         self.session.add_all(self.employees)
#         self.session.commit()
#
#         # These can be properties instead.
#         self.employee_count = self.session.query(Employee).count()
#         self.num_active = self.session.query(Employee).filter_by(is_active=True).count()
#         self.num_inactive = self.session.query(Employee).filter_by(is_active=False).count()
#
#     def given_any_employee(self):
#         self._given = random.choice(self.employees)
#         return self._given
#
#     def given_any_years_of_experience(self):
#         years_exp = set([emp.years_experience for emp in self.employees])
#         if len(years_exp) > 1:
#             years_exp.pop()
#         return years_exp
#
#     def given_employees_with_years_of_experience(self, years_exp):
#         self._given = [emp for emp
#                 in self.employees
#                 if emp.years_experience in years_exp]
#         return self._given
#
#     def given_any_employee_list(self):
#         self._given = []
#
#         max_emps = random.randint(1, len(self.employees)-1)
#
#         while len(self._given) < max_emps:
#             emp = random.choice(self.employees)
#             if emp.id not in self._given:
#                 self._given.append(emp)
#
#         return self._given
#
#     def when_http_request_querystring_is(self, querystr):
#         with test_app.test_request_context(querystr):
#             self._query = self.build_query()
#
#     def then_database_query_should_return(self, expec_func):
#         expected_emps = sorted(filter(expec_func, self.employees), key=lambda e: e.id)
#         actual_emps = sorted(self._query.all(), key=lambda e: e.id)
#
#         self.assertListEqual(expected_emps, actual_emps)
#
#     def generate_employee(self):
#         return Employee(
#             first_name=fake.first_name(),
#             last_name=fake.last_name(),
#             years_experience=random.randint(0, 10),
#             dob=fake.date_time_between('-40y', '-20y'),
#             job=random.choice(EMPLOYEE_JOBS.values()),
#             is_active=random.choice([True, False]),
#             preferred_shift_ids=[random.randint(1, 20) for _
#                                  in range(random.randint(1, 5))]
#         )
#
#     def delete_all_employees(self):
#         for e in self.session.query(Employee).all():
#             self.session.delete(e)
#         self.session.commit()
#
#     def tearDown(self):
#         self.session.rollback()
#         self.delete_all_employees()
#
