def kwargs(**students):
    for key, val in students.items():
        print("key : {} val : {} ".format(key, val))


kwargs(name='ed', age=41)
kwargs(name='ran', age=44)