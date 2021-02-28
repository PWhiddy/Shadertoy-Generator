import urllib.request
import json
import time
from tqdm import tqdm

def getTotal():
    with open("AllShadertoyShaders.json") as shaders_json:
        shaders = json.load(shaders_json)
        return int(shaders['Shaders'])

def readIndex(idx, shaders, api_key):                    
    first = shaders['Results'][idx]
    source = urllib.request.urlopen("https://www.shadertoy.com/api/v1/shaders/"+first+"?key="+api_key).read()
    return source
    #sd = json.loads(source.decode("utf-8"))
    #return sd

if __name__ == "__main__":
    num = getTotal()
    print(num)
    # this can be done in batches
    with open("key.txt") as key:
        api_key = key.read().replace('\n', '')
        with open("AllShadertoyShaders.json") as shaders_json:
            shaders = json.load(shaders_json)
            for i in tqdm(range(0,num)):
                shad = readIndex(i, shaders, api_key)
                shady = json.loads(shad.decode('utf-8'))
                with open("allshaders/" + shady['Shader']['info']['id'] + ".json", 'wb') as output:
                    output.write(shad)
                    output.close()
                time.sleep(0.01)
