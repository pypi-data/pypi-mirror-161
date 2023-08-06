# -*- coding: utf-8 -*-

import pickle
import json
import os
import numpy as np
import requests
from bs4 import BeautifulSoup as bs
import re
from time import time, sleep
import random

from sympy import true


class Account():
     
    def __init__(self, username, password, frist_time_login=False, exp=None, full_expr_record=False):
        # full_expr_record False--覆盖 True--追加        
        cloud_url = 'https://quantumcomputer.ac.cn/pyRequest'
        self.username = username
        self.password = password
        if exp is None:
            self.exp = {}
        else:
            self.exp = exp
        self.full_expr_record = full_expr_record
        self.base_url =  f'{cloud_url}?username={username}&password={password}'
        if frist_time_login:
            self.login = self.log_in()  
        
    def log_in(self):
        """
        Authenticate username and password and return user credit

        Returns
        -------
        log in state, 0 means pass authentication, 1 means failed

        """
        h = requests.get(url=self.base_url)
        return self.check_login(h, True, True)

    def check_login(self, h, flag=False, check_point=False):
        """
            check user login information.
        """
        content = bs(h.text, "html.parser")
        token_element = content.find_all('p', id='loginMsg')
        user_point_element = content.find_all('p', id='integral')
        ret = 0
        for e in token_element:
            token = str(e).split('登录返回的结果---&gt;')[1].split('</p>')[0]  # 登录失败，直接返回
            token = eval(token)
            if 'msg' in token:
                ret = token.get('msg')
                print(ret)
                return 0
            else:
                return 1

        if check_point:
            for e in user_point_element:
                user_point = str(e).split('用户积分---&gt;')[1].split('</p>')[0]
                if '积分不足' in user_point:  # 积分标签中存在 积分不足 直接返回
                    print(f'积分不足!')
                    return 0
                else:
                    if flag:
                        print(f'您已成功登入云平台，您账号里现在有{user_point}积分')
                    return 1           

    def create_experiment(self, exp_name):
        """create experiment

        Args:
            url (string): request the address

        Returns:
            0--失败, 非0成功
        """
        url = self.base_url + f'&expName={exp_name}'
        h = requests.get(url=url)
        content = bs(h.text, "html.parser")
        ret_check_login = self.check_login(h)
        if not ret_check_login:
            return ret_check_login

        create_experiment_element = content.find_all('p', id='addExp')
        for e in create_experiment_element:
            lab_id = str(e).split('新建实验返回的结果---&gt;')[1].split('</p>')[0]
            if 'msg' in lab_id:
                exp_result = eval(lab_id)
                if isinstance(exp_result, dict):
                    msg = exp_result.get('msg')
                    print(f'创建实验失败, {msg}')
                    return 0

            if not self.full_expr_record:
                self.exp = {}

            self.exp[lab_id] = {}
            self.exp[lab_id]['lab_name'] = exp_name
            return lab_id
        print("创建实验失败, 没有返回结果")
        return 0

    def save_experiment(self, lab_id, exp_data):
        """save experiment

        Args:
            url (string): request the addresslab_id

        Returns:
            0--失败, 非0成功

        异常情况：
            1.保存实验返回的结果-->{'code':500, 'msg': XXX}
            2.保存实验返回的结果-->  (多进程同时请求可能出现的情况)
            3.保存实验返回的结果-->exp_id,当前实验已保存
            4.保存实验返回的结果-->量子线路指令输入错误，请检查你的输入
        正常情况：
            1.保存实验返回的结果-->exp_id
        """
        exp_data = self.get_experiment_data(exp_data.upper())
        url = self.base_url + f'&expId={lab_id}&expData={exp_data}'
        h = requests.get(url=url)
        content = bs(h.text, "html.parser")
        ret_check_login = self.check_login(h)
        if not ret_check_login:
            return ret_check_login
        
        save_result_element = content.find_all('p', id='saveExp')
        for e in save_result_element:
            save_result = str(e).split('保存实验返回的结果---&gt;')[1].split('\n  </p>')[0]
            try:
                save_exp = eval(save_result)
                if 'code' in save_exp:
                    print(f"保存实验失败, {save_exp.get('msg')}")
                    return 0
                else:
                    print(f'保存实验失败, 返回信息中不存在code')
                    return 0
            except:
                if len(save_result.split(',')) > 1:
                    print(f"保存实验失败, {save_result.split(',')[1]}")
                    return 0
                else:
                    if u'\u4e00' <= save_result <= u'\u9fff':
                        print(f'保存实验失败, {save_result}')
                        return 0
                    
                    if lab_id in self.exp:
                        if self.full_expr_record and 'exp_detail' in self.exp[lab_id]: # 追加并且exp_detail存在于字典中
                            self.exp[lab_id]['exp_detail'][save_result] = {'version_name': save_result, 'run_detail': []}
                        else: # 覆盖，不管是full_expr_record为True还是exp_detail不存在于字典中，都需要重新定义exp_detail
                            exp_detail = {}
                            exp_detail[save_result] = {'version_name': save_result, 'run_detail': []}
                            self.exp[lab_id]['exp_detail'] = exp_detail                                
                    else:
                        print('保存实验版本编号无法保存, 信息中不存在当前实验集id')

                    return save_result

    def run_experiment(self, exp_id, num_shots=12000):
        """run experiment

        Args:
            url (string): request the address

        Returns:
            0--失败, 非0成功
        """
        url = self.base_url + f'&expDetailId={exp_id}&shots={num_shots}'
        h = requests.get(url=url)
        content = bs(h.text, "html.parser")
        ret_check_login = self.check_login(h, check_point=True)
        if not ret_check_login:
            return ret_check_login
        
        run_result_element = content.find_all('p', id='runExp')
        for e in run_result_element:
            run_result = str(e).split('运行实验返回的结果---&gt;')[1].split('</p>')[0]
            try:
                run_result = int(run_result)

                # 根据exp_id查询初lab_id
                lab_id = None
                for lab in self.exp:
                    exp_detail_dir = self.exp[lab].get('exp_detail', None)
                    if exp_detail_dir:
                        if exp_id in exp_detail_dir:
                            lab_id = lab
                
                if lab_id:
                    if self.full_expr_record: # 追加
                        self.exp[lab_id]['exp_detail'][exp_id]['run_detail'].append(run_result)
                    else:
                        self.exp[lab_id]['exp_detail'][exp_id]['run_detail'] = [run_result]
                else:
                    print('提交实验后的查询编号无法保存，信息中不存在当前实验集id活实验版本id')

                return run_result
            except:
                print(f'运行实验失败, {run_result}')
                return 0

    def query_experiment(self, query_id, max_wait_time=60):
        """query experiment

        Args:
            query_id (int): 查询id
            max_wait_time(int): 最大等待时间

        Returns:
            0--失败, 非0成功
        """
        t0 = time()
        while time()-t0 < max_wait_time:
            try:
                url = self.base_url + f'&download={query_id}'
                h = requests.get(url=url)
                content = bs(h.text, "html.parser")
                ret_check_login = self.check_login(h)
                if not ret_check_login:
                    return ret_check_login
                
                query_result_element = content.find_all('p', id='downloadExp')
                for e in query_result_element:
                    query_result = str(e).split('下载实验返回的结果---&gt;')[1].split('  </p>')[0]
                    query_exp = eval(query_result)
                    if 'code' in query_exp:
                        msg = query_exp.get('msg')
                    else:
                        return query_exp
            except:
                continue
            sleep_time = random.randint(0, 15)*0.3+round(random.uniform(0,1.5), 2)
            print(f'查询实验结果请等待: {sleep_time}')
            sleep(sleep_time)
        print(f'查询实验结果失败, {msg}')
        return 0

    def submit_job(self, circuit=None, exp_name='exp0', parameters=None, values=None, num_shots=12000, lab_id=None, exp_id=None):
        """[summary]

        Args:
            circuit_list ([type]): [description]
            exp_name (str, optional): [description]. Defaults to 'exp0'.
            parameters ([type], optional): [description]. Defaults to None.
            values ([type], optional): [description]. Defaults to None.
            num_shots (int, optional): [description]. Defaults to 12000.

        Returns
        -------
        error message : string Error message 
            ("你当前正在执行的任务已超过上限, 请待任务结束后再次提交运行",
             "登录失败请检查账户密码是否正确",
             "量子线路指令输入错误, 请检查您的输入",
             "实验任务排队已达上限",
             "线路含有2个参数, 您提供了1个参数值",
             "线路含有参数[*,*,*], 请提供相应的参数值",
             "线路含有*个参数, 您提供了*个参数",
             "线路中的参数与您输入的参数名称不符")
        0--失败, 非0成功
        {
                'lab_id_1': {
                    'exp_name': exp0', 
                    'exp_detail': 
                        {
                            'exp_id_1':{'version_name': 'v1', 'run_detail': ['query_id1', 'query_id2']},
                            'exp_id_2':{'version_name': 'v2', 'run_detail': ['query_id1', 'query_id2']}
                        },
                    ...
                },
            ...
        }
        """
        try:
            if circuit:
                circuit = self.assign_parameters(circuit.upper(), parameters, values)
                if not circuit:
                    print('无法为线路赋值，请检查线路，参数和参数值之后重试')
                    return 0

            flag = True
            if circuit and exp_id:
                # circuit 与 exp_id 冲突，不执行
                print('线路和实验版本冲突，无法执行')
                return 0
            elif circuit and lab_id:
                # 查看lab_id在字典中是否存在
                if lab_id not in self.exp:
                    print(f'{lab_id}不存在当前字典中')
                    return 0
                # 如存在save--run
            elif circuit:
                # 按照lab_name，# create--save--run
                lab_id = self.create_experiment(exp_name)
                if not lab_id:
                    return 0
            elif exp_id and lab_id:
                flag = False
                # 检查字典lab_id和exp_id是否匹配
                # 匹配成功 run
                if lab_id not in self.exp or exp_id not in self.exp.get(lab_id, {}).get('exp_detail', {}):
                    print(f'输入的实验版本{exp_id}不属于该实验集{lab_id}下')
                    return 0
            elif exp_id:
                # 查看字典中，是否存在exp_id
                # 存在 run
                for item in self.exp:
                    if exp_id in self.exp.get(item, {}).get('exp_detail', {}):
                        flag = False
                if flag:
                    print(f'找不到实验版本对应的实验集')
                    return 0
            else:
                print('没有待创建或已创建的实验可以执行')
                return 0

            if flag:
                exp_id = self.save_experiment(lab_id, circuit)
                if not exp_id:
                    return 0

            # 提交实验
            query_id = self.run_experiment(exp_id, num_shots)
            if query_id:
                return query_id
            else:
                return 0
        
        except:
            print('提交实验失败, 请检查参数信息')
        
        return 0

    def assign_parameters(self, circuit, parameters, values):
        """
        Check if the number of parameters, values match the circuit definition

        Parameters
        ----------
        circuit : string, QCIS circuit definition with or without parameter place holder
        parameters : list or ndarray of strings, parameters to be filled
        values : list or ndarray of floats, values to be assigned

        Returns
        -------
        circuit : circuit with parameters replaced by values or empty string
            empty string occurs when errors prevents parameters to be assigned
        """
        
        p = re.compile(r'\{(\w+)\}')
        circuit_parameters = p.findall(circuit)
        if circuit_parameters:
            
            # 如果values为整数或浮点数，改为列表格式##########################################################
            if isinstance(values, (float, int)):
                values = [values]
            # 如果parameters为字符格式，改为列表格式#########################################################
            if isinstance(parameters, str):
                parameters = [parameters]
            # 将所有parameter变为大写， 否则set(parameters) != set(circuit_parameters) 不通过 ###############
            parameters = [p.upper() for p in parameters]
                
            
            if not values:    
                error_message = f'线路含有参数{circuit_parameters}, 请提供相应的参数值'
                print(error_message)
                return ''
            
            else:
                if len(circuit_parameters) != len(values):
                    error_message = f'线路含有{len(circuit_parameters)}个参数, 您提供了{len(values)}个参数值'
                    print(error_message)
                    return ''
            
                elif parameters and len(circuit_parameters) != len(parameters):
                    error_message = f'线路含有{len(circuit_parameters)}个参数, 您提供了{len(parameters)}个参数'
                    print(error_message)
                    return ''

                elif set(parameters) != set(circuit_parameters):
                    error_message = f'线路中的参数与您输入的参数名称不符'
                    print(error_message)
                else:
                    param_dic = {}
                    ############################# 这个转化可以删了 #########################################
                    #parameters_upper = [p.upper() for p in parameters]
                    for p, v in zip(parameters, values): 
                        param_dic[p] = v 
                    expData = circuit.format(**param_dic)
                    return expData
                
        elif parameters or values:
                error_message = f'线路定义中不含有参数，无法接受您输入的参数或参数值'
                print(error_message)
                return ''
        else:
            expData = circuit
            return expData
        
    def get_experiment_data(self, circuit):
        """
        Parse circuit description and generate experiment script and extract number
        of measured qubits

        Parameters
        ----------
        circuit : string, QCIS circuit 

        Returns
        -------
        expData : string, transformed circuit

        """
        #get gates from circuit
        gates_list = circuit.split('\n')
        gates_list_strip = [g.strip() for g in gates_list if g]
        gates_list_strip = [g for g in gates_list_strip if g]
        
        #transform circuit from QCIS to expData
        expData = ';'.join(gates_list_strip)
        return expData

    def load_exp_data(self, filepath='lab_info.json'):
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath, 'r') as f:
                exp = json.load(f)
                # exp = pickle.load(f)
            return exp
        print('文件不存在或者文件内容为空')

    def save_exp_data(self, filename='lab_info.json', mode='w'):
        if self.exp:
            with open(filename, mode) as f:
                json.dump(self.exp, f)
                # pickle.dump(self.exp, f)

if __name__ == '__main__':
    username = 'lixiaorong'
    password = '12345678'
    # username = 'test03'
    # password = '123456'
    account = Account(username, password, frist_time_login=True, full_expr_record=True)

    if account.login:        
        circuit = '''
            RZ Q1 -0.494530670352271
            RX Q1 -1.6604650905638
            H Q1
            RZ Q2 -0.155487943732828
            RX Q2 -0.0137010734993274
            H Q2
            RZ Q3 -0.0228764841311865
            RX Q3 -0.0473825532042785
            H Q3
            RZ Q4 -0.788912927499223
            RX Q4 -0.64895063114411
            H Q4
            RX Q5 -1.69226448904139
            H Q5
            M Q1
            M Q2
            M Q3
            M Q4
            M Q5
        '''

        # submit_job
        
        # exp_data = account.load_exp_data()
        # account.exp = exp_data

        query_id = account.submit_job(circuit, exp_name='test1_3')
        if query_id:
            print(account.query_experiment(query_id, max_wait_time=20))

        query_id = account.submit_job(circuit, exp_name='test2_3')
        if query_id:
            print(account.query_experiment(query_id, max_wait_time=20))

        circuit1 = """
            M Q1
            Y Q3
            M Q3
            H Q2
        """
        query_id = account.submit_job(circuit1, lab_id=list(account.exp.keys())[0], exp_name='test3')
        if query_id:
            print(account.query_experiment(query_id, max_wait_time=20))

        lab_id = list(account.exp.keys())[0]
        exp_id = list(account.exp.get(lab_id).get('exp_detail').keys())[0]
        query_id = account.submit_job(lab_id=lab_id, exp_id=exp_id)
        if query_id:
            print(account.query_experiment(query_id, max_wait_time=20))

        account.save_exp_data()   

        # 分步测试
        # lab_id = account.create_experiment('test_exp')
        # if lab_id:
        #     exp_id = account.save_experiment(lab_id, circuit)
        #     if exp_id:
        #         query_id = account.run_experiment(exp_id)
        #         if query_id:
        #             print(account.query_experiment(query_id, max_wait_time=10))

        