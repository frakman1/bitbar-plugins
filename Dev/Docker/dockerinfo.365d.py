#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os, sys
import argparse
import subprocess
import simplejson, urllib
import json
import re
from time import sleep


os.environ["PATH"] += os.pathsep + '/usr/local/bin'
DOCKER_PATH = 'docker'
log_icon = 'iVBORw0KGgoAAAANSUhEUgAAAA4AAAAWCAYAAADwza0nAAAACXBIWXMAAC4jAAAuIwF4pT92AAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAqZJREFUOI2Fk0tvU0cYhp9vzvjY+MQxzoUUJzQRkbgJFBAgVaWqhEBVVandd9ElP4Ml6rYL1lT8AlYsERESAnG/CRSJQpTYUZOAHcf2OfE5Z2ZY2HFSEqXvcvQ97/t+Mxqhp8uHS8U0F9wcHxm4NFUuBYNBTvI5TWIsYRSzUm+bD9Xa8nrLXL03t3hDAH48UT7z3YmJp7//PCOjxTzGWgTBWQOiQEAQPK148rbK37efLSkAz8kfP5yelIPDBYw1ZLRGecJas03U6ZD1M4iCJDWcPT7O5IFiWQNY7POnD1/z6PUCx6bHmK/WmSqXOH98Auss1ZUGC8sNllbXefDsA0P7nNEAnue1poYyHBxM2Kgt8uLNZ8KVf3n1/B310DA97BNbOD+RZ3KmwOw/LTSAGNtKrQMgp4VfTxYZK2QAeLkUMlPO8/FzBwS0CAIoAKOIjKWvTQigkPUAGMh6JGlvyCH6yk+n7pQDObZQi1htJQwHmm9LPloJAEEPzGmFpXsm4tC/fD998VBByaeP8wAY66iFhnqYsj+vKWQVAL4WnHPQg3WcWLDSr+YpYXRAMzqgu626q+N7kBh6iYKnUWNhozYWZFQxq7cMNiWybbhXf74WOwG4cHSkcGGytD64TzESZCgXM/jeTpNN3X3ftArg/tyntq+Fc4cCpob8PaFufO85ANsxzuw9/R+uDxLFNo4Su8d4V7FxgNsCNxLandT9LxjG9qvENFnruu2U23acGIdDpA+2O67aSXevGiZb62+a98FmaO41Nna/n1ZnyzA23U/eB8O2+vPxYqu+vrEztbkNTC00ojTtgw8qlWh5uXn41sv624V6/FVit0ktNLyoRs251fD0ri998Wj5t29K+tr4oH8kyCpdWUucc1Qqa+n1eGTxr9lZ0i9VXSb1MMtpkAAAAABJRU5ErkJggg=='
#log_icon = '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'
shell_icon = 'iVBORw0KGgoAAAANSUhEUgAAABUAAAAUCAYAAABiS3YzAAAAAXNSR0IArs4c6QAABA5JREFUOBGNlE1sG0UUx/8zY683thvHThri5oMImhKl4UMEJEKgCJACUQlIFXABqQdUlJJDpAJCIDiBxAFKIaW0ai4I1EuRUOgBKlUIoqQGSqNASZEAF4ja2iVOm9qOHdvr3eHNrOMAPtDR7s7He/Ob9zXL8D9NSukllc30RiuqCerjjLFyZV7TsZqVyoLM5e5MffrZWyuzc/35n+YNazEFkLa3uRmBW3qLwb7bY01P7HieGcbcfxk1ULIscGXy2OSlgxMPrsbPabl3I3W2BDgDfVFeUl+gbkuXjD737Bfh4e2Pk+WrepE+/4ISMJrcNz6b/OBwVEoHIgi0veBF4DaO5eM2uI8hdD9H9nsHifcs2FkCCIHo2Oj56OhIH4HJHcCzRiegeenQRCzx/qGot4Wh41UDuR8c2HlXg5sEMNyxk5doftqDum6O829YSLwz3i5Mc5oYNxPY4mvQ9FdTBxL79neqeWS7gK+dIdjHUTjnaBVGVvIKtBCX2HAHh9nJEBkSWn7x7XdvypyM7VUTDaUTNqU+/HintMtoe9GD7DcEosfYxGDn9B5ynZTpVc2xyMUmihzlP3vaQeseD5xSCamPjowQa6OGrpw6PZqeiQl1ev09Qp+emXEt9IRckAIyBaUceUJuKq5O2Yg8KhC6TyBwK0f6y6+9+TPzuzQ0E/v2SbXVSknIIlC/jSP/sws1u7he1+5TCIoXJfxbXWjhNwf1/RxOQaK8TOdJicz0yac01EomWxW0foAjedit6YZBjpVZB4FeAi1IrCWqdMGBv4fpCggPuXlOHrT1XsUoJhLtnOiifDVNuQUaH/OggUrm8jEb5g0cdobiaFKCSOq6z6jMGJiHwVkBfNczXJm0EX6IIzKs7YOTzvg5lYAt/H5dzXaWXOvlqCNg7kdHZ19ZKSiGzCC4zx0X/pQIUvyVjrmFkeWuAcowHghIjTc62i+rhT9espA/S+6Ry9xP1hQlGN18lRihrPUyeMKu1c4qhSTgAnNnHCy8XFIIKsW2RV1ke49//okwfcOZ6bnI8glXqDIq6eIJyr6gBDEKHyNtLlQ46LpSWflaGRaP2EgeKIMxP92+sV+vG9m1rXpNVWwzM7HxC6+/uVvd+a4Jg34eJFaBqWppY6prpYREfHeJ/gGbZcdrr+wP3n3XHhVON7pqH01C9w6MhocGf1dbS0n3p1EDVMLKIdaimgANDw/GNwz0jymGmlfvvpqoJhobF6i7MTdPMfO7tarWzU46n84pLKyv5c66BxtNeo9S060G6ou2/EKSB5aOlrF0tKJFnRGlOBLP+qviwboInpao2lNtNdC6nu6plmd27qhq0EBKJrLfnWpigurxkb4Ueb9uLsn9W7un/ql/zWNKZC+9Pdey4W9Tunw1spRtRgAAAABJRU5ErkJggg=='
dockerps_images=[]


class c: 
    RED = '\033[31m' 
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    WHITE = '\033[0;37m'
    MAGENTA = '\033[35m'
    ENDC = '\033[0m'
    GREY = '\033[1m'
    
fullPathFileName = os.path.realpath(__file__)

def run_script(script):
    return (subprocess.Popen([script], stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True, universal_newlines=True).communicate()[0].strip())

def escape_ansi(line):
    ansi_regex = r'\x1b(' \
                 r'(\[\??\d+[hl])|' \
                 r'([=<>a-kzNM78])|' \
                 r'([\(\)][a-b0-2])|' \
                 r'(\[\d{0,2}[ma-dgkjqi])|' \
                 r'(\[\d+;\d+[hfy]?)|' \
                 r'(\[;?[hf])|' \
                 r'(#[3-68])|' \
                 r'([01356]n)|' \
                 r'(O[mlnp-z]?)|' \
                 r'(/Z)|' \
                 r'(\d+)|' \
                 r'(\[\?\d;\d0c)|' \
                 r'(\d;\dR))'
    ansi_escape = re.compile(ansi_regex, flags=re.IGNORECASE)
    return ansi_escape.sub('', line).replace("\r", "").replace("\n", "").replace("]0;","")


# Handle inputs
parser = argparse.ArgumentParser()
parser.add_argument('-s', action='store', dest='localstop',help='Stop Running Container')
parser.add_argument('-t', action='store', dest='localstart',help='Start A Stopped Container')
parser.add_argument('-r', action='store', dest='localremove',help='Remove A Stopped Container')
parser.add_argument('-rmf', action='store', dest='localforceremove',help='Force Remove A Running Container')
parser.add_argument('-b1', action='store', dest='localbash',help='Bash Into A Running Container')
parser.add_argument('-b2', action='store', dest='localsh',help='Sh Into A Running Container')
parser.add_argument('-rmi', action='store', dest='localremoveimage',help='Remove An Image')
parser.add_argument('-rmif', action='store', dest='localforceremoveimage',help='Force Remove An Image')

if(len(sys.argv) >= 2):
    if(sys.argv[1] == '-s'):   
        cmd = DOCKER_PATH + " stop " + sys.argv[2]
        run_script(cmd)
        sys.exit(0)     

    elif(sys.argv[1] == '-t'):   
        cmd = DOCKER_PATH + " start " + sys.argv[2]
        run_script(cmd)
        sys.exit(0)    
    
    elif(sys.argv[1] == '-r'):   
        cmd = DOCKER_PATH + " rm " + sys.argv[2]
        run_script(cmd)
        sys.exit(0)    

    elif(sys.argv[1] == '-rmf'):   
        cmd = DOCKER_PATH + " rm -f " + sys.argv[2]
        #print cmd
        run_script(cmd)
        sys.exit(0)  

    elif(sys.argv[1] == '-b1'):
        cmd = DOCKER_PATH + " exec -it " + sys.argv[2] + " /bin/bash"
        #print cmd
        os.system('echo "Running: {}";{}'.format(cmd,cmd))
        sys.exit(0)     

    elif(sys.argv[1] =='-b2'):
        cmd = DOCKER_PATH + " exec -it " + sys.argv[2] + " /bin/sh"
        #print cmd
        os.system('echo "Running: {}";{}'.format(cmd,cmd))
        sys.exit(0)       

    elif(sys.argv[1] == '-rmi'):   
        cmd = DOCKER_PATH + " rmi " + sys.argv[2]
        run_script(cmd)
        #print cmd
        sys.exit(0)  

    elif(sys.argv[1] == '-rmif'):   
        cmd = DOCKER_PATH + " rmi -f " + sys.argv[2]
        #print cmd
        run_script(cmd)
        sys.exit(0)  

print "🐳"
print "---"
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
dockerps_cmd = DOCKER_PATH + " ps -a --format '{{.ID}}\t{{.Image}}\t{{.Command}}\t{{.Status}}\t{{.Names}}'"
dockerps_output=run_script(dockerps_cmd)
print "📦 Containers"
if not dockerps_output:
    print"-- No Running or Stopped Containers"    
else:
    print '-- ',c.WHITE,'{:<13s}'.format('CONTAINER ID'),'{:<26s}'.format(' IMAGE'),'{:<22s}'.format('  COMMAND'),'{:<25s}'.format('   STATUS'),'{:<20s}'.format('    NAME'),c.ENDC," | size=10 font='Courier New'"
    #if '\n' not in dockerps_output:
        #dockerps_output += '\n'
    for line in dockerps_output.splitlines():
        #print "-- line:",line
        split_line = line.split("\t")
        print '-- ',c.BLUE,'{:<13s}'.format(split_line[0]),c.YELLOW,'{:<26s}'.format(split_line[1]),c.RED,'{:<22s}'.format(split_line[2]),c.MAGENTA,'{:<25s}'.format(split_line[3]),c.GREEN,'{:<20s}'.format(split_line[4]),c.ENDC," | size=10 font='Courier New'"
        
        get_img_id = DOCKER_PATH + " inspect --format='{{.Image}}' " + split_line[0]
        output = run_script(get_img_id)
        tmp = output[output.index(':')+1:]
        image_id = tmp[0:12]
        dockerps_images.append(image_id)
    
        inspect_cmd = DOCKER_PATH + " inspect " + split_line[0]
        inspect_output = run_script(inspect_cmd)
        print "---- 🔬 Inspect"
        for inspect_line in inspect_output.splitlines():
            print "------ "  + '‎‎' + inspect_line + " |  color=white size=11 font='Courier New'"

        log_cmd = DOCKER_PATH + " logs " + split_line[0].strip() +" 2> /dev/null"
        log_output = run_script(log_cmd)
        #print "---- 🪵 Log"
        print "---- Log | image={}".format(log_icon)
        for log_line in log_output.splitlines():
            log_clean = escape_ansi(log_line) 
            print "------ " , log_clean, "| color=white size=11 font='Courier New'"
        if 'Up' in split_line[3]:
            print "---- 🛑 Stop | bash=" + fullPathFileName +  " param1=-s param2={} terminal=false refresh=true".format(split_line[0])
            print "---- ↩️ Enter | none"
            print "------ bash | image={} bash=".format(shell_icon) + fullPathFileName +  " param1=-b1 param2={} terminal=true refresh=true".format(split_line[0])
            print "------ 🐚 sh   |  bash=" + fullPathFileName +  " param1=-b2 param2={} terminal=true refresh=true".format(split_line[0])
            print "---- 🔨 Force Remove | bash=" + fullPathFileName +  " param1=-rmf param2={} terminal=false refresh=true".format(split_line[0])
        
        if 'Exited' in split_line[3] or 'Created' in split_line[3]:
            print "---- ▶️ Start  |  bash=" + fullPathFileName +  " param1=-t param2={} terminal=false refresh=true".format(split_line[0])
            print "---- 🗑️ Remove |  bash=" + fullPathFileName +  " param1=-r param2={} terminal=false refresh=true".format(split_line[0])
        
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
dockerimages_cmd = DOCKER_PATH + ' images --format "{{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}"'
dockerimages_output=run_script(dockerimages_cmd)
print "🖼️ Images"
print '-- ',c.WHITE,'{:<45s}'.format('REPOSITORY'),c.WHITE,'{:<15s}'.format('TAG'),c.WHITE,'{:<15s}'.format('ID'),c.WHITE,'{:<15s}'.format('CREATED'),c.WHITE,'{:<10s}'.format('SIZE'),c.ENDC," | size=10 font='Courier New'"
for line in dockerimages_output.split('\n'):
    #print '--',line," | size=11 font='Courier New'"
    split_line = line.split("\t")
    #print '-- ',split_line[0],' ',split_line[1]
    print '-- ',c.BLUE,'{:<45s}'.format(split_line[0]),c.RED,'{:<15s}'.format(split_line[1]),c.YELLOW,'{:<15s}'.format(split_line[2]),c.MAGENTA,'{:<15s}'.format(split_line[3]),c.GREEN,'{:<10s}'.format(split_line[4]),c.ENDC," | size=10 font='Courier New'"
    if split_line[2] not in dockerps_images:
        print "---- 🗑️ Remove | bash=" + fullPathFileName +  " param1=-rmi param2={} terminal=false refresh=true".format(split_line[2])
    else:
        print "---- 🔨 Force Remove | bash=" + fullPathFileName +  " param1=-rmif param2={} terminal=false refresh=true".format(split_line[2])
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print "---"
print "🔄 Refresh | refresh=true"


