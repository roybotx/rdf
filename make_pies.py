import numpy as np
import matplotlib.pyplot as plt
from matplotlib import mlab
from matplotlib import rcParams

import utils

db = utils.__connect_to_db("scraping")
cur = db.cursor()
cur.execute("select zcode from zipcode where county = 'KingCounty' and code_type = 'Standard';")
zipcodes = [c[0] for c in cur.fetchall()]
# zipcodes = ["98004", "98005", "98006", "98007", "98052", "98053", "98033", "98034", "98059", "98011", "98012"]
data = {}
for zipcode in zipcodes:
    sql = "select count(link) from home_link where link like '%" + zipcode + "%'"
    cur.execute(sql)
    data[zipcode] = int(cur.fetchone()[0])

data = {key: value for key, value in data.items() if value > 0}

sorted_data = sorted(data.items(), key = lambda x: x[1])
print(sorted_data)

cur.close()
db.close()

Ys = tuple([d[1] for d in sorted_data])
Xs = tuple([i for i in range(1, len(sorted_data) + 1)])

fig = plt.figure(2)
rects = plt.bar(left = Xs, height = Ys, align = "center", yerr = 0.000001, color = "c")
plt.xticks(Xs, tuple([d[0] for d in sorted_data]), rotation = 45, fontsize = 7)

for a, b in zip(Xs, Ys):
    plt.text(a, b, "%.0f" % b, ha = "center", va = "bottom", fontsize = 7)

plt.title("listing amount by zipcdes")
plt.show()