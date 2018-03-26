dict = {'a':[1,2,3], 'b':[1,2,4], 'c':[1,2,5]}
print dict
for key, val in dict.items():
    print key
    print val
    
dict.clear()
print dict
for key, val in dict.items():
    print key
    print val