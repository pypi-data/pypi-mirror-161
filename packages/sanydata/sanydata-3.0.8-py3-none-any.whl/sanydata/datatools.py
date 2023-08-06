#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Team : SANY Heavy Energy DataTeam
# @Time    : 2020/8/05 17:37 下午
# @Author  : THao

import io
import os
import json
import time
import sqlite3
import datetime
import inspect
import multiprocessing
import grpc
import pandas as pd
import pyarrow.parquet as pq

from sanydata import model_data_message_pb2, model_data_message_pb2_grpc
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from utils.file_operation import GetTargetFile, GetCosToken, GetDeployment
from inspect import isfunction
from elasticsearch import Elasticsearch
from hdfs import Client as HdfsClient
import pyarrow as pa

query = gql("""
                query{
                turbineAllSqlite(type:""){
                turbineId
                innerTurbineName
                typeId
                typeName
                innerTurbineType
                innerPlatForm
                ratedPower
                etlType
                Pch2A_Acc
                farmId
                pinyinCode
                farmName
                curveId
                isDynamic
                powerCurve
                ownerTurbineName
                ownerId
                ownerEasyName
                ownerName
                farmCode
                projectName
                country
                province
                city
                address
                farmLongitude
                farmLatitude
                capacity
                installedNum
                loopName
                loopOrder
                protocolId
                ratedTorque
                ratedSpeed
                gridSpeed
                cutInSpeed
                cutOutSpeed
                minimumBladeAngle
                hubHeight
                plcIp
                turbineLongitude
                turbineLatitude
                windId
                airDensity
                annualAverageWindSpeed
                turbulenceIntensity
                windShear
                inflowAngle
                windDistributionParameter
                scadaVersion
                }
                }
                """)
key_map = dict(zip(
    [
        "turbineId",
        "innerTurbineName",
        "typeId",
        "typeName",
        "innerTurbineType",
        "innerPlatForm",
        "ratedPower",
        "etlType",
        "Pch2A_Acc",
        "farmId",
        "pinyinCode",
        "farmName",
        "curveId",
        "isDynamic",
        "powerCurve",
        "innerPowerCurve",
        "ownerTurbineName",
        "ownerId",
        "ownerEasyName",
        "ownerName",
        "farmCode",
        "projectName",
        "country",
        "province",
        "city",
        "address",
        "farmLongitude",
        "farmLatitude",
        "capacity",
        "installedNum",
        "loopName",
        "loopOrder",
        "protocolId",
        "ratedTorque",
        "ratedSpeed",
        "gridSpeed",
        "cutInSpeed",
        "cutOutSpeed",
        "minimumBladeAngle",
        "hubHeight",
        "plcIp",
        "turbineLongitude",
        "turbineLatitude",
        "windId",
        "airDensity",
        "annualAverageWindSpeed",
        "turbulenceIntensity",
        "windShear",
        "inflowAngle",
        "windDistributionParameter",
        "scadaVersion",
    ],
    [
        "turbine_id",
        "inner_turbine_name",
        "type_id",
        "type_name",
        "inner_turbine_type",
        "inner_plat_form",
        "rated_power",
        "etl_type",
        "Pch2A_Acc",
        "farm_id",
        "pinyin_code",
        "farm_name",
        "curve_id",
        "is_dynamic",
        "power_curve",
        "inner_power_curve",
        "owner_turbine_name",
        "owner_id",
        "owner_easy_name",
        "owner_name",
        "farm_code",
        "project_name",
        "country",
        "province",
        "city",
        "address",
        "farm_longitude",
        "farm_latitude",
        "capacity",
        "installed_num",
        "loop_name",
        "loop_order",
        "protocol_id",
        "rated_torque",
        "rated_speed",
        "grid_speed",
        "cut_in_speed",
        "cut_out_speed",
        "minimum_blade_angle",
        "hub_height",
        "plc_ip",
        "turbine_longitude",
        "turbine_latitude",
        "wind_id",
        "air_density",
        "annual_average_wind_speed",
        "turbulence_intensity",
        "wind_shear",
        "inflow_angle",
        "wind_distribution_parameter",
        "scada_version"
    ]
))
options = [('grpc.max_message_length', 64 * 1024 * 1024), ('grpc.max_receive_message_length', 64 * 1024 * 1024),
           ('grpc.service_config', '{ "retryPolicy":{ "maxAttempts": 4, "initialBackoff": "0.3s", "maxBackoff": "2s", '
                                   '"backoffMutiplier": 2, "retryableStatusCodes": [ "UNAVAILABLE" ] } }')]


def stub_channel(func):
    def wrapper(self, *args, **kwargs):
        if len(args) > 0:
            stub = args[0]
            if isinstance(stub, str):
                with grpc.insecure_channel(stub, options=options) as channel:
                    stub = model_data_message_pb2_grpc.ModelDataMessageStub(channel)
                    return func(self, stub, *args[1:], **kwargs)
            else:
                return func(self, stub, *args[1:], **kwargs)

        else:
            stub = kwargs['stub']
            if isinstance(stub, str):
                with grpc.insecure_channel(stub, options=options) as channel:
                    stub = model_data_message_pb2_grpc.ModelDataMessageStub(channel)
                    kwargs['stub'] = stub
                    return func(self, **kwargs)
            else:
                return func(self, **kwargs)

    return wrapper


class DataTools(object):
    # This programme is to get data.
    PROGRAMME = 'DataTools'
    VERSION = '3.0.8'

    def __init__(self, *args):
        stub = args[0] if len(args) > 0 else None
        if stub:
            with grpc.insecure_channel(stub, options=options) as channel:
                stub = model_data_message_pb2_grpc.ModelDataMessageStub(channel)
                self.cos_tocken = GetCosToken(stub)
                self.cos_tocken['time'] = time.time()
                self.cos_tocken['deployment'] = GetDeployment(stub)
        else:
            self.cos_tocken = None

    @staticmethod
    def change_v(value):
        if value:
            value = [value] if isinstance(value, str) else value
            value = json.dumps(value)
        return value

    @staticmethod
    def change_turbine(turbine):
        if isinstance(turbine, str) and len(turbine) == 3:
            turbine = json.dumps([turbine])
        elif isinstance(turbine, list):
            for t in turbine:
                if isinstance(t, str) and len(t) != 3:
                    raise ValueError("机组号必须为三位，例如：001")
            turbine = json.dumps(turbine)
        elif turbine is None:
            turbine = turbine
        else:
            raise ValueError("机组号必须为三位，例如：001")
        return turbine

    @staticmethod
    def check_time(str_time):
        if str_time is None:
            pass
        elif isinstance(str_time, str) and len(str_time) >= 10:
            str_time = str_time[:10] + ' 00:00:00'
            try:
                _ = datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                raise ValueError("请输入正确时间格式，例如：2021-01-01")
        else:
            raise ValueError("请输入正确时间格式，例如：2021-01-01")

    @stub_channel
    def get_files(self, stub, farm, data_type, start_time, end_time, turbine=None):
        """
        获取指定风场、机组号、时间段、类型的数据
        :param farm：风场中文拼音名（例如：DBCFC）
        :param data_type：数据类型（history、event、second、fault、qd、cms, ems_log, qd-gslb）
        :param start_time：数据开始时间（包含）, 例如：'2021-03-03'
        :param end_time：数据结束时间（包含）， 例如：'2021-03-10'
        :param turbine：机组号,str或list（例如：'001'，必须为三位数,或['001', '002']），可以省略，省略后将得到所有机组数据
        :return: 匹配到的所有文件列表
        """
        turbine = self.change_turbine(turbine)

        # 时间格式检查
        for str_time in [start_time, end_time]:
            self.check_time(str_time)

        start_time = start_time[:10] + ' 00:00:00'
        end_time = end_time[:10] + ' 23:59:59'
        try:
            dainput = model_data_message_pb2.GetFileListInput(windfarm=farm, turbines=turbine, filetype=data_type,
                                                              start=start_time, end=end_time)
            res = stub.GetFileList(dainput, timeout=20000)
            result_list = json.loads(res.output)
            result_list = [x for x in result_list if farm in x.split('/')]
            if data_type in ['second', 'sec']:
                result_list = [x for x in result_list if 'parquet' in x]
            if data_type == 'ems_log':
                result_list = [x.replace('.csv', '.parquet') for x in result_list]
            result_list = list(set(result_list))
            result_list.sort()
        except Exception as e:
            print(e)
            print('文件列表获取错误')
            result_list = []
        return result_list

    @stub_channel
    def get_self_files(self, stub, project_name, farm=None, turbine_type=None, turbine=None,
                       start_time=None, end_time=None):
        """
        获取指定风场、机组号、时间段、类型的数据
        :param project_name：项目英文名，必须传入
        :param farm：风场中文拼音名（例如：DBCFCB），可省略
        :param turbine_type：机组型号，str或list, 例如："SE14125"或['SE14125', '14630']，可省略
        :param turbine：机组号,str或list（例如：'001'，必须为三位数,或['001', '002']），可以省略
        :param start_time：数据开始时间（包含）, 例如：'2021-03-03'，可省略
        :param end_time：数据结束时间（包含）， 例如：'2021-03-10'，可省略
        :return: 匹配到的所有文件列表
        """
        turbine = self.change_turbine(turbine)
        # 时间格式检查
        for str_time in [start_time, end_time]:
            self.check_time(str_time)

        turbine_type = self.change_v(turbine_type)

        start_time = start_time if start_time is None else start_time[:10] + ' 00:00:00'
        end_time = end_time if end_time is None else end_time[:10] + ' 23:59:59'
        try:
            dainput = model_data_message_pb2.GetFileListInput(windfarm=farm, turbines=turbine, filetype='self',
                                                              start=start_time, end=end_time,
                                                              project_name=project_name, turbine_type=turbine_type)
            res = stub.GetFileList(dainput, timeout=20000)
            result_list = json.loads(res.output)
        except Exception as e:
            print(e)
            print('文件列表获取错误')
            result_list = []
        result_list = list(set(result_list))
        return result_list

    @staticmethod
    def get_parquet_mapping(path='/tmp/14125.xlsx', is_local=True, cloud_point_map=dict()):
        if is_local:
            df = pd.read_excel(path)
            df = df.dropna(subset=['SCADA编号'])
            df_scada = df.set_index('SCADA编号', drop=True)
            scada_dict = df_scada['中文描述'].T.to_dict()

            df_cn = df.set_index('中文描述', drop=True)
            cn_dict = df_cn['SCADA编号'].T.to_dict()

            return scada_dict, cn_dict
        else:
            cn_dict = dict([(v, k) for k, v in cloud_point_map.items()])
            scada_dict = cloud_point_map
            return scada_dict, cn_dict

    @staticmethod
    def drop_columns_duplication(columns):
        columns_set = list(set(columns))
        columns_set.sort(key=columns.index)
        return columns_set

    def get_costocken(self, stub):
        if self.cos_tocken and (time.time() - self.cos_tocken['time']) / 3600 < 23:
            pass
        else:
            with grpc.insecure_channel(stub, options=options) as channel:
                stub = model_data_message_pb2_grpc.ModelDataMessageStub(channel)
                self.cos_tocken = GetCosToken(stub)
                self.cos_tocken['time'] = time.time()
                self.cos_tocken['deployment'] = GetDeployment(stub)

    @staticmethod
    def check_map(map_fc):
        if map_fc and isfunction(map_fc):
            map_default_v = inspect.getfullargspec(map_fc)[0]
            if len(map_default_v) == 1 and 'data' in map_default_v:
                return 1
            elif len(map_default_v) == 2 and 'data' in map_default_v and 'map_v' in map_default_v:
                return 2
            else:
                print("请输入正确map_fc函数参数，map_fc函数输入参数只能包含data与字典map_v(map_v可选)")
                return 0

        return 3

    @staticmethod
    def map_data(df, check_result, map_fc, map_v):
        if check_result == 1:
            df = map_fc(data=df)
        elif check_result == 2:
            df = map_fc(data=df, map_v=map_v)
        else:
            pass
        return df

    def pd_read_csv(self, file_data, columns, header, names, map_fc, map_v, check_result, turbine_num=None,
                    file_type='csv', sheet_name=0):
        try:
            if file_type == 'csv':
                df = pd.read_csv(io.BytesIO(file_data), header=header, names=names, encoding='utf-8', usecols=columns)
            elif file_type == 'excel':
                df = pd.read_excel(io.BytesIO(file_data), header=header, names=names,
                                   usecols=columns, sheet_name=sheet_name)
        except Exception as e:
            if file_type == 'csv':
                df = pd.read_csv(io.BytesIO(file_data), header=header, names=names, encoding='gbk', usecols=columns)
            else:
                print(e)
        if columns:
            df = df.reindex(columns=columns)
        if turbine_num:
            df['turbine_num'] = turbine_num
        df = self.map_data(df, check_result, map_fc, map_v)
        return df

    def pd_read_parquet(self, file_data, columns, map_fc, map_v, check_result):
        data = io.BytesIO(file_data)
        if columns:
            schem_columns = pq.read_schema(data)
            schem_columns_all = set(schem_columns.names)
            inner_columns = list(set(columns).intersection(schem_columns_all))

            df = pd.read_parquet(data, columns=inner_columns)
            df = df.reindex(columns=columns)
        else:
            df = pd.read_parquet(data)
        if columns:
            df = df.reindex(columns=columns)
        df = self.map_data(df, check_result, map_fc, map_v)
        return df

    def get_csv_data(self, stub, file_list, columns=None, header='infer', names=None, map_fc=None, map_v=None,
                     use_filename=False, file_type='csv', sheet_name=0):
        """
        获取指定文件列表中的文件
        :param file_list：所要获取文件列表，文件只能是csv格式
        :param header：指定文件列名，默认为infer
        :param columns：所需获取的列名，list
        :param names：重定义列名
        :param map_fc：map函数
        :param map_v：map函数所以来的外部值对应字典
        :param use_filename：如果为True,则读取出的数据增加sanydata_file_name列，值为对应文件名
        :param file_type：文件类型
        :param sheet_name：所要读取的sheet名字
        :return：pandas.DataFrame
        """
        check_result = self.check_map(map_fc)

        if check_result == 0:
            return None

        self.get_costocken(stub)
        df_all = list()
        index = 0
        if columns:
            columns = self.drop_columns_duplication(columns)
        for file_data in GetTargetFile(file_list, self.cos_tocken):
            file_name = file_list[index].split('/')[-1]
            index = index + 1
            if file_data:
                if file_type == 'csv':
                    df = self.pd_read_csv(file_data, columns, header, names, map_fc, map_v, check_result)
                elif file_type == 'excel':
                    df = self.pd_read_csv(file_data, columns, header, names, map_fc, map_v, check_result,
                                          file_type=file_type, sheet_name=sheet_name)
                if use_filename:
                    df['sanydata_file_name'] = file_name
                df_all.append(df)

        if len(df_all) > 0:
            df_all = pd.concat(df_all)
            df_all = df_all.reset_index(drop=True)
        return df_all

    def get_self_data(self, stub, file_list, columns=None, header='infer',
                      names=None, map_fc=None, map_v=None, use_filename=False, sheet_name=0):

        check_result = self.check_map(map_fc)

        if check_result == 0:
            return None

        self.get_costocken(stub)
        df_all = list()
        if columns:
            columns = self.drop_columns_duplication(columns)
        index = 0

        for file_data in GetTargetFile(file_list, self.cos_tocken):

            file_name = file_list[index].split('/')[-1]
            index = index + 1
            if file_data:
                if file_name.split('.')[-1] == 'parquet':
                    df = self.pd_read_parquet(file_data, columns, map_fc, map_v, check_result)
                    if use_filename:
                        df['sanydata_file_name'] = file_name
                    df_all.append(df)
                elif file_name.split('.')[-1] == 'csv':
                    df = self.pd_read_csv(file_data, columns, header, names, map_fc, map_v, check_result)
                    if use_filename:
                        df['sanydata_file_name'] = file_name
                    df_all.append(df)
                elif file_name.split('.')[-1] == 'xlsx':
                    df = self.pd_read_csv(file_data, columns, header, names, map_fc, map_v, check_result,
                                          file_type='excel', sheet_name=sheet_name)
                    if use_filename:
                        df['sanydata_file_name'] = file_name
                    df_all.append(df)
                else:
                    print(file_name)
                    print('无法读取该数据类型')

        if len(df_all) > 0:
            df_all = pd.concat(df_all)
            df_all = df_all.reset_index(drop=True)
        return df_all

    def get_data(self, stub, file_list, columns=None, map_fc=None,
                 map_v=None, data_type=None, names=None, header='infer',
                 use_filename=False, point_map_is_local=True, cloud_point_map=dict()):
        """
        获取文件数据
        :param file_list：所要获取文件列表
        :param columns：需要的字段，默认加载所有字段
        :param map_fc：获取时指定自定义的map函数，将对每个文件执行map函数，
        map_fc输入参数必须包含"data",即获取到的数据，然后使用者可对data进行清洗等操作；
        map_fc的可选参数为"map_v",dict类型，如果有额外参数，都传入map_v字典中
        例如：筛选秒级数据中机舱X方向振动值大于指定值的数据，则map_fc可按以下方式编写
        def my_fc(data, map_v):
            a = map_v['a']
            df = data[data['机舱X方向振动值'] > a]
            return df
        :param map_v：dict类型，自定义map函数中可选参数
        :param data_type：如果需要获取自行上传的数据，则data_type需要传入"self"关键字
        :param names：自定义文件或cms数据获取时，设置列名
        :param header：自定义文件或cms数据获取时，首行处理方式
        :param use_filename：如果需要将文件列表名加入字段，则设置use_filename为True,输出数据中会增加file_name字段
        :param point_map_is_local：是否采用本地点表，默认是True，False代表采用hadoop上的点表
        :param cloud_point_map：如果point_map_is_local为False，则传入外部的云端的点表
        :return：所查询数据合并成的pandas.DataFrmae，在原有的列上增加turbine_num列，用来标识机组号，例：001
        """
        self.get_costocken(stub)
        df_all = list()

        if data_type == 'self' or data_type == 'other':
            df_all = self.get_self_data(stub, file_list, columns, header,
                                        names, map_fc, map_v, use_filename)
            return df_all

        check_result = self.check_map(map_fc)

        if check_result == 0:
            return None

        scada_dict, cn_dict = self.get_parquet_mapping(is_local=point_map_is_local, cloud_point_map=cloud_point_map)

        # 去除中文转换后与scada编号一致重复列名
        if columns:
            columns = [scada_dict[x] if x in scada_dict else x for x in columns]
            columns = self.drop_columns_duplication(columns)

        index = 0
        for file_data in GetTargetFile(file_list, self.cos_tocken):

            file_name = file_list[index].split('/')[-1]
            index = index + 1
            if file_data:
                try:
                    if file_name.split('.')[-1] == 'parquet':
                        turbine_num = file_name.split('#')[0].zfill(3)
                        if columns:
                            schema_names = pq.read_schema(io.BytesIO(file_data)).names  # 获取原始数据列名
                            # 对于点表包含的点进行转换，否则保留原始输入column名
                            scada_use_columns = [cn_dict[x] if x in cn_dict.keys() else x for x in columns]
                            # 获取原始数据列名与转换后列名一致的columns，read_schema
                            read_schema = list(set(scada_use_columns) & set(schema_names))
                            # 获取原始数据没有的列名，no_schema
                            no_schema = list(set(scada_use_columns) - set(schema_names))
                            df = pd.read_parquet(io.BytesIO(file_data), columns=read_schema)
                            if len(no_schema) > 0:
                                df[no_schema] = None
                            df = df.rename(columns=scada_dict)
                            columns = [scada_dict[x] if x in scada_dict else x for x in columns]
                            df = df[columns]
                        else:
                            df = pd.read_parquet(io.BytesIO(file_data))
                            df = df.rename(columns=scada_dict)

                        df['turbine_num'] = turbine_num
                        if use_filename:
                            df['sanydata_file_name'] = file_name
                        df = self.map_data(df, check_result, map_fc, map_v)
                        df_all.append(df)
                    else:
                        turbine_num = file_name.split('_')[1]
                        if 'cmsadaptor' in file_list[0].split('/'):
                            header = None
                            names = ['振动幅值']
                        df = self.pd_read_csv(file_data, columns, header, names, map_fc, map_v, check_result, turbine_num)
                        if use_filename:
                            df['sanydata_file_name'] = file_name
                        df_all.append(df)
                except Exception as e:
                    print(file_name)
                    print(e)
        if len(df_all) > 0:
            df_all = pd.concat(df_all)
            df_all = df_all.reset_index(drop=True)
        return df_all

    def put_manager_data(self, stub, files, columns, result_list, map_fc, map_v, data_type=None, names=None,
                         header='infer', use_filename=False):
        if len(files) > 0:
            try:
                df = self.get_data(stub, files, columns, map_fc, map_v, data_type=data_type, names=names,
                                   header=header, use_filename=use_filename)
                if isinstance(df, pd.DataFrame) and len(df) > 0:
                    result_list.append(df)
                else:
                    result_list.append(files)
            except Exception as e:
                result_list.append(files)

    def get_data_process(self, stub, file_list, columns, process=None, map_fc=None, map_v=None,
                         data_type=None, names=None, header='infer', use_filename=False):
        """
        多进程获取文件数据
        :param file_list：所要获取文件列表
        :param columns：需要的字段，默认加载所有字段
        :param process：进程数，如果文件小于去10个或运行环境cpu核心数小于2，则单进程执行，如果未指定，则进程数未环境cpu核心数-1
        :param map_fc：获取时指定自定义的map函数，将对每个文件执行map函数，
        map_fc输入参数必须包含"data",即获取到的数据，然后使用者可对data进行清洗等操作；
        map_fc的可选参数未"map_v",dict类型，如果有额外参数，都传入map_v字典中
        例如：筛选秒级数据中机舱X方向振动值大于指定值的数据，则map_fc可按以下方式编写
        def my_fc(data):
            a = map_v['a']
            df = data[data['机舱X方向振动值'] > a]
            return df
        :param map_v：dict类型，自定义maph函数中可选参数
        :return：所查询数据合并成的pandas.DataFrmae，在原有的列上增加turbine_num列，用来标识机组号，例：001
        """
        self.get_costocken(stub)
        cpu_count = multiprocessing.cpu_count() - 1
        if len(file_list) < 10 or cpu_count < 2:
            result = self.get_data(stub, file_list, columns=columns, map_fc=map_fc, map_v=map_v,
                                   data_type=data_type, names=names, header=header, use_filename=use_filename)
            return result

        cpu_count = cpu_count if len(file_list) > cpu_count else len(file_list)
        check_result = self.check_map(map_fc)
        if check_result == 0:
            return None
        process = process if process else cpu_count
        manager = multiprocessing.Manager()
        return_list = manager.list()
        p_list = list()
        process_dict = dict()
        process_files = list()
        for files in [file_list[process_num::process] for process_num in range(process)]:
            p = multiprocessing.Process(target=self.put_manager_data, args=(stub, files,
                                                                            columns, return_list, map_fc, map_v,
                                                                            data_type, names, header, use_filename))
            p_list.append(p)
            p.start()
            process_dict[str(p.pid)] = files

        for p1 in p_list:
            p1.join()
        for p1 in p_list:
            if p1.exitcode != 0:
                process_files = process_files + process_dict[str(p1.pid)]

        error_files = [x for x in return_list if isinstance(x, list)]
        error_files_list = sum(error_files, [])
        error_files_list = error_files_list + process_files
        if len(error_files_list) > 0:
            df_error = self.get_data(stub, error_files_list, columns=columns, map_fc=map_fc, map_v=map_v,
                                     data_type=data_type, names=names, header=header, use_filename=use_filename)
        else:
            df_error = None
        return_list.append(df_error)
        result = [x for x in return_list if isinstance(x, pd.DataFrame)]
        if len(result) > 0:
            result = pd.concat(result)
            result = result.reset_index(drop=True)
        else:
            result = None
        return result

    @stub_channel
    def return_result(self, stub, project_name, wind_farm, data_start_time, data_end_time,
                      turbine_type=None, turbine_num=None, status=None, result=None,
                      result_json=None, upload_fig_path=None, upload_log_path=None,
                      upload_file_path=None, local_fig_path=None, local_log_path=None,
                      local_file_path=None, model_version=None, project_id=None, comment=None,
                      description=None, rm_file=True):

        """
        模型结果保存接口
        :param project_name：模型英文名，不可省略
        :param wind_farm：风场拼音缩写，不可省略
        :param data_start_time：模型中使用的数据期望开始时间，不可省略（
        方便后续排查问题查询，格式统一为‘%Y-%m-%d %H:%M:%S’）
        :param data_end_time：模型中使用的数据期望结束时间，不可省略（
        格式统一为‘%Y-%m-%d %H:%M:%S’）
        :param turbine_type：机组型号（字符串，例如：‘SE14125’），可省略
        :param turbine_num：机组号（字符串，例如：001,002），可省略
        :param status：判断状态，共分为三种：正常、告警、故障（目的是前端显示颜色，分别为无色、黄色、红色），可省略
        :param result：模型判断结果（例如：0.8、90，正常等），可省略
        :param result_json：模型产生的其他信息，str(dict())格式，例如：
                    str({'real_start_time':'2020-09-11 00:00:01', 'real_end_time':'2020-09-12 00:00:01'})，
                    real_start_time、real_end_time代表数据真实开始于结束时间，不建议省略（主要留作后续给前段产生动态图的json数据），
        :param upload_fig_path：模型产生图片云端保存位置，可省略
        :param upload_log_path：模型产生日志云端保存位置，可省略
        :param upload_file_path：模型其他文件云端保存位置，可省略
        :param local_fig_path：模型产生的图片本地保存位置，可省略
        :param local_log_path：模型产生的日志本地保存位置，可省略
        :param local_file_path：模型产生的其他文件本地保存位置，可省略
        :param model_version：模型版本号（例如：1.0.0），可省略，(不建议省略)
        :param project_id：模型id号（例如：10001），可省略(目前可省略，后续统一之后再设置)
        :param comment：故障类型，例如：偏航振动异常，地形振动异常，位于图片右上角
        :param description：故障/正常描述，位于图片下方
        :param rm_file：上传文件时，是否删除本地文件，默认为删除，如果传入False,则不删除
        :return：返回为int数字，如果成功，则返回0，如果失败，则返回1
        注意：
        1）模型执行过程将产生的图片、日志、其他文件等暂保存为"本地"位置(这里本地是指执行代码的环境下)，最终通过调用接口，传入相关参数后，
           接口会自动将本地文件传入云端cos，并删除本地文件
        2）模型上传文件统一格式为：fig、log、file/{模型名字，project_name}/{wind_farm,风场名}/**.png、**.log、**.csv、其他；
          （**代表最终文件命名，命名时应尽可能说明机组号、模型所使用数据时间范围等信息，可以对模型每次执行结果进行区分）
        3）模型本地保存统一格式为：/tmp/sanydata_frpc_**.png、sanydata_frpc_**.log、sanydata_frpc_**.csv、其他
          （上述中**代表最终文件命名，命名时应尽可能避免多文件保存到本地时进行覆盖，建议采用当前时间戳）

        """

        model_end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        model_start_time = os.getenv('ModelStartTime')
        task_id = int(os.getenv('TaskId'))
        if not model_version:
            model_version = os.getenv('ProjectVersion')

        fig_fio = None
        log_fio = None
        file_fio = None
        # 本地图片处理
        if local_fig_path:
            with open(local_fig_path, 'rb') as f:
                fig_fio = f.read()
            if rm_file:
                os.remove(local_fig_path)
        # 本地日志处理
        if local_log_path:
            with open(local_log_path, 'rb') as f:
                log_fio = f.read()
            if rm_file:
                os.remove(local_log_path)
        # 本地其他文件处理
        if local_file_path:
            with open(local_file_path, 'rb') as f:
                file_fio = f.read()
            if rm_file:
                os.remove(local_file_path)

        data_input = model_data_message_pb2.ReturnResultInput(projectname=project_name,
                                                              windfarm=wind_farm, turbinetype=turbine_type,
                                                              turbine=turbine_num, description=description,
                                                              DataStartTime=data_start_time, DataEndTime=data_end_time,
                                                              ModeStartTime=model_start_time,
                                                              ModeEndTime=model_end_time,
                                                              projectid=project_id, projectversion=model_version,
                                                              task_id=task_id, comment=comment,
                                                              result=result, resultjson=result_json, status=status,
                                                              uploadfigpath=upload_fig_path,
                                                              uploadlogpath=upload_log_path,
                                                              uploadfilepath=upload_file_path,
                                                              fig=fig_fio, log=log_fio, file=file_fio)
        res = stub.ReturnResult(data_input, timeout=20000)
        return int(json.loads(res.code))

    @stub_channel
    def put_files(self, stub, local_files, upload_files=None, database=False, project_name=None, wind_farm=None,
                  turbine_type=None, turbine_num=None, data_time=None, file_type=None, rm_file=True):
        """
        其他文件上传接口，例如子图等
        :param local_files：模型产生的文件本地保存位置，list类型 ，例如：['1.png', '2.png']
        :param upload_files：模型产生的文件云端保存位置，list类型，例如：['test1/1.png', 'test2/2.png'],
                             可省略，省略后将自动生成保存位置，注：如果进行自定义传入，则local_files与upload_files必须一一对应
        :param database：数据是否入库，方便后续查询，默认不入库，如要入库，请传入True
        :param project_name：模型英文名
        :param wind_farm：风场拼音缩写，例如：'TYSFCB'
        :param turbine_type：机型号，例如：'SE4125'
        :param turbine_num：机组号，例如：'001'
        :param data_time：文件时间，必须为'2020-01-01'格式，可省略
        :param file_type：文件类型，必须为file或fig
        :param rm_file：上传文件时，是否删除本地文件，默认为删除，如果传入False,则不删除
        :return：云端保存的位置
        """
        if database and project_name is None:
            print('请输入项目名')
            return
        if database and isinstance(data_time, str) and len(data_time) >= 10:
            data_time = data_time[:10] + ' 00:00:00'
        elif database and isinstance(data_time, str) and len(data_time) < 10:
            print('请检查输入的data_time时间格式,正确格式如：2021-01-01')
            return
        else:
            pass
        wind_farm = 'all_farm' if wind_farm is None else wind_farm
        turbine_type = 'all_turbine_type' if turbine_type is None else turbine_type
        turbine_num = 'all_turbine' if turbine_num is None else turbine_num
        data_time = 'all_time' if data_time is None else data_time.split(' ')[0]
        upload_path = f'{file_type}/{project_name}/{data_time}'
        if isinstance(local_files, list) and upload_files is None:
            upload_files = [f'{upload_path}/{wind_farm}/{turbine_type}/{turbine_num}/' + x.split('/')[-1]
                            for x in local_files]
        elif isinstance(local_files, list) and isinstance(upload_files, list):
            pass
        else:
            print('请输入正确文件列表')
            return
        file_type = os.getenv('FileType')
        if not file_type:
            file_type = 'cosfig'
        result = list()
        # 本地其他文件处理
        for local_file_path, upload_file_path in zip(local_files, upload_files):
            if not local_file_path:
                print(local_file_path + '：本地不存在')
                continue
            with open(local_file_path, 'rb') as f:
                file_fio = f.read()
            if rm_file:
                os.remove(local_file_path)
            data_time = None if data_time == 'all_time' else data_time
            wind_farm = None if wind_farm == 'all_farm' else wind_farm
            turbine_type = None if turbine_type == 'all_turbine_type' else turbine_type
            turbine_num = None if turbine_num == 'all_turbine' else turbine_num
            data_input = model_data_message_pb2.PutFileInput(type=file_type, uploadfilepath=upload_file_path,
                                                             file=file_fio, database=database,
                                                             project_name=project_name, wind_farm=wind_farm,
                                                             turbine_type=turbine_type, turbine_num=turbine_num,
                                                             data_time=data_time)
            res = stub.PutFile(data_input, timeout=20000)
            if res.msg:
                result.append('put_file error, error is {}'.format(res.msg))
            else:
                result.append(res.coskey)

        return result

    # 保存结果三个分析模块的结果文件
    @stub_channel
    def return_report_result(self, stub, project_name, wind_farm, data_start_time, data_end_time,
                             turbine_type=None, turbine_num=None, status=None, result=None,
                             result_json=None, upload_fig_path=None, upload_log_path=None,
                             upload_file_path=None, local_fig_path=None, local_log_path=None,
                             local_file_path=None, Report_version=None, project_id=None):
        """
        将事件分析，发电量分析，健康分析三个模块的结果文件传入COS上(一次只传一个文件)
        :param project_name：报表英文名，不可省略
        :param wind_farm：风场拼音缩写，不可省略
        :param data_start_time：报表中使用的数据开始时间，不可省略（
                                方便后续排查问题查询，格式统一为‘%Y-%m-%d %H:%M:%S’）
        :param data_end_time：报表中使用的数据结束时间，不可省略（
                              格式统一为‘%Y-%m-%d %H:%M:%S’）
        :param turbine_type：机组型号（字符串，例如：‘14125’），可省略
        :param turbine_num：机组号（字符串，例如：01,02），可省略
        :param status：判断状态，共分为三种：正常、告警、故障（目的是前端显示颜色，分别为无色、黄色、红色）
        :param result：报表判断结果（例如：0.8、90，不可判断等），可省略
        :param result_json：报表产生的其他信息，json格式，可省略（主要留作后续给前段产生动态图的json数据）
        :param upload_fig_path：报表产生图片云端保存位置，可省略
        :param upload_log_path：报表产生日志云端保存位置，可省略
        :param upload_file_path：报表其他文件云端保存位置，可省略
        :param local_fig_path：报表产生的图片本地保存位置，可省略
        :param local_log_path：报表产生的日志本地保存位置，可省略
        :param local_file_path：报表产生的其他文件本地保存位置，可省略
        :param Report_version：报表版本号（例如：1.0.0），可省略，(不建议省略)
        :param project_id：报表id号（例如：10001），可省略(目前可省略，后续统一之后再设置)
        :return：返回为int数字，如果成果，则返回0，如果失败，则返回1
         注意：
         1）报表执行过程将产生的图片、日志、其他文件等暂保存为本地位置，最终通过调用接口，传入相关参数后，接口会自动将本地文件传入云端，并删除本地文件
         2）报表上传文件统一格式为：fig、log、file/{报表名字，project_name}/{wind_farm,风场名}/**.png、**.log、**.csv、其他；（**代表最终文件命名，命名时应尽可能说明机组号、报表所使用数据时间等信息，可以对报表每次执行结果进行区分）
         3）报表本地保存统一格式为：/tmp/sanydata_frpc_**.png、sanydata_frpc_**.log、sanydata_frpc_**.csv、其他（上述中**代表最终文件命名，命名时应尽可能避免多文件保存到本地时进行覆盖，建议采用当前时间）

        """

        Report_end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        Report_start_time = os.getenv('ReportStartTime')
        task_id = int(os.getenv('TaskId'))

        if not Report_version:
            Report_version = os.getenv('ProjectVersion')

        fig_fio = None
        log_fio = None
        file_fio = None

        # 本地图片处理
        if local_fig_path:
            with open(local_fig_path, 'rb') as f:
                fig_fio = f.read()
            os.remove(local_fig_path)
        # 本地日志处理
        if local_log_path:
            with open(local_log_path, 'rb') as f:
                log_fio = f.read()
            os.remove(local_log_path)
        # 本地文件处理
        if local_file_path:
            with open(local_file_path, 'rb') as f:
                file_fio = f.read()
            os.remove(local_file_path)

        data_input = model_data_message_pb2.ReturnReportResultInput(projectname=project_name,
                                                                    windfarm=wind_farm, turbinetype=turbine_type,
                                                                    turbine=turbine_num,
                                                                    DataStartTime=data_start_time,
                                                                    DataEndTime=data_end_time,
                                                                    ModeStartTime=Report_start_time,
                                                                    ModeEndTime=Report_end_time,
                                                                    projectid=project_id, projectversion=Report_version,
                                                                    task_id=task_id,
                                                                    result=result, resultjson=result_json,
                                                                    status=status,
                                                                    uploadfigpath=upload_fig_path,
                                                                    uploadlogpath=upload_log_path,
                                                                    uploadfilepath=upload_file_path,
                                                                    fig=fig_fio, log=log_fio, file=file_fio)

        res = stub.ReturnReportResult(data_input, timeout=20000)
        return json.loads(res.code)

    @stub_channel
    def return_fault_analy(self, stub, fault_detail_df):
        """
        将故障明细表插入mysql中
        :param fault_detail_df:  故障明细表
        :return:返回为int数字，如果成果，则返回0，如果失败，则返回1
        """

        res_l = list()
        for index, row in fault_detail_df.iterrows():
            pinyincode = row['farm']
            turbinename = row['fan']
            statuscode = row['list_code']
            faultdesc = row['list_name']
            faultpart = row['list_partstyle']
            faultstarttime = row['list_stime']
            faultendtime = row['list_etime']
            downtime = row['list_time']
            dentatime = row['list_mt']
            updatetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            farmid = row['farm_id']
            farmname = row['farm_name']
            turbineid = row['turbine_id']
            turbinetype = row['turbine_type']
            faulttype = row['fault_type']

            data_input = model_data_message_pb2.ReturnFaultAnalyInput(farmid=farmid, pinyincode=pinyincode,
                                                                      farmname=farmname,
                                                                      turbineid=turbineid, turbinename=turbinename,
                                                                      turbinetype=turbinetype, statuscode=statuscode,
                                                                      faultdesc=faultdesc, faulttype=faulttype,
                                                                      faultpart=faultpart,
                                                                      faultstarttime=faultstarttime,
                                                                      faultendtime=faultendtime, downtime=downtime,
                                                                      dentatime=dentatime, updatetime=updatetime)
            res = stub.ReturnFaultAnaly(data_input, timeout=20000)
            res_l.append({index: res})
        return res_l

    @stub_channel
    def return_report_result_status(self, stub, page_feature_sta, page_power_sta, taskname, jobname, farmid=None,
                                    farmname=None, reporttype=None, datestring=None, reportargs=None,
                                    analyzingsummary=None, analyzingreports=None, taskid=None, comment=None,
                                    description=None):
        """
        将页面显示的指标及文件地址插入mysql中
        :param page_feature_sta: 页面显示前9个指标
        :param page_power_sta:   页面显示的关于发电量3个指标
        :param analyzingsummary：分析总结html文件
        :param analyzingreports：分析报表json格式，文件与cos地址
        param comment：备用字段
        param description：备用字段
        :return: 返回为int数字，如果成果，则返回0，如果失败，则返回1
        """

        taskname = taskname
        jobname = jobname
        farmid = farmid
        farmname = farmname
        reporttype = reporttype
        datestring = datestring
        reportargs = reportargs
        turbinecount = page_feature_sta['风机台数'].iloc[0]
        averageavailability = page_feature_sta['平均可利用率'].iloc[0]
        totalhalttime = page_feature_sta['总停机时长'].iloc[0]
        haltfrequency = page_feature_sta['停机频次'].iloc[0]
        totalhaltcount = page_feature_sta['总停机次数'].iloc[0]
        averagehalttime = page_feature_sta['平均停机时长'].iloc[0]
        totalhaltturbines = page_feature_sta['总停机台数'].iloc[0]
        mtbf = page_feature_sta['平均无故障时间'].iloc[0]
        mttr = page_feature_sta['平均恢复时间'].iloc[0]
        event_completeness = page_feature_sta['事件记录数据完整率'].iloc[0]
        averagespeed = page_power_sta['平均风速'].iloc[0]
        totalpower = page_power_sta['总发电量'].iloc[0]
        cyclepower = page_power_sta['发电量'].iloc[0]
        history_completeness = page_power_sta['5min数据完整率'].iloc[0]
        analyzingsummary = analyzingsummary
        analyzingreports = analyzingreports
        taskid = taskid
        updatedat = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        createdat = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_input = model_data_message_pb2.ReturnReportResultStatusInput(taskname=taskname, jobname=jobname,
                                                                          farmid=farmid,
                                                                          farmname=farmname, reporttype=reporttype,
                                                                          datestring=datestring,
                                                                          reportargs=reportargs,
                                                                          turbinecount=turbinecount,
                                                                          averageavailability=averageavailability,
                                                                          averagehalttime=averagehalttime,
                                                                          haltfrequency=haltfrequency,
                                                                          totalhaltcount=totalhaltcount,
                                                                          totalhalttime=totalhalttime,
                                                                          totalhaltturbines=totalhaltturbines,
                                                                          mtbf=mtbf, mttr=mttr,
                                                                          averagespeed=averagespeed,
                                                                          totalpower=totalpower, cyclepower=cyclepower,
                                                                          analyzingsummary=analyzingsummary,
                                                                          analyzingreports=analyzingreports,
                                                                          taskid=taskid, createdat=createdat,
                                                                          updatedat=updatedat,
                                                                          eventcom=event_completeness,
                                                                          historycom=history_completeness,
                                                                          comment=comment,
                                                                          description=description)
        res = stub.ReturnReportResultStatus(data_input, timeout=20000)

        return res

    @stub_channel
    def shut_down_rpc(self, stub):
        ShutdownCommandRequest = model_data_message_pb2.ShutdownCommandRequest(command=True)
        stub.ShutdownRpc(ShutdownCommandRequest)

    @staticmethod
    def get_time_str(time_list):
        time_s = time_list[0] if time_list[0] is None else time_list[0][:10] + ' 00:00:00'
        time_e = time_list[1] if time_list[1] is None else time_list[1][:10] + ' 23:59:59'
        return time_s, time_e

    @staticmethod
    def check_time_list(time_list):
        if isinstance(time_list, list) and len(time_list) == 2:
            pass
        else:
            raise ValueError("请输入正确时间范围，例如：['2021-03-03', '2021-03-04']")

    @stub_channel
    def get_model_result(self, stub, project_name=None, farm=None, turbine=None,
                         data_start_time_list=[None, None], data_end_time_list=[None, None],
                         model_start_time_list=[None, None], model_end_time_list=[None, None]):
        """
        获取指定风场、机组号、时间段、类型的数据
        :param project_name：项目英文名，如果为多个，则传入list，如果是一个，可直接传入字符串
        :param farm：风场中文拼音名（例如：DBCFCB），如果为多个，则传入list，如果是一个，可直接传入字符串
        :param turbine：机组号,str或list（例如：'001'，必须为三位数,或['001', '002']），可以省略
        :param data_start_time_list：数据开始时间（包含）范围, 例如：['2021-03-03', '2021-03-04']，可省略
        :param data_end_time_list：数据结束时间（包含）范围， 例如：['2021-03-03', '2021-03-04']，可省略
        :param model_start_time_list：数据开始时间（包含）范围, 例如：['2021-03-03', '2021-03-04']，可省略
        :param model_end_time_list：数据结束时间（包含范围）， 例如：['2021-03-03', '2021-03-04']，可省略
        :return: 匹配到的所有数据pandas.DataFrame
        """
        turbine = self.change_turbine(turbine)
        project_name = self.change_v(project_name)
        farm = self.change_v(farm)

        # 时间格式转换
        for str_time_list in [data_start_time_list, data_end_time_list, model_start_time_list, model_end_time_list]:
            self.check_time_list(str_time_list)
            for str_time in str_time_list:
                self.check_time(str_time)

        data_start_time_s, data_start_time_e = self.get_time_str(data_start_time_list)
        data_end_time_s, data_end_time_e = self.get_time_str(data_end_time_list)
        model_start_time_s, model_start_time_e = self.get_time_str(model_start_time_list)
        model_end_time_s, model_end_time_e = self.get_time_str(model_end_time_list)
        try:

            request = model_data_message_pb2.GetModelResultRequest(project_name=project_name, windfarm=farm,
                                                                   turbines=turbine,
                                                                   data_start_time_s=data_start_time_s,
                                                                   data_start_time_e=data_start_time_e,
                                                                   data_end_time_s=data_end_time_s,
                                                                   data_end_time_e=data_end_time_e,
                                                                   model_start_time_s=model_start_time_s,
                                                                   model_start_time_e=model_start_time_e,
                                                                   model_end_time_s=model_end_time_s,
                                                                   model_end_time_e=model_end_time_e,
                                                                   )

            res = stub.GetModelResult(request, timeout=20000)

            result_dataframe = res.output

            if result_dataframe != '':
                return pd.read_json(result_dataframe)
            else:
                print('未查询到信息')
                return None

        except Exception as e:
            print(str(e))
            print('模型结果获取错误')
            return None

    @stub_channel
    def get_first_fault(self, stub, farm=None, turbine=None, fault_code=None,
                        fault_tags=None, fault_start_time_list=[None, None],
                        fault_end_time_list=[None, None]):
        """
        获取云端首发故障信息
        :param farm：风场中文拼音名（例如：DBCFCB），如果为多个，则传入list，如果是一个，可直接传入字符串
        :param turbine：机组号,str或list（例如：'001'，必须为三位数,或['001', '002']），可省略
        :param fault_code：故障码,str或list（例如：'706'，或['706', '707']），可省略
        :param fault_tags：云端首发故障标签,str或list（例如：'受累'，或['受累', '人为']），可以省略
        :param fault_start_time_list：故障开始时间（包含）范围, 例如：['2021-03-03', '2021-03-04']，可省略
        :param fault_end_time_list：故障结束时间（包含）范围, 例如：['2021-03-03', '2021-03-04']，可省略
        :return: 匹配到的所有数据pandas.DataFrame
        """
        turbine = self.change_turbine(turbine)
        farm = self.change_v(farm)

        fault_code = self.change_v(fault_code)
        fault_tags = self.change_v(fault_tags)

        # 时间格式检查
        for str_time_list in [fault_start_time_list, fault_end_time_list]:
            self.check_time_list(str_time_list)
            for str_time in str_time_list:
                self.check_time(str_time)

        fault_start_time_s, fault_start_time_e = self.get_time_str(fault_start_time_list)
        fault_end_time_s, fault_end_time_e = self.get_time_str(fault_end_time_list)

        try:

            request = model_data_message_pb2.GetFirstFaultRequest(windfarm=farm,
                                                                  turbines=turbine,
                                                                  fault_code=fault_code,
                                                                  fault_tags=fault_tags,
                                                                  fault_start_time_s=fault_start_time_s,
                                                                  fault_start_time_e=fault_start_time_e,
                                                                  fault_end_time_s=fault_end_time_s,
                                                                  fault_end_time_e=fault_end_time_e,)

            res = stub.GetFirstFault(request, timeout=20000)

            result_dataframe = res.output

            if result_dataframe != '':
                return pd.read_json(result_dataframe)
            else:
                print('未查询到信息')
                return None

        except Exception as e:
            print(str(e))
            print('云平台首发故障获取错误')
            return None


class WindFarmInf(object):
    # This programme is to get wind farm information.
    PROGRAMME = 'WindFarmInf'
    VERSION = '1.1.5'

    def __init__(self, sql_file='/tmp/1597716056484sqlite.sqlite',
                 graphql_url="https://graphql.sanywind.net/graphql", use_grapql=True):
        position = os.getenv('Position')
        if not use_grapql or position == 'local':
            if os.path.exists(sql_file):
                conn = sqlite3.connect(sql_file)
                self.df_wind_farm_turbine = pd.read_sql('select * from wind_farm_turbine', con=conn)
                self.df_turbine_type_powercurve = pd.read_sql('select * from turbine_type_powercurve', con=conn)
                self.df_turbine_part_attribute = pd.read_sql('select * from turbine_part_attribute', con=conn)
                self.df_turbine_protocol_point = pd.read_sql('select * from turbine_protocol_point', con=conn)
                conn.close()
            else:
                print('本地主数据文件不存在')
        else:
            transport = RequestsHTTPTransport(url=graphql_url, verify=True, retries=3, )
            client = Client(transport=transport, fetch_schema_from_transport=True)
            result = client.execute(query)
            self.turbineAllSqlite = pd.DataFrame.from_dict(result["turbineAllSqlite"])
            self.turbineAllSqlite = self.turbineAllSqlite.rename(columns=key_map)
            self.df_wind_farm_turbine = self.turbineAllSqlite
            self.df_turbine_type_powercurve = self.turbineAllSqlite
        try:
            self.df_wind_farm_turbine['inner_plat_type'] = self.df_wind_farm_turbine.apply(
                lambda x: str(x.inner_turbine_type) if not x.inner_plat_form else '-'.join(
                    [str(x.inner_turbine_type), str(x.inner_plat_form)]), axis=1)
        except Exception as e:
            if 'inner_turbine_type' in self.df_wind_farm_turbine.columns:
                self.df_wind_farm_turbine['inner_plat_type'] = self.df_wind_farm_turbine['inner_turbine_type']
            else:
                self.df_wind_farm_turbine['inner_plat_type'] = self.df_wind_farm_turbine['type_name']
                self.df_wind_farm_turbine['inner_turbine_type'] = self.df_wind_farm_turbine['type_name']

    def get_rated_power_by_turbine(self, farm, turbine_num):
        """
        获取指定机组额定功率
        :param farm：需要查询的风场，例：'TYSFCA'
        :param turbine_num：需要查询的机组号，例：'001'
        :return：所查询机组的额定功率，例：2500
        """

        df_turbine = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_turbine_name == @turbine_num')
        if len(df_turbine) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {}_{} 机组信息'.format(farm, turbine_num)
        else:
            result = df_turbine['rated_power'].unique().tolist()[0]
            if str(result) not in ['nan', 'None']:
                result = float(result)
            else:
                result = '数据库表df_wind_farm_turbine中缺少 {}_{} 机组信息'.format(farm, turbine_num)

        return result

    def get_power_curve_by_turbine(self, farm, turbine_num):
        """
        获取指定机组理论功率曲线
        :param farm：需要查询的风场，例：'TYSFCA'
        :param turbine_num：需要查询的机组号，例：'001'
        :return：所查询机组的理论功率曲线,返回pandas.DataFrame,columns=['Wind', 'Power']
        """

        df_turbine = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_turbine_name == @turbine_num')
        if len(df_turbine) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {}_{} 机组信息'.format(farm, turbine_num)
        else:
            turbine_id = df_turbine['turbine_id'].values[0]
            farm_id = df_turbine['farm_id'].values[0]
            df_power_curve = self.df_turbine_type_powercurve.query('farm_id == @farm_id & turbine_id == @turbine_id')
            if len(df_power_curve) == 0:
                result = '数据库表turbine_type_powercurve中缺少 {}_{} 机组相关id信息'.format(farm, turbine_num)
            else:
                power_curve = df_power_curve['inner_power_curve'].unique().tolist()[0]
                if power_curve:
                    result = dict()
                    wind = list(json.loads(power_curve).keys())
                    wind = [float(x) for x in wind]
                    power = list(json.loads(power_curve).values())
                    power = [float(x) for x in power]
                    while power[-1] == 0:
                        power.pop()
                    wind = wind[:len(power)]
                    result['Wind'] = wind
                    result['Power'] = power
                    result = pd.DataFrame(result)
                else:
                    result = '数据库表turbine_type_powercurve中缺少 {}_{} 机组理论功率曲线信息'.format(farm, turbine_num)

        return result

    def get_types_by_farm(self, farm):
        """
        获取指定风场所有机型
        :param farm：需要查询的风场，例：'TYSFCA'
        :return：所查询风场的机型list
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        else:
            result = df_farm['inner_plat_type'].unique().tolist()
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {} 风场相关id信息'.format(farm)
        return result

    def get_turbines_by_farm(self, farm):
        """
        获取指定风场下所有机组号
        :param farm：需要查询的风场，例：'TYSFCA'
        :return：所查询风场下所有风机号list
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        else:
            result = df_farm['inner_turbine_name'].unique().tolist()
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
            else:
                result.sort()

        return result

    def get_turbines_by_type(self, farm, type_name):
        """
        获取指定风场与机型的所有机组号
        :param farm：需要查询的风场，例：'TYSFCA'
        :param type_name：需要查询的机型，例：'SE8715'
        :return：所查询风场与机型下所有风机号list
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_plat_type == @type_name')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        else:
            turbines = df_farm['turbine_id'].unique().tolist()
            result = df_farm.query('turbine_id in @turbines')['inner_turbine_name'].unique().tolist()
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {} 风场相关信息'.format(farm)
            else:
                result.sort()
        return result

    def get_type_by_turbine(self, farm, turbine_num):
        """
        获取指定机组型号
        :param farm：需要查询的风场，例：'TYSFCA'
        :param turbine_num：需要查询的机组号，例：'001'
        :return：所查询机型，例：'SE8715'
        """
        result = '未查询到{}机组信息'.format(turbine_num)
        turbine_types = self.get_types_by_farm(farm)
        if isinstance(turbine_types, str):
            result = turbine_types
        else:
            for turbine_type in turbine_types:
                type_turbines = self.get_turbines_by_type(farm, turbine_type)
                if isinstance(type_turbines, list):
                    if turbine_num in type_turbines:
                        return turbine_type
                    else:
                        continue
                else:
                    result = type_turbines
        return result

    def get_inner_type_by_turbine(self, farm, turbine_num):
        """
        获取指定机组内部机型号
        :param farm：需要查询的风场，例：'TYSFCA'
        :param turbine_num：需要查询的机组号，例：'001'
        :return：所查询机型，例：'SE8715'
        """
        result = '未查询到{}机组信息'.format(turbine_num)
        turbine_types = self.get_types_by_farm(farm)
        if isinstance(turbine_types, str):
            result = turbine_types
        else:
            for turbine_type in turbine_types:
                type_turbines = self.get_turbines_by_type(farm, turbine_type)
                if isinstance(type_turbines, list):
                    if turbine_num in type_turbines:
                        # 修改返回值
                        return turbine_type.split('-')[0]
                    else:
                        continue
                else:
                    result = type_turbines
        return result

    # 新增方法
    def get_platform_by_turbine(self, farm, turbine_num):
        """
        获取指定机组平台号
        :param farm：需要查询的风场，例：'TYSFCA'
        :param turbine_num：需要查询的机组号，例：'001'
        :return：所查询平台号，例：'C5'、'905'
        """
        result = '未查询到{}机组信息'.format(turbine_num)
        turbine_types = self.get_types_by_farm(farm)
        if isinstance(turbine_types, str):
            result = turbine_types
        else:
            for turbine_type in turbine_types:
                type_turbines = self.get_turbines_by_type(farm, turbine_type)
                if isinstance(type_turbines, list):
                    if turbine_num in type_turbines:
                        # 修改返回值
                        return turbine_type.split('-')[1] if '-' in turbine_type else ''
                    else:
                        continue
                else:
                    result = type_turbines
        return result

    def get_power_curve_by_type(self, farm, type_name):
        """
        获取指定风场、机型的理论功率曲线
        :param farm：需要查询的风场，例：'TYSFCA'
        :param type_name：需要查询的机组型号，例：'SE8715'
        :return：所查询机型的理论功率曲线,返回pandas.DataFrame,columns=['Wind', 'Power']
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_turbine_type == @type_name')
        if len(df_farm) == 0:
            df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_plat_type == @type_name')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {}_{} 型号机组信息'.format(farm, type_name)
        else:
            farm_id = df_farm['farm_id'].values[0]
            turbine_id = df_farm['turbine_id'].values[0]
            df_power_curve = self.df_turbine_type_powercurve.query(
                'farm_id == @farm_id & turbine_id == @turbine_id')
            if len(df_power_curve) > 0:
                power_curve = df_power_curve['inner_power_curve'].unique().tolist()[0]
                if power_curve:
                    result = dict()
                    wind = list(json.loads(power_curve).keys())
                    wind = [float(x) for x in wind]
                    power = list(json.loads(power_curve).values())
                    power = [float(x) for x in power]
                    while power[-1] == 0:
                        power.pop()
                    wind = wind[:len(power)]
                    result['Wind'] = wind
                    result['Power'] = power

                    result = pd.DataFrame(result)
                else:
                    result = '数据库表turbine_type_powercurve中缺少 {}_{} 型号机组理论功率曲线信息'.format(farm, type_name)
            else:
                result = '数据库表turbine_type_powercurve中缺少 {}_{} 型号机组相关信息'.format(farm, type_name)

        return result

    def get_chinese_name_by_farm(self, farm):
        """
        根据风场拼音名获取其中文名
        :param farm：需要查询的风场，例：'TYSFCA'
        :return：所查询风场的中文名，如果数据库中不存在中文名，则返回字符串'None'
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        else:
            result = str(df_farm['farm_name'].unique()[0])
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)

        return result

    def get_py_code_by_farm(self, chinese_name):
        """
        根据风场中文名获取其拼音名
        :param chinese_name：需要查询的风场的中文名，例：'太阳山二期'
        :return：所查询风场的拼音缩写，如果数据库中不存在拼音缩写，则返回字符串'None'
        """

        df_farm = self.df_wind_farm_turbine.query('farm_name == @chinese_name')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(chinese_name)
        else:
            result = str(df_farm['pinyin_code'].unique()[0])
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(chinese_name)

        return result

    def get_etl_type_by_farm(self, farm):
        """
        :param farm：需要查询的风场，例：'TYSFCA'
        :return：所查询风场下 {风机号: etl_type}
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm')
        if len(df_farm) == 0:
            type_result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        else:
            result = df_farm['inner_turbine_name'].unique().tolist()
            if str(result) in ['nan', 'None']:
                type_result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
            else:
                result.sort()
                type_result = dict([(turbine, df_farm.loc[df_farm['inner_turbine_name'] == turbine]['etl_type'].max())
                                    for turbine in result])

        return type_result

    def get_speed_by_turbine(self, farm, turbine):
        """
        :param farm: 需要查询的风场，例："TYSFCA"
        :param turbine: 需要查询的机组号，例："001"
        :return：所查询机组的额定转速和并网转速，返回pandas.DataFrame, columns = ['rated_speed', 'grid_speed']
        """

        df_turbine = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_turbine_name == @turbine')
        if len(df_turbine) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {}_{} 机组信息'.format(farm, turbine)
        else:
            rated_speed = df_turbine['rated_speed'].unique().tolist()[0]
            grid_speed = df_turbine['grid_speed'].unique().tolist()[0]
            if str(rated_speed) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {}_{} 额定转速信息'.format(farm, turbine)
            elif str(grid_speed) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {}_{} 并网转速信息'.format(farm, turbine)
            else:
                result = pd.DataFrame([[rated_speed, grid_speed]], columns=['rated_speed', 'grid_speed'])
        return result

    def get_pch2a_acc_by_turbine(self, farm, turbine):
        """
        :param farm: 需要查询的风场，例“TYSFCA”
        :param turbine: 需要查询的机组号，例"001"
        :return: 所查询机组的X通道加速度信号的传感器位置，返回str,前后/左右，缺失时默认前后
        """

        df_turbine = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_turbine_name == @turbine')
        if len(df_turbine) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {}_{} 机组信息'.format(farm, turbine)
        else:
            result = df_turbine['Pch2A_Acc'].unique().tolist()[0]
            if str(result) in ['nan', 'None']:
                result = '前后'
        return result

    def get_farm_id_by_farm(self, farm):
        """
        :param farm：需要查询的风场，例：'TYSFCB'
        :return：所查询风场的风场id
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        else:
            result = str(df_farm['farm_id'].unique()[0])
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        return result

    def get_turbine_id_by_turbine(self, farm, turbine):
        """
        :param farm: 需要查询的风场，例“TYSFCA”
        :param turbine: 需要查询的机组号，例"001"
        :return: 所查询机组风机编号
        """

        df_turbine = self.df_wind_farm_turbine.query('pinyin_code == @farm & inner_turbine_name == @turbine')
        if len(df_turbine) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {}_{} 机组信息'.format(farm, turbine)
        else:
            result = df_turbine['turbine_id'].unique().tolist()[0]
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {}_{} 机组信息'.format(farm, turbine)
        return result

    # scada_version
    def get_scada_version(self, farm):
        """
        获取指定风场scada版本
        :param farm: 需要查询的风场，例“TYSFCA”
        :return: 所查询风场scada版本
        """

        df_farm = self.df_wind_farm_turbine.query('pinyin_code == @farm')
        if len(df_farm) == 0:
            result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
        else:
            result = df_farm['scada_version'].iloc[0]
            if str(result) in ['nan', 'None']:
                result = '数据库表df_wind_farm_turbine中缺少 {} 风场信息'.format(farm)
            else:
                result = int(result)

        return result



class EsHandler(object):
    # This programme is to get label from es.
    PROGRAMME = 'EsHandler'
    VERSION = '1.0'

    """
    初始化数据库连接。
    :param url:es数据库访问路径 示例：'http://10.0.6.7:9200'
    :param index:es数据库-数据库名字 示例:'sany_data_label_update'
    """

    def __init__(self,
                 hdfs_url='http://10.162.80.7:50070;http://10.162.80.4:50070',
                 stub='cloud-data-service-test.sanywind.net:50051',
                 es_url='http://192.168.0.3:19200/',
                 hdfs_rpc_ip="10.162.80.7",
                 hdfs_rpc_port=8020,
                 meta_data_index="model_file",
                 cms_label_index='sany_cms_label'
                 ):
        self.es_url = es_url
        self.hdfs_url = hdfs_url
        self.hdfs_rpc_ip = hdfs_rpc_ip
        self.hdfs_rpc_port = hdfs_rpc_port
        self.cms_label_index = cms_label_index
        self.meta_data_index = meta_data_index
        self.stub = stub
        self.dt = DataTools()
        self.es_client = None
        self.pyarrow_client = None
        self.hdfs_client = None

    def init_clients(self, hadoop_home='/opt/hadoop'):
        if os.environ.get("HADOOP_HOME") is None:
            os.environ.setdefault('HADOOP_HOME', hadoop_home)
        try:
            self.es_client = Elasticsearch([self.es_url])
        except Exception as e:
            print("es连接错误")
        try:
            self.pyarrow_client = pa.hdfs.connect(host=self.hdfs_rpc_ip, port=self.hdfs_rpc_port)
        except:
            print("pyarrow连接hadoop错误,请配置jdk环境和hadoop环境")
        try:
            self.hdfs_client = HdfsClient(url=self.hdfs_url, )
        except:
            print("hdfs客户端连接错误")

    def get_cms_label(self, farm, turbine, start_time, end_time, label, point_name, sample_fre):
        """
            获取cms标签，传参如下
            :param farm:风场大写拼音代码  例如：'PTCFC'
            :param turbine:3位数字风机号 数字字符串 例如：'001'
            :param start_time 查询数据的起始时间，闭区间  格式为：''2022-02-01''
            :param end_time   查询数据的结束时间，闭区间  格式为：''2022-02-22''
            :param label 表征数据状态的标签 例如：无效工况数据、有效工况数据(并网工况)等，完全匹配，多词少词均查不到
            :param point_name 测点名称 例如：主轴承径向、齿轮箱二级行星内齿圈等，完全匹配，多词少词均查不到
            :param sample_fre 采样频率 数字字符串 例如：2560、5120等

            返回值如下：
            ①数据库连接超时：'数据库连接超时'
            ②未查到结果：'未查到结果'
            ③查到数据：返回封装为dataframe的信息
        """
        # 类似于sql的查询语句。range为区间查询；match为匹配查询，默认分词；字段带.keyword，表示完全匹配，不分词。
        query = {
            "bool": {
                "must": [
                    {"match": {"farm_name.keyword": farm}},
                    {"match": {"turbine_name.keyword": '#F' + turbine}},
                    {"range": {"signal_date": {"gte": start_time + '||/d', "lte": end_time + '||/d'}}},
                    {"match": {"csv_label.keyword": label}},
                    {"match": {"point_name.keyword": point_name}},
                    {"match": {"sample_fre.keyword": sample_fre + 'Hz'}}
                ]
            }
        }

        # 返回值除了包含所需的查询信息，还包含总命中数、查询时间等指标。
        # index:数据库
        # query:查询语句
        # size:最大返回数
        data = self.es_client.search(index=self.cms_label_index, query=query, size=10000)

        # 获取所需的查询信息
        result = data["hits"]["hits"]

        # 未查到数据则返回None
        if not result:
            return '未查到结果'

        # 封装为df
        df = pd.DataFrame(result)
        # 去掉'_index','_type','_id','_score'的'_'
        df.rename(columns={'_index': 'index', '_type': 'type', '_id': 'id', '_score': 'score'}, inplace=True)
        df_source = pd.DataFrame(df['_source'].tolist())
        del df['_source']
        df = pd.concat([df, df_source], axis=1)
        df.sort_values('signal_date', inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

    def get_files(self, data_type, farm, start_time, end_time, turbine=None):
        """
        从elasticsearch中获取指定风场、机组号、时间段、类型的数据
        @param farm: 风场中文拼音名（例如：DBCFC）
        @param data_type: 数据类型（history、event、second、fault、qd、cms, ems_log, qd-gslb)
        @param start_time: 数据开始时间（包含）, 例如：'2021-03-03'
        @param end_time: 数据结束时间（包含）， 例如：'2021-03-10'
        @param turbine: 机组号,list[str],可以省略，省略后将得到所有机组数据
        @return: 匹配到的所有文件列表
        """

        if not isinstance(turbine, list) and turbine is not None:
            print("请传入列表格式机组！")
            return []


        for str_time in [start_time, end_time]:
            if isinstance(str_time, str) and len(str_time) >= 10:
                str_time = str_time[:10] + ' 00:00:00'
                import datetime
                try:
                    _ = datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(e)
                    print('请检查时间格式，例如：2021-03-03')
                    return
            else:
                print('请检查时间格式，例如：2021-03-03')
                return

        start_time = start_time[:10] + ' 00:00:00'
        end_time = end_time[:10] + ' 23:59:59'
        results=[]
        if isinstance(turbine, list):
            for tb in turbine:
                docs = self.get_single_turbine(farm, tb, start_time, end_time, data_type)
                results.extend(docs)
        if not turbine:
            docs = self.get_all_turbines(farm, start_time, end_time, data_type)
            results.extend(docs)

        df = pd.DataFrame(results)
        if len(df) > 0:
            df_source = pd.DataFrame(df['_source'].tolist())
            return sorted(df_source['upload_path'].to_list())
        return []

    def get_point_map(self):
        """
        从hadoop上面读取点表得到相应的点表映射
        @return: map
        """
        try:
            path = '/tmp/config_point.json'
            with self.pyarrow_client.open(path, 'rb') as f:
                j = json.loads(f.read())
                df_point = pd.DataFrame(j['SE14125-1.5.2:V1.5.2'])
                df_point = df_point.loc[(df_point['variable_name_old'].notna()) &
                                        (df_point['variable_desc'].notna()) &
                                        (df_point['variable_name_old'] != '') &
                                        (df_point['variable_desc'] != '')]
                point_map = dict(zip(df_point['variable_name_old'].values, df_point['variable_desc'].values))
                return point_map
        except:
            return {}

    def get_single_turbine(self, farm, turbine, start_time, end_time, data_type):
        """
        从es中获取指定风场下面的单个机组的某个时间范围的文件路径列表
        @param farm: 风场中文拼音名（例如：DBCFC）
        @param turbine: 机组号，str，长度为三位 001
        @param start_time: 数据开始时间（包含）, 例如：'2021-03-03'
        @param end_time: 数据结束时间（包含）， 例如：'2021-03-10'
        @param data_type: 数据类型（history、event、second、fault、qd、cms, ems_log, qd-gslb)
        @return: 匹配到的所有文件列表
        """

        if data_type in ['history', 'event', 'sec', 'fault', 'qd', 'cms', 'ems_log', 'qd-qslb']:
            func_name = 'cos_file_index'
            file_type = data_type
        else:
            func_name = data_type
            file_type = 'model_file'
        query = {
            "bool": {
                "must": [
                    {"match": {"pinyin_code": farm}},
                    {"match": {"turbine_num": turbine}},
                    {"match": {"file_type": file_type}},
                    {"match": {"func_name": func_name}},
                    {"match": {"func_status": 'success'}},
                    {"range": {"date": {"gte": start_time, "lte": end_time}}},
                ]
            }
        }
        print(self.es_client)
        data = self.es_client.search(index=self.meta_data_index, query=query, size=10000, _source=['upload_path'])
        return data['hits']['hits']

    def get_all_turbines(self, farm, start_time, end_time, data_type):
        """
        从es中获取某个风场下面的全部机组的文件路径列表
        @param farm: 风场中文拼音名（例如：DBCFC）
        @param start_time: 数据开始时间（包含）, 例如：'2021-03-03'
        @param end_time: 数据结束时间（包含）， 例如：'2021-03-10'
        @return: 匹配到的所有文件列表
        """
        if data_type in ['history', 'event', 'sec', 'fault', 'qd', 'cms', 'ems_log', 'qd-qslb']:
            func_name = 'cos_file_index'
            file_type = data_type
        else:
            func_name = data_type
            file_type = 'model_file'

        query = {
            "bool": {
                "must": [
                    {"match": {"pinyin_code": farm}},
                    {"match": {"file_type": file_type}},
                    {"match": {"func_name": func_name}},
                    {"match": {"func_status": 'success'}},
                    {"range": {"date": {"gte": start_time, "lte": end_time}}},
                ]
            }
        }
        data = self.es_client.search(index=self.meta_data_index, query=query, size=10000, _source=['upload_path'])
        return data['hits']['hits']

    def get_data(self, files_list, columns=None, data_type=None):
        """
        根据文件的路径判断是从cos或者是hadoop上面拉取数据
        @param files_list: 拉取的文件列表
        @param columns: 选择需要读取的列（list 或者 None）
        @param data_type: 数据类型
        @return: pd.DataFrame
        """
        if not isinstance(files_list, list):
            return
        if len(files_list) == 0:
            return

        cos_files = [file for file in files_list if file.startswith("semi/data/")]
        hadoop_files = [file for file in files_list if not file.startswith("semi/data/")]
        if len(cos_files) > 0:
            res_df = self.get_data_from_cos(cos_files, columns=columns, data_type=data_type)
            return res_df

        if len(hadoop_files) > 0:
            res_df = self.get_data_from_hadoop(hadoop_files, columns=columns)
            return res_df

    def get_data_from_cos(self, files, columns=None, data_type=None):
        """
        从cos上面拉取数据，复用了 datatools 里面的函数
        @param files: 需要拉取的文件列表
        @param columns: 需要的读取的列
        @param data_type: 读取的数据类型
        @return: pd.DataFrame
        """
        df = self.dt.get_data(self.stub, files, columns=columns,
                              data_type=data_type,
                              point_map_is_local=False,
                              cloud_point_map=self.get_point_map())
        return df

    def get_data_from_hadoop(self, files, columns=None):
        """
        从 HADOOPFILESYSTEM 上面获取数据，根据文件的类型(csv/csv.gz/parquet)使用不同的客户端获取数据，
        其中读取hadoop上面的parquet文件用到了pyarrow,同时需要配置宿主机环境的jdk环境以配置hadoop环境，
        因为pyarrow要用到hadoop/lib 下面的jar包
        @param files: 获取的文件列表
        @param columns: 需要读取的列(list 或者 None)
        @return: pd.DataFrame
        """
        res = []
        point_map = self.get_point_map()
        if columns:
            c = [k for k, v in point_map.items() if v in columns]
            c = c + list(set(columns).difference(set(list(point_map.values()))))
        else:
            c = columns

        for file in files:
            if file.endswith(".csv.gz"):
                try:
                    with self.hdfs_client.read(file) as f:
                       df = pd.read_csv(f, compression='gzip', engine='c', usecols=c)
                       df = df.rename(columns=point_map)
                except Exception as e:
                       df = pd.DataFrame()

            elif file.endswith(".csv"):
                try:
                    with self.hdfs_client.read(file) as f:
                       df = pd.read_csv(f, compression='infer', engine='c', usecols=c)
                       df = df.rename(columns=point_map)
                except Exception as e:
                    df = pd.DataFrame()
            elif file.endswith(".parquet"):
                try:
                    with self.pyarrow_client.open(file, "rb") as f:
                        df = pd.read_parquet(f, columns=c)
                        df = df.rename(columns=point_map)
                except Exception as e:
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()
            res.append(df)
        df_res = pd.concat(res, axis=0)
        return df_res