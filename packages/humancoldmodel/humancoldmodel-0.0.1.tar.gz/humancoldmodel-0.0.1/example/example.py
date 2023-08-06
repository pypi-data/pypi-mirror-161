import humanthermalmodel
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

model = humanthermalmodel.ColdStressModel()
model.simulate(30)

# print(1 * 133.3 * 10 ** (5.10765 - 1750.29 / (235 - 5)))
# print((58 * 70 +1741 * 1.74 -14 * 24 +227) * 1000 / 24 / 3600)
# print(model.basal_met(height=1.74, weight=70, age=24,))

# # 画图
#     fig = plt.figure(1, dpi=600)
#     T = pd.read_csv(filename)
#     x = range(30)
#     ax1 = plt.subplot(2, 2, 1)
#     plt.plot(x, T['3'][1:])
#     plt.xlabel('Time(min)')
#     plt.ylabel('Face skin temperature(℃)')
#     plt.axis([0, 30, 16, 32])
#
#     ax2 = plt.subplot(2, 2, 2)
#     plt.plot(x, T['40'][1:])
#     plt.xlabel('Time(min)')
#     plt.ylabel('Core temperature(℃)')
#     plt.axis([0, 30, 22, 44])
#
#     ax3 = plt.subplot(2, 2, 3)
#     plt.plot(x, T['87'][1:])
#     plt.xlabel('Time(min)')
#     plt.ylabel('Finger skin temperature(℃)')
#     plt.axis([0, 30, 10, 32])
#     plt.show()
#     fig.savefig('result.png')