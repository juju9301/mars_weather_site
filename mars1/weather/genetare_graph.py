from matplotlib import pyplot as plt
from pandas import read_csv

plt.style.use('fivethirtyeight')

data = read_csv('soles.csv')
sol = data['sol'].tolist()
max_temp = data['max_temp'].to_list()

#
# plt.plot(sol, max_temp)
# plt.plot(dev_x, py_dev_y, color='k', marker='.',linestyle='--',label='python')
plt.plot(dev_x, py_dev_y, color='#444444', marker='.',linestyle='--', label='python')
plt.plot(dev_x, dev_y, color='#5a7d9a', marker='o', label='all devs', linewidth=5)

plt.plot(dev_x, js1_dev_y, color='r', marker='o',label='js')



plt.legend(['py dev', 'all dev'])
plt.title('max temp on mars each sol')
plt.xlabel('Sol')
plt.ylabel('Max temp')

plt.tight_layout()
plt.grid(True)

plt.savefig('myfig.png')

plt.show()
