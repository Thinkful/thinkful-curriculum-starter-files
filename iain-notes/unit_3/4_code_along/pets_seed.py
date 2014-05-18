"pets_seed.py - reusable seed class for the db"

from pets_model import (
    Base,
    Species,
    Breed,
    Pet,
    Person,
    Shelter
)

class SeedClass(object):
   
    @classmethod
    def _get_items(cls):
        "return all non-private attributes of the class"
        items = []
        for attr in dir(cls):
            if attr[0] != "_":
                items.append( getattr(cls, attr) )
        return items


# callable that builds and returns a seed class
def get_seed_class():
    
    class PetSeedClass(SeedClass):
        cat = Species(name="Cat")
        dog = Species(name="Dog")
        
        persian = Breed(name="Persian", species=cat)
        tabby = Breed(name="Tabby", species=cat)
        lab = Breed(name="Labrador Retriever", species=dog)
        poodle = Breed(name="Poodle", species=dog)

        bcspca = Shelter(name="BCSPCA")
        aspca = Shelter(name="ASPCA")

        titchy = Pet(name='Titchy', age=17, dead=True, adopted=True,
            shelter=None, breed=tabby)
        jackson = Pet(name='Jackson', age=10, dead=False, adopted=True,
            shelter=bcspca, breed=persian)
        ginger = Pet(name='Ginger', age=1, dead=False, adopted=False,
            breed=poodle, shelter=bcspca)

        iain = Person(first_name='Iain', last_name='Duncan', 
            pets=[ titchy, jackson ] )


    return PetSeedClass       

