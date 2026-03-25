n = 23

currentseq=0
maxsequence=0
while n > 0:
    rem = n % 2
 
    if rem==1:
        currentseq+=1
         
    else:
         
        if currentseq>maxsequence:
            
            maxsequence=currentseq
        currentseq=0
     
    n = n//2
if currentseq>maxsequence:
            
            maxsequence=currentseq
    
    
    
    
print(maxsequence)
