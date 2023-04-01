cond = [[1, 2], [1, 2], [1, 2], [1, 2], [2, 3], [2, 3], [2, 3], [2, 3], [3, 4], [3, 4], [3, 4], [4, 1], [4, 1], [4, 1],
        [4, 1]]
ans = []

import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def convert_files_to_bin(folder: str):
    sequence = ''
    for i in range(1, 46):
        with open(f'{folder}\\test{i}.txt') as f:
            if f.read().split(',')[0] == 'off':
                sequence += '0'
            else:
                sequence += '1'
    return sequence

def publish_data(cur: str):
    #cur = prev = convert_files_to_bin(folder)
    #while 1:
        #cur = convert_files_to_bin(folder)
        #if cur != prev:
            #print('Changed')
    #prev = cur
    client.publish('relay/1', cur[:8], 1)
    time.sleep(0.1)
    client.publish('relay/2', cur[8:16], 1)
    time.sleep(0.1)
    client.publish('relay/3', cur[16:24], 1)
    time.sleep(0.1)
    client.publish('relay/4', cur[24:32], 1)
    time.sleep(0.1)
    client.publish('relay/5', cur[32:40], 1)
    time.sleep(0.1)
    client.publish('relay/6', cur[40:45]+'000', 1)
    time.sleep(0.5)

def rec(tmp, step):
    global cond
    if (step == 16):
        add=[]
        for i in tmp:
            add.append(i)
        ans.append(add)
    else:
        for i in range(2):
            tmp.append(cond[step - 1][i])
            rec(tmp, step + 1)
            tmp.pop()

def on_button_update():
    global cond
    str=[]
    for i in range(30):
        fst=0
        scnd=0
        with open(f'user_data/userStatus/test{i+1}.txt', 'r') as f:
            fst,scnd=f.read().split(',')
        if(fst=='on'):
            str.append(1)
        else:
            str.append(0)
    list = []
    sch = 0
    for i in range(len(str)):
        if sch % 2 == 0:
            list.append(int(str[i]))
        else:
            list[len(list)-1] += int(str[i])
        sch += 1
    tmpls = []
    sch=1
    rec(tmpls, sch)
    calcans=[]
    tmpcountcalc = []
    for i in ans:
        tmpcalc=[0]*4
        for j in range(len(i)):
            if(i[j]==1):
                tmpcalc[0]+=list[j]
            if(i[j]==2):
                tmpcalc[1]+=list[j]
            if(i[j]==3):
                tmpcalc[2]+=list[j]
            if(i[j]==4):
                tmpcalc[3]+=list[j]
        sr=sum(tmpcalc)/4
        rep=0
        for i in range(4):
            rep+=abs(tmpcalc[i]-sr)
        tmpcountcalc.append(rep)
    bestidx=0
    mindif=1e10
    for i in range(len(tmpcountcalc)):
        if(tmpcountcalc[i]<mindif):
            mindif=tmpcountcalc[i]
            bestidx=i
    finalans=[]
    for i in range(len(str)):
        if(int(str[i])==0):
            finalans.append(0)
        else:
            finalans.append(1)
    for i in range (len(ans[bestidx])):
        if(cond[i][0]==ans[bestidx][i]):
            finalans.append(0)
        else:
            finalans.append(1)
    publish_data("".join(list(map(str, finalans))))


client = mqtt.Client(client_id="Website", clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
client.tls_set(ca_certs="./ser")

#client.on_publish = on_publish
client.on_connect = on_connect
#client.on_log = on_log

client.username_pw_set('User2', '12345678')
client.connect('9226d4b3c64f41bd91b139162073c30e.s2.eu.hivemq.cloud', 8883, 3600)

#client.publish('relay/2', '10011100', 1)

publish_data(f'user_data/userStatus/')

client.disconnect()