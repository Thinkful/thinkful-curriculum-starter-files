"""
pet_csv_1.py
  
  - additionally populate the breed, species, and shelter tables manually
  - parse the pet csv file programmatically, inserting into the
    Pet table, with the correct foreign keys to Breed, Species, Shelter

  Instructor notes:
    - this version is pretty much a top-down monolithic script
    - pet_cvs_3.py shows breaking it up into more functions

"""

import psycopg2
import psycopg2.extras
import pdb

def file_to_values(filename):
    "reads in csv file, returns 2D array of values"
    # open our csv file and read into an array of lines
    file = open(filename, 'r')
    # get all the lines of the file, skipping line 1 which has headers
    csv_lines = file.readlines()[1:]
    # drop empty lines
    csv_lines = [ line for line in csv_lines if line != '\n' ]
    # change csv_lines into lists, so we have a list of lists,
    # strip white space off values using a nested list comprehension
    csv_values = [ [ cell.strip() for cell in line.split(',') ] 
        for line in csv_lines ] 
    # return our sanitized 2D array of valid values
    return csv_values


if __name__=="__main__":

    # Connect to an existing database
    conn = psycopg2.connect("dbname=pets user=postgres")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print "Connected"
  
    # call our helper to get csv values into sanitized 2D array
    csv_values = file_to_values("pets_to_add.csv")

    # count how many pets we should get, only lines with data count
    num_pets = len( csv_values )
    print "Found %i pet records in csv file" % num_pets
    
    print "Cleaning out pet table"
    # empty our pet table to begin
    cur.execute("delete from pet where true")
    conn.commit()
    cur.execute("select count(pet.id) from pet");
    count = cur.fetchone()[0]
    assert count == 0, "pet table should be empty"
    print "...Pet table is empty, ready to fill\n"
    
    for pet_values in csv_values:
        name = pet_values[0] or None
        age =  pet_values[1] or None
        adopted = pet_values[-1] or None
        print "Inserting pet record: (%s,%s,%s)" % (name, age, adopted)
        cur.execute("insert into pet(name, age, adopted) values (%s,%s,%s)",
            (name, age, adopted) )
    conn.commit()
    
    # verify pet insert worked
    print "\nChecking for %i pet records..." % num_pets
    cur.execute("select count(pet.id) from pet");
    count = cur.fetchone()[0]
    assert count == num_pets, "should be %i pets" % num_pets
    print "   success, %i pets found" % num_pets
    
    cur.close()
    conn.close()


