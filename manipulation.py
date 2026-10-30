str_manip = input("Enter a sentence")
length = len(str_manip)
print(length)
lastletter = str_manip[-1]
replacewith = "@"
newstr_manip = str_manip.replace(lastletter,replacewith)
print(newstr_manip)
lastthreeletters = str_manip[-1:-4:-1]
print(lastthreeletters)
Firstthreecharacters = str_manip[0:4]
lasttwocharacters = str_manip[-1:-3:-1]
print(Firstthreecharacters,lasttwocharacters)


