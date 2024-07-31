import json
import os

real_data_list = os.listdir('./data/real')
synth_data_list = os.listdir('./data/synth')

answer = {}
for f in real_data_list:
    answer['real/'+f] = 1
for f in synth_data_list:
    answer['synth/'+f] = 0
    
with open("answer.json", "w") as f:
    json.dump(answer, f, indent=4)