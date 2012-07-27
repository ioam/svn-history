from dispatch import Spec, LinearSpecs, ListSpecs, review_and_launch

# WORK IN PROGRESS

        # for kwargs in spec():  # Static
        #    result = func(**kwargs)
        #    spec.update(result)

        # for arg_group in spec():  # Dynamic
        #    for args, kwargs in arg_group:
        #       result = func(*args, **kwargs)

def invoke(function, specifier):
    for spec in next(specifier):
        function(**spec)

def numeric_example(number):
    print number

linspec = LinearSpecs('number', 1,5,steps=3, fp_precision=4)
invoke(numeric_example, linspec)


def greetings(time_of_day, person):
    greeting = '%s %s!' % (time_of_day[1:-1], person[1:-1])
    print greeting

times_of_day = ['Good morning', 'Afternoon']
people =  ['Bob', 'John']
specifier = ListSpecs('time_of_day',times_of_day ) * ListSpecs('person',people)
invoke(greetings, specifier)


