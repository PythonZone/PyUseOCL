        //@Issue cl.syn.Role.Defined 1
        //@Issue else *

    //@Metric "class" 6
    //@Metric "plain class" 5
    //@Metric "association" 1
    //@Metric "plain association" 0
    //@Metric "association class" 1
    //@Metric "attribute" 0
    //@Metric "role" 1

class model Cl_association01

class Elephant
class Banana
class Tree

class NiceThing
class TimeSlice

association class Meal
    | Take record of the bananas eaten by elephants.
    roles
        eater : Elephant[0..1]
        eater : Banana[*]
