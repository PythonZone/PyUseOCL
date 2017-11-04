
model Employee


class Person
attributes
  name : String
  age : Integer
  salary : Real
operations
  raiseSalary(rate : Real) : Real
end

package sf jchjvh cj

class Company
attributes
  name : String
  location : String
operations
  hire(p : Person)
  fire(p : Person)
end

-- associations

association WorksFor between
  Person[*] role employee
  Company[0..1] role employer
end

-- constraints

constraints

context Person::raiseSalary(rate : Real) : Real
  post raiseSalaryPost: 
    salary = salary@pre * (1.0 + rate)
  post resultPost:
    result = salary

context Company::hire(p : Person)
  pre  hirePre1: p.isDefined()
  pre  hirePre2: employee->excludes(p)
  post hirePost: employee->includes(p)

context Company::fire(p : Person)
  pre  firePre:  employee->includes(p)
  post firePost: employee->excludes(p)
