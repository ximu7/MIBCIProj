def change(int1,float1,str1,dict1,obj1,list1, bool1):
    int1+=1
    float1+=1
    str1+='changed'
    dict1['none_exist_key']='none_exist_value'
    obj1=None
    list1.append('change')
    bool1=True
class obj:
    pass
int1=0
float1=0.0
str1='origin'
dict1={'key':'value'}
obj1=obj()
list1=['only_element']
bool1=False
print(int1)
print(float1)
print(str1)
print(dict1)
print(obj1)
print(list1)
print(bool1)
change(int1,float1,str1,dict1,obj1,list1,bool1)
print('after change')
print(int1)
print(float1)
print(str1)
print(dict1)
print(obj1)
print(list1)
print(bool1)