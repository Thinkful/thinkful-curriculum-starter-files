"""
pet_csv_3.py
  - make a first pass through the file to populate the shelter table programmatically
    with shelter names
  - make a second pass to populate the species table
  - make a third pass to populate the breed table, with proper keys to species table
  - make a fourth pass to populate the pet table
  - note: you'll need to normalize capitalization
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


def empty_table(table):
    "reusable helper to clean out a table"
    cur.execute("delete from %s where True" % table)
    cur.execute("select count(%s.id) from %s" % (table, table) );
    count = cur.fetchone()[0]
    assert count == 0, "%s table should be empty" % table


def populate_shelters(pet_values, conn, cur):
    "populate the shelter table from our csv file"
    print "populate_shelter()"

    # get list of all unique shelters, dropping duplicates and empties
    shelter_entries = set( [ pet[4] for pet in pet_values if pet[4] ] )
    print("shelter_entries: %s" % shelter_entries)
    # insert them
    for shelter in shelter_entries:
        # NB cur.execute expects a list/tuple for last arg
        cur.execute("insert into shelter (name) values (%s)", (shelter,) )
    conn.commit()    
   

def populate_species(pet_values, conn, cur):   
    print "populate_species()"

    # get list of unique species, capitalizing too
    species_entries = set( [ pet[3].title() for pet in pet_values if pet[3] ] )
    print("species_entries: %s" % species_entries)
    # insert them
    for species in species_entries:
        # NB cur.execute expects a list/tuple for last arg
        cur.execute("insert into species (name) values (%s)", (species,) )
    conn.commit()    


def populate_breeds(pet_values, conn, cur):   
    print "populate_breeds()"

    # make a list in memory of all the breeds, with their species
    breed_species_pairs = [ ( pet[2], pet[3] ) for pet in pet_values ]
    # get rid of duplicates and empty entries, capitalize words
    # and only keep entries if they have *both* a breed and species
    pairs = set( [ (pair[0].title(), pair[1].title() ) for pair 
        in breed_species_pairs if (pair[0] and pair[1]) ] )
    print( "Creating breed records for: %s" % pairs)
    # insert them, using subquery to get correct species id
    for breed, species in pairs:
        # NB cur.execute expects a list/tuple for last arg
        cur.execute("insert into breed (name, species_id) values "
            "(%s, (select id from species where species.name=%s) )", 
            (breed, species) )
    conn.commit()    


def populate_pets(pet_values, conn, cur):
    print "populate_pets"

    # make a list in memory of all the pets, with their breeds
    # we have too many columns for a list comprehension to be readable
    # so we'll loop through our data to santize it before entry

    for pet in pet_values:
        name = pet[0].title()
        age = pet[1] or None
        breed = pet[2].title() or None
        shelter = pet[4] or None
        adopted = pet[5]

        # insert our pet, with subquery to get breed and shelter id
        print( "Creating pet record for %s" % name)
        # NB cur.execute expects a list/tuple for last arg
        cur.execute("insert into pet (name, age, adopted, breed_id, shelter_id) "
            " values (%s, %s, %s, "
            "(select id from breed where breed.name=%s), "
            "(select id from shelter where shelter.name=%s) )",
            (name, age, adopted, breed, shelter) )
    conn.commit()     


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
    
    # empty all the tables
    for table in ['pet','breed','species','shelter']:
        empty_table(table)

    # populate the tables
    populate_shelters(csv_values, conn, cur)
    populate_species(csv_values, conn, cur)
    populate_breeds(csv_values, conn, cur)
    populate_pets(csv_values, conn, cur)

    # verify pet inserts worked
    num_pets = len(csv_values)
    print "\nChecking for %i pet records..." % num_pets
    cur.execute("select count(pet.id) from pet");
    count = cur.fetchone()[0]
    assert count == num_pets, "should be %i pets" % num_pets
    print "   success, %i pets found" % num_pets
    
    cur.close()
    conn.close()


