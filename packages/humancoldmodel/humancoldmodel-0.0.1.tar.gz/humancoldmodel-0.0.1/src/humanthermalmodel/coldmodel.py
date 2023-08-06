#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import math
from importlib import resources
from scipy.integrate import solve_ivp
from scipy.integrate import ode
from .arterialmodel import arterial_model
import time
import datetime as dt
import matplotlib.pyplot as plt

import solartotr

class ColdStressModel:
    def __init__(
            self,
            height=1.74,
            weight=70,
            age=30,
            sex="male"
    ):
        if sex == "male":
            self._sex = 0
        elif sex == "female":
            self._sex = 1
        self._height = height
        self._weight = weight
        self._age = age

        # Default values of input condition
        self._met = 1
        self._area = 1.87

        # Default values of input condition
        self._ta = -5
        self._tr = -5
        self._rh = 0.65
        self._va = 0

        # import body data from csv file
        self._body_data = pd.read_csv(resources.open_text('humanthermalmodel', 'body_data.csv'))
        # self._body_data = pd.read_csv('../src/humanthermalmodel/body_data.csv')
        # read data from csv file
        self._adu = self._body_data["ADu"].values.T
        self._ldu = self._body_data["LDu"].values.T[0]
        self._m_base = self._body_data[["Qb"]].values.T[0]
        self._t_in = self._body_data[["Tin"]].values.T[0]
        self._cap = self._body_data[["Cjk"]].values.T[0]
        self._met_f = self._body_data[["Metf"]].values.T[0]
        self._temp_set = self._body_data[["Tset"]].values.T[0]
        self._skinr = self._body_data[["SKINR"]].values.T[0]
        self._skins = self._body_data[["SKINS"]].values.T[0]
        self._chit = self._body_data[["Chit"]].values.T[0]
        self._viewseat = self._body_data[["viewseat"]].values.T[0]
        self._viewstand = self._body_data[["viewstand"]].values.T[0]
        self._m_skin_basal = self._body_data[["m_skin_basal"]].values.T[0]
        self._m_skin_max = self._body_data[["m_skin_max"]].values.T[0]
        self._m_skin_min = self._body_data[["m_skin_min"]].values.T[0]
        self._Icl = self._body_data[["icltest"]].values.T[0]
        self._icl = 2.16
        self._i = self._body_data[["i"]].values.T[0]

        self._T = pd.DataFrame([self._t_in])

        # imporved for high cold
        self._altitude = None
        self._pt = None
        self._p0 = 101.3  # kPa
        self._solarfixtr = 0  # false:0  true:1
        self._i_dir = None

        self._m_base_sum = 86.727912
        self._filename = None



    def simulate(self, runtime, dtime=60):
        """
        Execute the cold stress model.

        Parameters
        ----------
        runtime : int
            Time [min] to run the model.
        dtime : int, optional
            Time delta [sec]. The default is 60.

        Returns
        -------
        None.

        """

        # fix BMR
        bmr = 13.88 * self._weight + 4.16 * self._height - 3.43 * self._age - 112.4 * self._sex + 54.34
        self._m_base = self._m_base * bmr / self._m_base_sum

        # fix tr with solar b=60 sharp=120
        if self._solarfixtr == 1:
            if self._i_dir is None:
                if self._altitude is not None:
                    i_dir = solartotr.get_i_dir(b=60, height=self._altitude)
                else:
                    i_dir = 800
            else:
                i_dir = self._i_dir
            self._tr = solartotr.solar_to_tr(i_dir=i_dir, ta=self._ta, b=60, sharp=120, f_bes=0.5, f_svv=0.5, t_sol=0.5)


        start = time.perf_counter()
        # self._run(dtime)
        for t in range(int(runtime * 60 / dtime)):
            print(t)
            self._run(dtime)
        end = time.perf_counter()
        print("运行耗时", end - start, "s")
        nowtime = dt.datetime.now().strftime("%Y%m%d_%H%M")
        self._filename = "./" + str(self._ta) + "_" + nowtime + "_T.csv"
        self._T.to_csv(self._filename, encoding="utf-8-sig", index=False)
        return self._T



    def _run(self, time):
        """
        Run the model.

        :param time:
        :return:
        """
        print('run')
        ex = solve_ivp(self._f, [0, time], self._t_in, method='BDF', t_eval=np.linspace(0, time, time), dense_output=True)
        # ex = solve_ivp(self._f, [0, 0.5], self._t_in, method='BDF', t_eval=np.linspace(0, 0.5, 31), dense_output=True)
        print(ex.success)
        print(ex.y.T[-1])

        T_new = pd.DataFrame([ex.y.T[-1]])
        print(T_new)
        self._T = pd.concat([self._T, T_new], ignore_index=True)


        self._t_in = ex.y.T[-1]

        dictout = {}
        return dictout

    # energy balance equations
    def _f(self, t, temp):
        # print(str(t) + 'h')
        # Calculate ha, hv, m_perfusion
        ha, hv, m_perfusion, q = arterial_model(self._m_base, temp, t)

        # Calculate temp_mean_skin
        temp_mean_skin = 0.07 * temp[3] + 0.35 * temp[35] + 0.14 * temp[19] + 0.05 * temp[27] + 0.19 * temp[59] + 0.13 * temp[67] + 0.07 * temp[75]
        # Calculate m_skin
        if temp[40] >= 37.2:
            m_skin_dil = self._m_skin_max
        elif temp[40] > 36.8:
            m_skin_dil = ((temp[40] - 36.8) / (37.2 - 36.8)) * (self._m_skin_max - self._m_skin_basal) + self._m_skin_basal
        else:
            m_skin_dil = self._m_skin_basal

        if temp_mean_skin >= 33.7:
            m_skin_con = self._m_skin_basal
        elif temp_mean_skin > 27.8:
            m_skin_con = ((temp_mean_skin - 27.8) / (33.7 - 27.8)) * (self._m_skin_basal - self._m_skin_min) + self._m_skin_min
        else:
            m_skin_con = self._m_skin_min
        m_skin = np.empty(98)
        for i in range(98):
            if ((i+1) < 89) & ((i+1) % 4 == 0):
                m_skin[i] = (m_skin_dil[i] * m_skin_con[i]) / self._m_skin_basal[i]
            else:
                m_skin[i] = 0
        # Calculate qava
        # 是基于平均皮肤温度和核心温度进行判定的，原来程序是基于手或脚的皮肤温度和核心温度进行判定的；且将34修改为33.7，对应本文的调定点
        fava = (0.265 * (temp_mean_skin - 34) + 0.953 * (temp[40] - 36.8) + 0.9126)
        if fava > 1:
            fava = 1
        elif fava < 0:
            fava = 0
        else:
            fava = fava

        qava3 = self._m_skin_max[83] * fava
        qava4 = self._m_skin_max[87] * fava

        cava = (0.265 * (temp_mean_skin - 35.4) + 0.953 * (temp[40] - 37) + 0.9126)
        if cava > 1:
            cava = 1
        elif cava < 0:
            cava = 0
        else:
            cava = cava

        qava1 = self._m_skin_max[75] * cava
        qava2 = self._m_skin_max[79] * cava

        # Calculate ksuperficialvein, (W/K) 表示浅静脉逆流与皮肤间的换热系数，基于JOS-2
        ksuperficialvein = np.array([
            0, 0, 37.768, 37.768, 0.351, 0.351, 16.634, 16.634, 0, 57.735, 0, 57.735, 0, 0, 102.012, 102.013, 54.784, 54.784, 24.277, 24.277, 16.634, 16.634
        ])

        # Calculate k_cr_sk
        Cb = 4 / 3600
        k_cr_sk = np.array([
            1.8476, 1.8476, 1.304, 1.304, 0.913, 0.913, 0.5452, 0.5452, 4.9212, 1.304, 4.9212, 1.304, 4.9212, 4.9212, 1.5637, 1.5637, 1.216, 1.216, 0.6311, 0.6311, 0.5452, 0.5452
        ])
        for i in range(22):
            k_cr_sk[i] = k_cr_sk[i] + (m_skin[4 * (i+1) - 1] * Cb)

        # m_base is the local basal metabolic rate [W]
        m_base = self._m_base

        # Calculate error signals of thermoregulation
        error = np.empty(98)
        wrm = np.empty(98)
        cld = np.empty(98)
        wrms = np.empty(98)
        clds = np.empty(98)
        for i in range(98):
            error[i] = temp[i] - self._temp_set[i]
            wrm[i] = max(0, error[i])
            cld[i] = 0 - min(0, error[i])
            wrms[i] = self._skinr[i] * wrm[i]
            clds[i] = self._skinr[i] * cld[i]
        wrms_sum = sum(wrms)
        clds_sum = sum(clds)

        # Calculate the local metabolic rate by work [W]
        w_work = np.empty(98)
        for i in range(98):
            w_work[i] = 58.2 * (self._met - 0.778) * self._area * self._met_f[i]
            w_work[i] = max(0, w_work[i])

        # Calculate local metabolic rate by shivering [W].
        Cch = 24.4
        Sch = 0
        Pch = 24.4
        if self._va > 5:
            chit = self._chit / 100
        elif self._va > 2:
            chit = self._chit / 10
        else:
            chit = self._chit
        m_sh = np.empty(98)
        for i in range(98):
            m_sh[i] = (- Cch * error[0] - Sch * (wrms_sum - clds_sum) + Pch * cld[0] * clds_sum) * chit[i]

        # Calculate pa
        pa = self._rh * 133.3 * 10 ** (5.10765 - 1750.29 / (235 + self._ta))
        isk = 0.33  # 皮肤湿阻
        iask = 0.0129  # 空气层湿阻
        hfg = 2.26 * 10 ** 6
        psatsk = np.empty(98)
        psk = np.empty(98)
        for i in range(98):
            psatsk[i] = 133.3 * 10 ** (5.10765 - 1750.29 / (235 + temp[i]))
            psk[i] = (psatsk[i] * iask + pa * isk) / (isk + iask)  # 皮肤表面蒸汽压力计算

        # Calculate q_res
        q_res = np.empty(98)
        for i in range(98):
            if i == 32:
                q_res[i] = (0.0014 * (34 - self._ta) + 0.0173 * (5.876 - pa)) * (sum(m_base) + sum(w_work) + sum(m_sh))
            else:
                q_res[i] = 0

        # Calculate qt
        # 裸体计算方法如下
        hr = np.empty(98)
        esw = np.empty(98)
        stefan = 5.67 * 10 ** (-8)
        embody = 0.99  # 身体发射率
        emenv = 1  # 环境发射率，用平均辐射温度时，取值为1
        csw = 371.2
        ssw = 33.6
        psw = 0
        for i in range(98):
            hr[i] = stefan * embody * emenv * self._viewseat[i] * ((273 + temp[i]) ** 2 + (273 + self._tr) ** 2) * ((273 + temp[i]) + (273 + self._tr))
            esw[i] = (csw * error[i] + ssw * (wrms_sum - clds_sum) + psw * wrm[i] * wrms_sum) * self._skins[i] * 2 ** (error[i] / 10)

        if self._va < 1:
            self._va = 1

        hc = np.array([
            0.1, 0.1, 0.1, 0.5 * (3 * (abs(temp[3] - self._ta)) ** 0.5 + 113 * self._va - 10.8) ** 1, 0.1, 0.1, 0.1, 3 * (3 * (abs(temp[7] - self._ta)) ** 0.5 + 113 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, 5 * (8.3 * (abs(temp[11] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, 5 * (8.3 * (abs(temp[15] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5,
            0.1, 0.1, 0.1, 4 * (8.3 * (abs(temp[19] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, 4 * (8.3 * (abs(temp[19] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, 1.2 * (8.3 * (abs(temp[19] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, 1.2 * (8.3 * (abs(temp[19] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5,
            0.1, 0.1, 0.1, (0.5 * (abs(temp[35] - self._ta)) ** 0.5 + 180 * self._va - 7.4) ** 0.5, 0.1, 0.1, 0.1, 0.5 * (5.9 * (abs(temp[39] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, (1.2 * (abs(temp[43] - self._ta)) ** 0.5 + 180 * self._va - 9) ** 0.5, 0.1, 0.1, 0.1, 0.5 * (5.9 * (abs(temp[39] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5,
            0.1, 0.1, 0.1, (5.9 * (abs(temp[39] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, (5.9 * (abs(temp[39] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, 0.5 * (5.3 * (abs(temp[59] - self._ta)) ** 0.5 + 220 * self._va - 11) ** 0.5, 0.1, 0.1, 0.1, 0.5 * (5.3 * (abs(temp[59] - self._ta)) ** 0.5 + 220 * self._va - 11) ** 0.5,
            0.1, 0.1, 0.1, 0.5 * (5.3 * (abs(temp[59] - self._ta)) ** 0.5 + 220 * self._va - 11) ** 0.5, 0.1, 0.1, 0.1, 0.5 * (5.3 * (abs(temp[59] - self._ta)) ** 0.5 + 220 * self._va - 11) ** 0.5, 0.1, 0.1, 0.1, 0.9 * (6.8 * (abs(temp[94] - self._ta)) ** 0.5 + 210 * self._va - 10.5) ** 0.5, 0.1, 0.1, 0.1, 0.9 * (6.8 * (abs(temp[94] - self._ta)) ** 0.5 + 210 * self._va - 10.5) ** 0.5,
            0.1, 0.1, 0.1, 5 * (8.3 * (abs(temp[87] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5, 0.1, 0.1, 0.1, 5 * (8.3 * (abs(temp[87] - self._ta)) ** 0.5 + 216 * self._va - 10.8) ** 0.5,
            0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1
        ])
        he = 16.5 * hc
        if self._pt is not None:
            hc = hc * ((self._pt / self._p0) ** 0.5)
            he = he * ((self._p0 / self._pt) ** 0.5)


        esw1 = np.empty(98)
        for i in range(98):
            esw1[i] = max(0, esw[i])

        qtunc = np.empty(98)
        emaxunc = np.empty(98)
        eunc = np.empty(98)
        for i in range(98):
            qtunc[i] = self._adu[i] * hr[i] * (temp[i] - self._tr) + self._adu[i] * hc[i] * (temp[i] - self._ta)  # 辐射与对流传热的计算表达式,辐射换热中用的是平均辐射温度，这个和空气温度有什么关系？？？
            # 以下为蒸发换热
            emaxunc[i] = he[i] * (psk[i] - pa) * self._adu[i]  # 皮肤水面水分扩散散热，Psatsk(i)为皮肤表面饱和蒸汽压
            eunc[i] = 0.06 * (1 - esw1[i] / emaxunc[i]) * emaxunc[i] + esw1[i]  # 皮肤蒸发热损失表达式，由皮肤表面水分扩散散热及汗液蒸发热损失两部分组成

        # 着装计算方方式如下
        # 着装部分辐射和对流换热
        fcl = np.empty(98)
        htc = np.empty(98)
        to = np.empty(98)
        qtc = np.empty(98)
        hec = np.empty(98)
        emaxc = np.empty(98)
        ec = np.empty(98)
        for i in range(98):
            fcl[i] = 1 + 0.31 * self._Icl[i]  # 计算服装面积因子
            htc[i] = 0.5 / (0.155 * self._Icl[i] + 1 / ((hc[i] + hr[i]) * fcl[i]))  # hr为辐射换热系数
            to[i] = (hr[i] * self._tr + hc[i] * self._ta) / (hr[i] + hc[i])
            qtc[i] = htc[i] * (temp[i] - to[i]) * self._adu[i]
            # 以下为着装部分蒸发换热量
            if self._pt is not None:
                hec[i] = (16.5 * (self._p0 / self._pt) * self._icl) / (0.155 * self._Icl[i] + self._icl * ((self._pt / self._p0) ** 0.97) / (hc[i] * fcl[i]))
            else:
                hec[i] = (16.5 * self._icl) / (0.155 * self._Icl[i] + self._icl / (hc[i] * fcl[i]))
            emaxc[i] = hec[i] * (psk[i] - pa) * self._adu[i]
            ec[i] = 0.06 * (1 - esw1[i] / emaxc[i]) * emaxc[i] + esw1[i]
        qt = np.empty(98)
        e = np.empty(98)

        for i in range(98):
            if self._i[i] > 0:
                qt[i] = qtc[i]
                e[i] = ec[i]
            else:
                qt[i] = qtunc[i]
                e[i] = eunc[i]


        # return d_temp 作为微分方程组
        d_temp = np.array([
            # node 0
            (m_base[0] + w_work[0] + m_sh[0] - q_res[0] - (ha[0] * (temp[0] - temp[1])) - (hv[0] * (temp[0] - temp[2])) - (k_cr_sk[0] * (temp[0] - temp[3])) - (m_perfusion[0] * Cb * (temp[0] - temp[1])) - (m_skin[3] * Cb * (temp[0] - temp[3]))) / self._cap[0],
            # node 1
            ((ha[0] * (temp[0] - temp[1])) + (q[0] * Cb * (temp[33] - temp[1]))) / self._cap[1],
            # node 2
            ((hv[0] * (temp[0] - temp[2])) + (m_perfusion[0] * Cb * (temp[0] - temp[2]))) / self._cap[2],
            # node 3
            (m_base[3] + (k_cr_sk[0] * (temp[0] - temp[3])) - qt[3] - e[3] + (m_skin[3] * Cb * (temp[0] - temp[3]))) / self._cap[3],
            # node 4
            (m_base[4] + w_work[4] + m_sh[4] - q_res[4] - (ha[1] * (temp[4] - temp[5])) - (hv[1] * (temp[4] - temp[6])) - (k_cr_sk[1] * (temp[4] - temp[7])) - (m_perfusion[1] * Cb * (temp[4] - temp[5])) - (m_skin[7] * Cb * (temp[4] - temp[7]))) / self._cap[4],
            # node 5
            ((ha[1] * (temp[4] - temp[5])) + (q[1] * Cb * (temp[33] - temp[5]))) / self._cap[5],
            # node 6
            ((hv[1] * (temp[4] - temp[6])) + (m_perfusion[1] * Cb * (temp[4] - temp[6]))) / self._cap[6],
            # node 7
            (m_base[7] + (k_cr_sk[1] * (temp[4] - temp[7])) - qt[7] - e[7] + (m_skin[7] * Cb * (temp[4] - temp[7]))) / self._cap[7],
            # node 8
            (m_base[8] + w_work[8] + m_sh[8] - q_res[8] - (ha[2] * (temp[8] - temp[9])) - (hv[2] * (temp[8] - temp[10])) - (k_cr_sk[2] * (temp[8] - temp[11])) - (m_perfusion[2] * Cb * (temp[8] - temp[9])) - (m_skin[11] * Cb * (temp[8] - temp[11]))) / self._cap[8],
            # node 9
            ((ha[2] * (temp[8] - temp[9])) + (q[2] * Cb * (temp[37] - temp[9]))) / self._cap[9],
            # node 10
            ((hv[2] * (temp[8] - temp[10])) + ((5 * m_perfusion[20] + m_perfusion[6] + m_perfusion[4]) * Cb * (temp[38] - temp[10])) + (m_perfusion[2] * Cb * (temp[8] - temp[10])) + ((5 * (qava3 + m_skin[83]) + m_skin[27] + m_skin[19]) * Cb * (temp[88] - temp[10]))) / self._cap[10],
            # node 11
            (m_base[11] + (k_cr_sk[2] * (temp[8] - temp[11])) - qt[11] - e[11] + (m_skin[11] * Cb * (temp[8] - temp[11]))) / self._cap[11],
            # node 12
            (m_base[12] + w_work[12] + m_sh[12] - q_res[12] - (ha[3] * (temp[12] - temp[13])) - (hv[3] * (temp[12] - temp[14])) - (k_cr_sk[3] * (temp[12] - temp[15])) - (m_perfusion[3] * Cb * (temp[12] - temp[13])) - (m_skin[15] * Cb * (temp[12] - temp[15]))) / self._cap[12],
            # node 13
            ((ha[3] * (temp[12] - temp[13])) + (q[3] * Cb * (temp[45] - temp[13]))) / self._cap[13],
            # node 14
            ((hv[3] * (temp[12] - temp[14])) + ((5 * m_perfusion[21] + m_perfusion[7] + m_perfusion[5]) * Cb * (temp[22] - temp[14])) + (m_perfusion[3] * Cb * (temp[12] - temp[14])) + ((5 * (qava4 + m_skin[87]) + m_skin[31] + m_skin[23]) * Cb * (temp[89] - temp[14]))) / self._cap[14],
            # node 15
            (m_base[15] + (k_cr_sk[3] * (temp[12] - temp[15])) - qt[15] - e[15] + (m_skin[15] * Cb * (temp[12] - temp[15]))) / self._cap[15],
            # node 16
            (m_base[16] + w_work[16] + m_sh[16] - q_res[16] - (ha[4] * (temp[16] - temp[17])) - (hv[4] * (temp[16] - temp[18])) - (k_cr_sk[4] * (temp[16] - temp[19])) - (m_perfusion[4] * Cb * (temp[16] - temp[17])) - (m_skin[19] * Cb * (temp[16] - temp[19]))) / self._cap[16],
            # node 17
            ((ha[4] * (temp[16] - temp[17])) + (q[4] * Cb * (temp[9] - temp[17]))) / self._cap[17],
            # node 18
            ((hv[4] * (temp[16] - temp[18])) + ((5 * m_perfusion[20] + m_perfusion[6]) * Cb * (temp[10] - temp[18])) + (m_perfusion[4] * Cb * (temp[16] - temp[18]))) / self._cap[18],
            # node 19
            (m_base[19] + (ksuperficialvein[4] * (temp[88] - temp[19])) + (k_cr_sk[4] * (temp[16] - temp[19])) - qt[19] - e[19] + (m_skin[19] * Cb * (temp[16] - temp[19])) + (m_skin[19] * Cb * (temp[88] - temp[19]))) / self._cap[19],
            # node 20
            (m_base[20] + w_work[20] + m_sh[20] - q_res[20] - (ha[5] * (temp[20] - temp[21])) - (hv[5] * (temp[20] - temp[22])) - (k_cr_sk[5] * (temp[20] - temp[23])) - (m_perfusion[5] * Cb * (temp[20] - temp[21])) - (m_skin[23] * Cb * (temp[20] - temp[23]))) / self._cap[20],
            # node 21
            ((ha[5] * (temp[20] - temp[21])) + (q[5] * Cb * (temp[13] - temp[21]))) / self._cap[21],
            # node 22
            ((hv[5] * (temp[20] - temp[22])) + ((5 * m_perfusion[21] + m_perfusion[7]) * Cb * (temp[30] - temp[22])) + (m_perfusion[5] * Cb * (temp[20] - temp[22]))) / self._cap[22],
            # node 23
            (m_base[23] + (ksuperficialvein[5] * (temp[89] - temp[23])) + (k_cr_sk[5] * (temp[20] - temp[23])) - qt[23] - e[23] + (m_skin[23] * Cb * (temp[20] - temp[23])) + (m_skin[23] * Cb * (temp[89] - temp[23]))) / self._cap[23],
            # node 24
            (m_base[24] + w_work[24] + m_sh[24] - q_res[24] - (ha[6] * (temp[24] - temp[25])) - (hv[6] * (temp[24] - temp[26])) - (k_cr_sk[6] * (temp[24] - temp[27])) - (m_perfusion[6] * Cb * (temp[24] - temp[25])) - (m_skin[27] * Cb * (temp[24] - temp[27]))) / self._cap[24],
            # node 25
            ((ha[6] * (temp[24] - temp[25])) + (q[6] * Cb * (temp[17] - temp[25]))) / self._cap[25],
            # node 26
            ((hv[6] * (temp[24] - temp[26])) + ((5 * m_perfusion[20]) * Cb * (temp[82] - temp[26])) + (m_perfusion[6] * Cb * (temp[24] - temp[26]))) / self._cap[26],
            # node 27
            (m_base[27] + (ksuperficialvein[6] * (temp[90] - temp[27])) + (k_cr_sk[6] * (temp[24] - temp[27])) - qt[27] - e[27] + (m_skin[27] * Cb * (temp[24] - temp[27])) + (m_skin[27] * Cb * (temp[90] - temp[27]))) / self._cap[27],
            # node 28
            (m_base[28] + w_work[28] + m_sh[28] - q_res[28] - (ha[7] * (temp[28] - temp[29])) - (hv[7] * (temp[28] - temp[30])) - (k_cr_sk[7] * (temp[28] - temp[31])) - (m_perfusion[7] * Cb * (temp[28] - temp[29])) - (m_skin[31] * Cb * (temp[28] - temp[31]))) / self._cap[28],
            # node 29
            ((ha[7] * (temp[28] - temp[29])) + (q[7] * Cb * (temp[21] - temp[29]))) / self._cap[29],
            # node 30
            ((hv[7] * (temp[28] - temp[30])) + ((5 * m_perfusion[21]) * Cb * (temp[86] - temp[30])) + (m_perfusion[7] * Cb * (temp[28] - temp[30]))) / self._cap[30],
            # node 31
            (m_base[31] + (ksuperficialvein[7] * (temp[91] - temp[31])) + (k_cr_sk[7] * (temp[28] - temp[31])) - qt[31] - e[31] + (m_skin[31] * Cb * (temp[28] - temp[31])) + (m_skin[31] * Cb * (temp[91] - temp[31]))) / self._cap[31],
            # node 32
            (m_base[32] + w_work[32] + m_sh[32] - q_res[32] - (ha[8] * (temp[32] - temp[33])) - (hv[8] * (temp[32] - temp[34])) - (k_cr_sk[8] * (temp[32] - temp[35])) - (m_perfusion[8] * Cb * (temp[32] - temp[33])) - (m_skin[35] * Cb * (temp[32] - temp[35]))) / self._cap[32],
            # node 33
            (ha[8] * (temp[32] - temp[33])) / self._cap[33],
            # node 34
            ((hv[8] * (temp[32] - temp[34])) + ((m_perfusion[0] + m_skin[3]) * Cb * (temp[2] - temp[34])) + ((m_perfusion[1] + m_skin[7]) * Cb * (temp[6] - temp[34])) + ((5 * m_perfusion[20] + m_perfusion[6] + m_perfusion[4] + m_perfusion[2] + m_perfusion[9] + 5 * (qava3 + m_skin[83]) + m_skin[27] + m_skin[19] + m_skin[11] + m_skin[39]) * Cb * (temp[38] - temp[34])) + ((5 * m_perfusion[21] + m_perfusion[7] + m_perfusion[5] + m_perfusion[3] + m_perfusion[11] + 5 * (qava4 + m_skin[87]) + m_skin[31] + m_skin[23] + m_skin[15] + m_skin[47]) * Cb * (temp[46] - temp[34])) + ((m_perfusion[12] + m_perfusion[13] + m_perfusion[14] + m_perfusion[15] + m_perfusion[16] + m_perfusion[17] + m_perfusion[18] + m_perfusion[19] + m_perfusion[10] + qava1 + qava2 + m_skin[79] + m_skin[75] + m_skin[71] + m_skin[67] + m_skin[63] + m_skin[59] + m_skin[55] + m_skin[51] + m_skin[43]) * Cb * (temp[42] - temp[34]))) / self._cap[34],
            # node 35
            (m_base[35] + (k_cr_sk[8] * (temp[32] - temp[35])) - qt[35] - e[35] + (m_skin[35] * Cb * (temp[32] - temp[35]))) / self._cap[35],
            # node 36
            (m_base[36] + w_work[36] + m_sh[36] - q_res[36] - (ha[9] * (temp[36] - temp[37])) - (hv[9] * (temp[36] - temp[38])) - (k_cr_sk[9] * (temp[36] - temp[39])) - (m_perfusion[9] * Cb * (temp[36] - temp[37])) - (m_skin[39] * Cb * (temp[36] - temp[39]))) / self._cap[36],
            # node 37
            ((ha[9] * (temp[36] - temp[37])) + (q[9] * Cb * (temp[33] - temp[37]))) / self._cap[37],
            # node 38
            ((hv[9] * (temp[36] - temp[38])) + ((5 * m_perfusion[20] + m_perfusion[6] + m_perfusion[4] + m_perfusion[2]) * Cb * (temp[10] - temp[38])) + (m_perfusion[9] * Cb * (temp[36] - temp[38])) + ((5 * (qava3 + m_skin[83]) + m_skin[27] + m_skin[19] + m_skin[11]) * Cb * (temp[10] - temp[38]))) / self._cap[38],
            # node 39
            (m_base[39] + (k_cr_sk[9] * (temp[36] - temp[39])) - qt[39] - e[39] + (m_skin[39] * Cb * (temp[36] - temp[39]))) / self._cap[39],
            # node 40
            (m_base[40] + w_work[40] + m_sh[40] - q_res[40] - (ha[10] * (temp[40] - temp[41])) - (hv[10] * (temp[40] - temp[42])) - (k_cr_sk[10] * (temp[40] - temp[43])) - (m_perfusion[10] * Cb * (temp[40] - temp[41])) - (m_skin[43] * Cb * (temp[40] - temp[43]))) / self._cap[40],
            # node 41
            ((ha[10] * (temp[40] - temp[41])) + (q[10] * Cb * (temp[33] - temp[41]))) / self._cap[41],
            # node 42
            ((hv[10] * (temp[40] - temp[42])) + ((m_perfusion[19] + m_perfusion[17] + m_perfusion[15] + m_perfusion[13] + qava2 + m_skin[79] + m_skin[71] + m_skin[63] + m_skin[55]) * Cb * (temp[54] - temp[42])) + ((m_perfusion[18] + m_perfusion[16] + m_perfusion[14] + m_perfusion[12] + qava1 + m_skin[75] + m_skin[67] + m_skin[59] + m_skin[51]) * Cb * (temp[50] - temp[42])) + (m_perfusion[10] * Cb * (temp[40] - temp[42]))) / self._cap[42],
            # node 43
            (m_base[43] + (k_cr_sk[10] * (temp[40] - temp[43])) - qt[43] - e[43] + (m_skin[43] * Cb * (temp[40] - temp[43]))) / self._cap[43],
            # node 44
            (m_base[44] + w_work[44] + m_sh[44] - q_res[44] - (ha[11] * (temp[44] - temp[45])) - (hv[11] * (temp[44] - temp[46])) - (k_cr_sk[11] * (temp[44] - temp[47])) - (m_perfusion[11] * Cb * (temp[44] - temp[45])) - (m_skin[47] * Cb * (temp[44] - temp[47]))) / self._cap[44],
            # node 45
            ((ha[11] * (temp[44] - temp[45])) + (q[11] * Cb * (temp[33] - temp[45]))) / self._cap[45],
            # node 46
            ((hv[11] * (temp[44] - temp[46])) + ((5 * m_perfusion[21] + m_perfusion[7] + m_perfusion[5] + m_perfusion[3]) * Cb * (temp[14] - temp[46])) + ((5 * (qava4 + m_skin[87]) + m_skin[31] + m_skin[23] + m_skin[15]) * Cb * (temp[14] - temp[46])) + (m_perfusion[11] * Cb * (temp[44] - temp[46]))) / self._cap[46],
            # node 47
            (m_base[47] + (k_cr_sk[11] * (temp[44] - temp[47])) - qt[47] - e[47] + (m_skin[47] * Cb * (temp[44] - temp[47]))) / self._cap[47],
            # node 48
            (m_base[48] + w_work[48] + m_sh[48] - q_res[48] - (ha[12] * (temp[48] - temp[49])) - (hv[12] * (temp[48] - temp[50])) - (k_cr_sk[12] * (temp[48] - temp[51])) - (m_perfusion[12] * Cb * (temp[48] - temp[49])) - (m_skin[51] * Cb * (temp[48] - temp[51]))) / self._cap[48],
            # node 49
            ((ha[12] * (temp[48] - temp[49])) + (q[12] * Cb * (temp[41] - temp[49]))) / self._cap[49],
            # node 50
            ((hv[12] * (temp[48] - temp[50])) + ((m_perfusion[18] + m_perfusion[16] + m_perfusion[14]) * Cb * (temp[58] - temp[50])) + ((qava1 + m_skin[75] + m_skin[67] + m_skin[59]) * Cb * (temp[58] - temp[50])) + (m_perfusion[12] * Cb * (temp[48] - temp[50]))) / self._cap[50],
            # node 51
            (m_base[51] + (k_cr_sk[12] * (temp[48] - temp[51])) - qt[51] - e[51] + (m_skin[51] * Cb * (temp[48] - temp[51]))) / self._cap[51],
            # node 52
            (m_base[52] + w_work[52] + m_sh[52] - q_res[52] - (ha[13] * (temp[52] - temp[53])) - (hv[13] * (temp[52] - temp[54])) - (k_cr_sk[13] * (temp[52] - temp[55])) - (m_perfusion[13] * Cb * (temp[52] - temp[53])) - (m_skin[55] * Cb * (temp[52] - temp[55]))) / self._cap[52],
            # node 53
            ((ha[13] * (temp[52] - temp[53])) + (q[13] * Cb * (temp[41] - temp[53]))) / self._cap[53],
            # node 54
            ((hv[13] * (temp[52] - temp[54])) + ((m_perfusion[19] + m_perfusion[17] + m_perfusion[15]) * Cb * (temp[62] - temp[54])) + ((qava2 + m_skin[79] + m_skin[71] + m_skin[63]) * Cb * (temp[62] - temp[54])) + (m_perfusion[13] * Cb * (temp[52] - temp[54]))) / self._cap[54],
            # node 55
            (m_base[55] + (k_cr_sk[13] * (temp[52] - temp[55])) - qt[55] - e[55] + (m_skin[55] * Cb * (temp[52] - temp[55]))) / self._cap[55],
            # node 56
            (m_base[56] + w_work[56] + m_sh[56] - q_res[56] - (ha[14] * (temp[56] - temp[57])) - (hv[14] * (temp[56] - temp[58])) - (k_cr_sk[14] * (temp[56] - temp[59])) - (m_perfusion[14] * Cb * (temp[56] - temp[57])) - (m_skin[59] * Cb * (temp[56] - temp[59]))) / self._cap[56],
            # node 57
            ((ha[14] * (temp[56] - temp[57])) + (q[14] * Cb * (temp[49] - temp[57]))) / self._cap[57],
            # node 58
            ((hv[14] * (temp[56] - temp[58])) + ((m_perfusion[18] + m_perfusion[16]) * Cb * (temp[66] - temp[58])) + ((qava1 + m_skin[75] + m_skin[67]) * Cb * (temp[92] - temp[58])) + (m_perfusion[14] * Cb * (temp[56] - temp[58]))) / self._cap[58],
            # node 59
            (m_base[59] + (k_cr_sk[14] * (temp[56] - temp[59])) - qt[59] - e[59] + (m_skin[59] * Cb * (temp[56] - temp[59]))) / self._cap[59],
            # node 60
            (m_base[60] + w_work[60] + m_sh[60] - q_res[60] - (ha[15] * (temp[60] - temp[61])) - (hv[15] * (temp[60] - temp[62])) - (k_cr_sk[15] * (temp[60] - temp[63])) - (m_perfusion[15] * Cb * (temp[60] - temp[61])) - (m_skin[63] * Cb * (temp[60] - temp[63]))) / self._cap[60],
            # node 61
            ((ha[15] * (temp[60] - temp[61])) + (q[15] * Cb * (temp[53] - temp[61]))) / self._cap[61],
            # node 62
            ((hv[15] * (temp[60] - temp[62])) + ((m_perfusion[19] + m_perfusion[17]) * Cb * (temp[70] - temp[62])) + ((qava2 + m_skin[79] + m_skin[71]) * Cb * (temp[93] - temp[62])) + (m_perfusion[15] * Cb * (temp[60] - temp[62]))) / self._cap[62],
            # node 63
            (m_base[63] + (k_cr_sk[15] * (temp[60] - temp[63])) - qt[63] - e[63] + (m_skin[63] * Cb * (temp[60] - temp[63]))) / self._cap[63],
            # node 64
            (m_base[64] + w_work[64] + m_sh[64] - q_res[64] - (ha[16] * (temp[64] - temp[65])) - (hv[16] * (temp[64] - temp[66])) - (k_cr_sk[16] * (temp[64] - temp[67])) - (m_perfusion[16] * Cb * (temp[64] - temp[65])) - (m_skin[67] * Cb * (temp[64] - temp[67]))) / self._cap[64],
            # node 65
            ((ha[16] * (temp[64] - temp[65])) + (q[16] * Cb * (temp[57] - temp[65]))) / self._cap[65],
            # node 66
            ((hv[16] * (temp[64] - temp[66])) + (m_perfusion[18] * Cb * (temp[74] - temp[66])) + (m_perfusion[16] * Cb * (temp[64] - temp[66]))) / self._cap[66],
            # node 67
            (m_base[67] + (ksuperficialvein[16] * (temp[92] - temp[67])) + (k_cr_sk[16] * (temp[64] - temp[67])) - qt[67] - e[67] + (m_skin[67] * Cb * (temp[64] - temp[67])) + (m_skin[67] * Cb * (temp[92] - temp[67]))) / self._cap[67],
            # node 68
            (m_base[68] + w_work[68] + m_sh[68] - q_res[68] - (ha[17] * (temp[68] - temp[69])) - (hv[17] * (temp[68] - temp[70])) - (k_cr_sk[17] * (temp[68] - temp[71])) - (m_perfusion[17] * Cb * (temp[68] - temp[69])) - (m_skin[71] * Cb * (temp[68] - temp[71]))) / self._cap[68],
            # node 69
            ((ha[17] * (temp[68] - temp[69])) + (q[17] * Cb * (temp[61] - temp[69]))) / self._cap[69],
            # node 70
            ((hv[17] * (temp[68] - temp[70])) + (m_perfusion[19] * Cb * (temp[78] - temp[70])) + (m_perfusion[17] * Cb * (temp[68] - temp[70]))) / self._cap[70],
            # node 71
            (m_base[71] + (ksuperficialvein[17] * (temp[93] - temp[71])) + (k_cr_sk[17] * (temp[68] - temp[71])) - qt[71] - e[71] + (m_skin[71] * Cb * (temp[68] - temp[71])) + (m_skin[71] * Cb * (temp[93] - temp[71]))) / self._cap[71],
            # node 72
            (m_base[72] + w_work[72] + m_sh[72] - q_res[72] - (ha[18] * (temp[72] - temp[73])) - (hv[18] * (temp[72] - temp[74])) - (k_cr_sk[18] * (temp[72] - temp[75])) - ((m_perfusion[18] - qava1 - m_skin[83]) * Cb * (temp[72] - temp[73])) - (m_skin[75] * Cb * (temp[72] - temp[75]))) / self._cap[72],
            # node 73
            ((ha[18] * (temp[72] - temp[73])) + (q[18] * Cb * (temp[65] - temp[73])) - (qava1 * Cb * (temp[73] - temp[94]))) / self._cap[73],
            # node 74
            ((hv[18] * (temp[72] - temp[74])) + (m_perfusion[18] * Cb * (temp[72] - temp[74]))) / self._cap[74],
            # node 75
            (m_base[75] + (ksuperficialvein[18] * (temp[94] - temp[75])) + (k_cr_sk[18] * (temp[72] - temp[75])) - qt[75] - e[75] + (m_skin[75] * Cb * (temp[72] - temp[75])) + (m_skin[75] * Cb * (temp[94] - temp[75]))) / self._cap[75],
            # node 76
            (m_base[76] + w_work[76] + m_sh[76] - q_res[76] - (ha[19] * (temp[76] - temp[77])) - (hv[19] * (temp[76] - temp[78])) - (k_cr_sk[19] * (temp[76] - temp[79])) - ((m_perfusion[19] - qava2 - m_skin[79]) * Cb * (temp[76] - temp[77])) - (m_skin[79] * Cb * (temp[76] - temp[79]))) / self._cap[76],
            # node 77
            ((ha[19] * (temp[76] - temp[77])) + (q[19] * Cb * (temp[69] - temp[77])) - (qava2 * Cb * (temp[77] - temp[95]))) / self._cap[77],
            # node 78
            ((hv[19] * (temp[76] - temp[78])) + (m_perfusion[19] * Cb * (temp[76] - temp[78]))) / self._cap[78],
            # node 79
            (m_base[79] + (ksuperficialvein[19] * (temp[95] - temp[79])) + (k_cr_sk[19] * (temp[76] - temp[79])) - qt[79] - e[79] + (m_skin[79] * Cb * (temp[76] - temp[79])) + (m_skin[79] * Cb * (temp[95] - temp[79]))) / self._cap[79],
            # node 80
            (m_base[80] + w_work[80] + m_sh[80] - q_res[80] - (ha[20] * (temp[80] - temp[81])) - (hv[20] * (temp[80] - temp[82])) - (k_cr_sk[20] * (temp[80] - temp[83])) - (m_perfusion[20] * Cb * (temp[80] - temp[81])) - (m_skin[83] * Cb * (temp[80] - temp[83]))) / self._cap[80],
            # node 81
            ((ha[20] * (temp[80] - temp[81])) + ((0.2 * q[6]) * Cb * (temp[25] - temp[81])) + (qava3 * Cb * (temp[96] - temp[81]))) / self._cap[81],
            # node 82
            ((hv[20] * (temp[80] - temp[82])) + (m_perfusion[20] * Cb * (temp[80] - temp[82]))) / self._cap[82],
            # node 83
            (m_base[83] + (ksuperficialvein[20] * (temp[96] - temp[83])) + (k_cr_sk[20] * (temp[80] - temp[83])) - qt[83] - e[83] + (m_skin[83] * Cb * (temp[80] - temp[83])) + (m_skin[83] * Cb * (temp[96] - temp[83]))) / self._cap[83],
            # node 84
            (m_base[84] + w_work[84] + m_sh[84] - q_res[84] - (ha[21] * (temp[84] - temp[85])) - (hv[21] * (temp[84] - temp[86])) - (k_cr_sk[21] * (temp[84] - temp[87])) - (m_perfusion[21] * Cb * (temp[84] - temp[85])) - (m_skin[87] * Cb * (temp[84] - temp[87]))) / self._cap[84],
            # node 85
            ((ha[21] * (temp[84] - temp[85])) + ((0.2 * q[7]) * Cb * (temp[29] - temp[85])) + (qava4 * Cb * (temp[97] - temp[85]))) / self._cap[85],
            # node 86
            ((hv[21] * (temp[84] - temp[86])) + (m_perfusion[21] * Cb * (temp[84] - temp[86]))) / self._cap[86],
            # node 87
            (m_base[87] + (ksuperficialvein[21] * (temp[97] - temp[87])) + (k_cr_sk[21] * (temp[84] - temp[87])) - qt[87] - e[87] + (m_skin[87] * Cb * (temp[84] - temp[87])) + (m_skin[87] * Cb * (temp[97] - temp[87]))) / self._cap[87],
            # 浅静脉节点
            # node 88
            ((ksuperficialvein[4] * (temp[19] - temp[88])) + ((5 * (qava3 + m_skin[83]) + m_skin[27]) * Cb * (temp[90] - temp[88])) + (m_skin[19] * Cb * (temp[19] - temp[88]))) / self._cap[88],
            # node 89
            ((ksuperficialvein[5] * (temp[23] - temp[89])) + ((5 * (qava4 + m_skin[87]) + m_skin[31]) * Cb * (temp[91] - temp[89])) + (m_skin[23] * Cb * (temp[23] - temp[89]))) / self._cap[89],
            # node 90
            ((ksuperficialvein[6] * (temp[27] - temp[90])) + (5 * (qava3 + m_skin[83]) * Cb * (temp[96] - temp[90])) + (m_skin[27] * Cb * (temp[27] - temp[90]))) / self._cap[90],
            # node 91
            ((ksuperficialvein[7] * (temp[31] - temp[91])) + (5 * (qava4 + m_skin[87]) * Cb * (temp[97] - temp[91])) + (m_skin[31] * Cb * (temp[31] - temp[91]))) / self._cap[91],
            # node 92
            ((ksuperficialvein[16] * (temp[67] - temp[92])) + ((qava1 + m_skin[75]) * Cb * (temp[94] - temp[92])) + (m_skin[67] * Cb * (temp[67] - temp[92]))) / self._cap[92],
            # node 93
            ((ksuperficialvein[17] * (temp[71] - temp[93])) + ((qava2 + m_skin[79]) * Cb * (temp[95] - temp[93])) + (m_skin[71] * Cb * (temp[71] - temp[93]))) / self._cap[93],
            # node 94
            ((ksuperficialvein[18] * (temp[75] - temp[94])) + (qava1 * Cb * (temp[73] - temp[94])) + (m_skin[75] * Cb * (temp[75] - temp[94]))) / self._cap[94],
            # node 95
            ((ksuperficialvein[19] * (temp[79] - temp[95])) + (qava2 * Cb * (temp[77] - temp[95])) + (m_skin[79] * Cb * (temp[79] - temp[95]))) / self._cap[95],
            # node 96
            ((ksuperficialvein[20] * (temp[83] - temp[96])) + (qava3 * Cb * (temp[81] - temp[96])) + (m_skin[83] * Cb * (temp[83] - temp[96]))) / self._cap[96],
            # node 97
            ((ksuperficialvein[21] * (temp[87] - temp[97])) + (qava4 * Cb * (temp[85] - temp[97])) + (m_skin[87] * Cb * (temp[87] - temp[97]))) / self._cap[97],

        ])

        return d_temp

    def basal_met(self, height=1.72, weight=74.43, age=20,
                  sex="male", equation="harris-benedict"):
        """
        Calculate basal metabolic rate [W].

        Parameters
        ----------
        height : float, optional
            Body height [m]. The default is 1.72.
        weight : float, optional
            Body weight [kg]. The default is 74.43.
        age : float, optional
            Age [years]. The default is 20.
        sex : str, optional
            Choose male or female. The default is "male".
        equation : str, optional
            Choose harris-benedict or ganpule. The default is "harris-benedict".

        Returns
        -------
        BMR : float
            Basal metabolic rate [W].

        """

        if equation == "harris-benedict":
            if sex == "male":
                bmr = 88.362 + 13.397 * weight + 500.3 * height - 5.677 * age
            else:
                bmr = 447.593 + 9.247 * weight + 479.9 * height - 4.330 * age

        elif equation == "harris-benedict_origin":
            if sex == "male":
                bmr = 66.4730 + 13.7516 * weight + 500.33 * height - 6.7550 * age
            else:
                bmr = 655.0955 + 9.5634 * weight + 184.96 * height - 4.6756 * age

        elif equation == "japanese" or equation == "ganpule":
            # Ganpule et al., 2007, https://doi.org/10.1038/sj.ejcn.1602645
            if sex == "male":
                bmr = 0.0481 * weight + 2.34 * height - 0.0138 * age - 0.4235
            else:
                bmr = 0.0481 * weight + 2.34 * height - 0.0138 * age - 0.9708
            bmr *= 1000 / 4.186

        bmr *= 0.048  # [kcal/day] to [W]

        return bmr





    # -----------------------------------------------------------------------------------------------------------------------
    # Setter and Getter
    # -----------------------------------------------------------------------------------------------------------------------
    @property
    def Ta(self):
        return self._ta

    @Ta.setter
    def Ta(self, value):
        self._ta = value

    @property
    def Tr(self):
        return self._tr

    @Ta.setter
    def Tr(self, value):
        self._tr = value

    @property
    def Rh(self):
        return self._rh

    @Ta.setter
    def Rh(self, value):
        self._rh = value

    @property
    def V(self):
        return self._va

    @Ta.setter
    def V(self, value):
        self._va = value

    @property
    def Met(self):
        return self._met

    @Ta.setter
    def Met(self, value):
        self._met = value

    @property
    def Altitude(self):
        return self._altitude

    @Altitude.setter
    def Altitude(self, value):
        self._altitude = value

    @property
    def Pt(self):
        return self._pt

    @Pt.setter
    def Pt(self, value):
        self._pt = value

    @property
    def Solarfixtr(self):
        return self._solarfixtr

    @Solarfixtr.setter
    def Solarfixtr(self, value):
        self._solarfixtr = value

    @property
    def Idir(self):
        return self._i_dir

    @Idir.setter
    def Idir(self, value):
        self._i_dir = value
