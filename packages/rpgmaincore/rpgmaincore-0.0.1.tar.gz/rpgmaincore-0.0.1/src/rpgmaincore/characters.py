from random import randint

class Character:
    def __init__(self,attributes_list=[]):
        self.attributes = {name:(0,max) for name,max in attributes_list}
    def change(self,attribute,value):
        c,max = self.attributes[attribute]
        self.attributes[attribute] = value,max
    def up(self,attribute,value=1):
        c,max = self.attributes[attribute]
        self.attributes[attribute] = c+value,max
    def down(self,attribute,value=1):
        c,max = self.attributes[attribute]
        self.attributes[attribute] = c-value,max
    def test(self,attribute,bonus=0):
        c,max = self.attributes[attribute]
        return randint(0,max)<=c+bonus


if __name__ == '__main__':
    test = Character([('force',100),('int',100)])
    test.change('force',40)
    test.up('force')
    print(test.attributes)
    print(test.test('force'))
