
counts = {'Digits':0,'Charaters':0}

def counter(inPut):
  for x in inPut:
    if x.isdigit():
      counts['Digits']+=1
    elif x.isalpha():
      counts['Charaters']+=1
  print(counts)

