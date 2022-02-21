import subprocess
ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
try:
    output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
    status = "WIFI"
except subprocess.CalledProcessError:
    # grep did not match any lines
    status = "NOWIFI"
    
if status == "WIFI":
    print("Red disponible")
else:
    print("Red no disponible")