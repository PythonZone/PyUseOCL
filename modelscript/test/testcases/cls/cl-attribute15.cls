    //@Metric "enumeration" 0
    //@Metric "enumeration literal" 0
    //@Metric "class" 1
    //@Metric "plain class" 1
    //@Metric "association" 0
    //@Metric "plain association" 0
    //@Metric "association class" 0
    //@Metric "attribute" 8

class model Cl_class03

class A
    attributes
        /  a : Integer {id}
        / - b : Integer {id}
        # c : Integer {id,readOnly}
        - d : Integer
        + e : Integer
        ~ f : Integer
        g : Integer {id}
        h : Integer {readOnly}
