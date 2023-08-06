debit = [10000,25000,57000,35000 ]
kredit = [15000,45000,]

def results (debit, kredit):
    z= 0
    x= 0
    for i in debit:
        z+=i
    for u in kredit: 
        x+=u
    print(f"debit : {z}, kredit : {x}" )



results(debit,kredit)    
        
