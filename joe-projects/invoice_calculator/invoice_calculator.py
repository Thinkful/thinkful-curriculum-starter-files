def divide_pay(amount, staff_hours):
    """
    Divide an invoice evenly amongst staff depending on how many hours they
    worked on a project
    """
    total_hours = 0
    for person in staff_hours:
        total_hours += staff_hours[person]

    per_hour = amount / total_hours

    for person in staff_hours:
        pay = staff_hours[person] * per_hour
        print "{} should be paid ${:.2f}".format(person, pay)

divide_pay(360.0, {"Alice": 3.0, "Bob": 3.0, "Carol": 6.0})
