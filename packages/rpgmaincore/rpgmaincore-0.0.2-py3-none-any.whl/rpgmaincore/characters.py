from random import randint

class Character:
    """class corresponding to all types of characters"""
    def __init__(self,attributes_list=[]):
        """creation of the Character w/ its attributes
        attributes_list : list of attributes
            attribute : (name,generation_rule,max)

        """
        self.generate(attributes_list)
    def generate(self,attributes_list):
        """
        generation of the attributes
        attributes_list : list of attributes
            attribute : (name,generation_rule,max)

        """
        self.attributes = {name:(self.generate_one(rule),max) for name,rule,max in attributes_list}

    def generate_one(self,rule):
        """
        generate one attribute with the rule
        """
        val = 0
        for e in rule.split('+'):
            if 'd' in e:
                n,d = e.split('d')
                val += sum([randint(0,int(d)) for x in range(int(n))])
            else:
                val+=int(e)
        return val

    def change(self,attribute,value):
        """
        change the value of one attribute
        """
        c,max = self.attributes[attribute]
        self.attributes[attribute] = value,max
    def up(self,attribute,value=1):
        """
        raise one attribute by the value (1 by default)
        """
        c,max = self.attributes[attribute]
        self.attributes[attribute] = c+value,max
    def down(self,attribute,value=1):
        """
        raise down one attribute by the value (1 by default)
        """
        c,max = self.attributes[attribute]
        self.attributes[attribute] = c-value,max
    def test(self,attribute,bonus=0):
        """
        make a test of one attribute with a bonus (can be negative)
        """
        c,max = self.attributes[attribute]
        return randint(0,max)<=c+bonus


if __name__ == '__main__':
    test = Character([('force','30+1d10',100),('int','4d5',100)])
    test.up('force')
    print(test.attributes)
    print(test.test('force'))
