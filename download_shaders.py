import urllib.request
import json
import time

def getTotal():
    with open("AllShadertoyShaders.json") as shaders_json:
        shaders = json.load(shaders_json)
        return int(shaders['Shaders'])

def readIndex(idx):
    with open("AllShadertoyShaders.json") as shaders_json:
        with open("key.txt") as key:
            api_key = key.read().replace('\n', '')
            shaders = json.load(shaders_json)
            first = shaders['Results'][idx]
            source = urllib.request.urlopen("https://www.shadertoy.com/api/v1/shaders/"+first+"?key="+api_key).read()
            return source
            #sd = json.loads(source.decode("utf-8"))
            #return sd

if __name__ == "__main__":
    num = getTotal()
    print(num)
    # this can be done in batches
    for i in range(0,num):
        if (i%100 == 0):
            print(i)
        with open("allshaders/s" + str(i) + ".json", 'wb') as output:
            output.write(readIndex(i))
            output.close()
        time.sleep(1.5)