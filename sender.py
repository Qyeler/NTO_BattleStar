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

def publish_data(folder: str):
    cur = prev = convert_files_to_bin(folder)
    while 1:
        cur = convert_files_to_bin(folder)
        if cur != prev:
            print('Changed')
            prev = cur
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