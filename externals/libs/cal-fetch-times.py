
filename = './fetch-times.txt'
total_time = 0
totalUrlNo = 0
with open(filename) as fh:
    line = fh.readline()
    while (line):
        line = line.rstrip()
        t = float(line)
        total_time = total_time + t
        totalUrlNo = totalUrlNo +1
        line = fh.readline()

print "total time = ", total_time /60/60
print "total URLs = ", totalUrlNo
     
