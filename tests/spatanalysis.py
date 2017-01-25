from itertools import groupby


class Conflict:
    def __init__(self, best_est, region, country, lat, lon):
        self.best_est = best_est
        self.region = region
        self.country = country
        self.lat = lat
        self.lon = lon


file = open('armedConfl.csv', encoding="utf8")
header = []
for line in file:
    if 'lat' in line:
        header = line.split(',')
        break
file.close()
print(header)
ind_lat = -1
ind_lon = -1
ind_bestest = -1
ind_region = -1
ind_country = -1

for i in range(len(header)):
    if 'latitude' in header[i]:
        ind_lat = i
        break
for i in range(len(header)):
    if 'longitude' in header[i]:
        ind_lon = i
        break
for i in range(len(header)):
    if 'region' in header[i]:
        ind_region = i
        break
for i in range(len(header)):
    if header[i] == '"country"':
        ind_country = i
        break
for i in range(len(header)):
    if 'best_est' in header[i]:
        ind_bestest = i
        break

file = open('armedConfl.csv', encoding="utf8")
conflicts = []
for line in file:
    spl = line.split(',')
    print(len(spl))
    if 'Europe' in spl[33] or 'Asia' in spl[33]:
        conflicts.append(Conflict(spl[42], spl[33], spl[32], spl[28], spl[29]))
file.close()

print(conflicts[0].region)

groups = groupby(conflicts, lambda confl: confl.country)

#for key, group in groups:
    #print("Key: %s, Number of items: %s" % (key, len(list(group))))

print(len(conflicts))
