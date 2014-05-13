Database Testing Tools
----------------------

Expected example

    class ExpectedCat(object):
        _fields = ['name','age','dead','adopted','breed_id','shelter_id']
        _required_fields = ['name','adopted']
        def __init__(self, values):
            self._value = values
            for k,v in self.values.items():
                setattr(self, k, v)
      
        @property 
        def values(self):
            return self._values            

        def verify(self, cat):
            # check attributes are filled
            for attr in self._fields:
                expected_val = getattr(self, attr)
                actual_val = getattr(cat, attr)
                assert actual_val == expected_val, ( "cat.%s should be %s is %s"
                   % (attr, expected_val, actual_val) 
            # check required fields have values
            for attr in self._required_fields:
                assert getattr(cat, attr), "cat should have a %s value" % attr

    # now in our test, we can use the ExpectedCat class to hold values
    # from which we make a cat and we can use it to verify the whole cat in one
    # line
    
    def test_new_cat_no_breed(self):
        "test_new_cat_no_breed - creating a cat with no breed should work" 
        cat_expected = ExpectedCat( name='Fifi', age=10, adopted=True)
        # call the SUT method that makes a cat from a dict of values
        self.app.create_cat( cat_expected.values )    
        # get the newest cat record from the database
        new_cat = self.db_session.query(Cat).all()[-1]
        # verify our cat is good in one step
        cat_expected.verify( new_cat )



