"""
pet_csv_2.py
  
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
    "reads file, returns 2D array of values"
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


################################################################################
if __name__=="__main__":
    
    # Connect to an existing database
    conn = psycopg2.connect("dbname=pets user=postgres")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print "Connected"
   
    csv_values = file_to_values("pets_to_add.csv")

    # count how many pets we should get, only lines with data count
    num_pets = len( csv_values )
    print "Found %i pet records in csv file" % num_pets
    
    print "Cleaning out pet table"
    # empty our pet table to begin
    cur.execute("delete from pet where true")
    conn.commit()
    # verify pet delete worked
    cur.execute("select count(pet.id) from pet");
    count = cur.fetchone()[0]
    assert count == 0, "pet table should be empty"
    print "...Pet table is empty, ready to fill\n"
   
    # iterate through pets, creating records
    for pet_values in csv_values:
        
        # empty strings will become Nones
        name = pet_values[0] or None
        age =  pet_values[1] or None
        breed = pet_values[2] or None
        species = pet_values[3] or None
        shelter = pet_values[4] or None
        adopted = pet_values[5] or None
   
        # get the species id if species present
        if species:
            species = species.capitalize()
            cur.execute("select id from species where species.name='%s'"
                % species ) 
            res = cur.fetchone()
            species_id = res[0] if res else None
            print "species id: ", species_id
        else:
            species_id = None
    
        # get breed id if breed present
        if breed:
            # figure out what breed should be
            # in the database, our breeds are capitalized 
            breed = breed.title()
            # see if this breed is in the db
            if species_id:
                cur.execute("select id from breed where breed.name='%s' "
                    "and species_id=%i" % (breed, species_id ) )
            else:
                cur.execute("select id from breed where breed.name='%s'"
                    % breed) 
            res = cur.fetchone()
            breed_id = res[0] if res else None
            print "breed id: ", breed_id
        else:
            breed_id = None
    
        if shelter:
            # shelters are all uppercase in the db
            shelter = shelter.upper()
            print "shelter to find: ", shelter
            cur.execute("select id from shelter where shelter.name='%s'" 
                % shelter ) 
            res = cur.fetchone()
            shelter_id = res[0] if res else None
            print "shelter id: ", shelter_id
        else:
            shelter_id = None
    
        print( "Inserting pet record: (%s,%s,%s,%s,%s)" % 
            (name, age, adopted, breed_id, shelter_id) )
        cur.execute("insert into pet(name, age, adopted, breed_id, "
            "shelter_id) values (%s,%s,%s,%s,%s)", 
            (name, age, adopted, breed_id, shelter_id) )
   
    # end of pet for loop
    conn.commit()
    
    # verify pet insert worked
    print "\nChecking for %i pet records..." % num_pets
    cur.execute("select count(pet.id) from pet");
    count = cur.fetchone()[0]
    assert count == num_pets, "should be %i pets" % num_pets
    print "   success, %i pets found" % num_pets
    
    cur.close()
    conn.close()


