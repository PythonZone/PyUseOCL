    // name conflict

    //@Issue cl.fin.Attribute.InhVertical 1
    //@Issue else *


class model Cl_inhatt


class Animal
    attributes
        color : Integer
        
class Elephant < Animal
    attributes
        size : Integer

class SmallElephant < Elephant
    attributes
        color : Integer