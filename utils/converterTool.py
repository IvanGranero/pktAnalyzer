import scapy.all as scapy
import pandas as pd
import sys





# list of name, degree, score
nme = ["aparna", "pankaj", "sudhir", "Geeku"]
deg = ["MBA", "BCA", "M.Tech", "MBA"]
scr = [90, 40, 80, 98]

# dictionary of lists
dict = {'name': nme, 'degree': deg, 'score': scr}
    
df = pd.DataFrame(dict)
df.to_csv('file1.csv')

exit()



alldata = pd.DataFrame()

def decode_packet(pkt):
    message = []       
    for field in can_fields:            
        try:
            if field == 'flags':        
                message.append(pkt.fields[field].flagrepr())
            else:
                message.append(pkt.fields[field])
        except: 
            message.append(None)

    try:
        datahex = pkt.fields['data'].hex()
        message.append(datahex)
        dataascii = ""
        for i in range(0, len(datahex), 2):
            if 32 <= int(datahex[i : i + 2], 16) <= 126:
                dataascii += chr(int(datahex[i : i + 2], 16))                    
            else:
                dataascii += "."
        message.append(dataascii)

    except:
        message.append(None)
    return message


print (sys.argv)

#if len(sys.argv) < 2:
#    print ("needs arguments")
#    exit(1)

#filepath = sys.argv[1]
#filepath = "/home/kali/Documents/DEFCON/VicOne/mache/candump.txt"
filepath = "/home/kali/Documents/DEFCON/VicOne/mache/wellsee_mache.log"
#file_name = sys.argv[2]
file_name = "candump"

scapy.load_layer("can")

can_fields = [field.name for field in CAN().fields_desc]
dataframe_fields = can_fields + ['datahex','dataascii']
alldata = pd.DataFrame(columns=dataframe_fields)

print ("Reading CANDUMP...")

sock = CandumpReader(filepath)

pkts = sock.read_all()
sock.close()

print (len(pkts))
print ("ALL READ FROM READ ALL")
print ("Converting...")
count = 0
updateevery = 1000

for pkt in pkts:
    msg = decode_packet(pkt)
    #print(msg)
    alldata.loc[len(alldata)] = msg    
    count += 1
    if count > updateevery:
        count = 0
        print(msg)

print ("CONVERTING DTYPES...")

alldata = alldata.convert_dtypes()
try:        
    alldata.to_parquet(file_name+'.parquet.gzip', compression='gzip')
except Exception as e:
    try:
        print(e)
        alldata.to_csv(file_name+'.gzip', compression='gzip')
    except Exception as e:
        print(e)
        alldata.to_csv(file_name+'.csv', sep='\t')
print("Saved as bufferdump.")