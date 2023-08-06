#!/usr/bin/python
# -*- coding: utf-8 -*-
# 同步cih表到cm表

import datetime
import re
import traceback
from cih_spider_tools.dbdriver import Dbdriver




class SyncBiddingData(object):
    """
    将cih的bidding的表同步到cm的千里马投标的表中
    """

    error_log_table = "cih_cih2cm_sync_log"

    def __init__(self, city):
        self.city = city
        self.name='bidding_{}'.format(self.city)
        self.spider_db = Dbdriver("yjy_Academe_DataSpider_w")
        self.business_db = Dbdriver("yjy_Academe_Business_w")
        self.src_desc_table='cih_{}_desc'.format(self.name)
        self.src_excel_table = 'cih_{}_announce_detail'.format(self.name)
        self.src_file_table='cih_{}_file'.format(self.name)

    # 清洗公告详情信息
    def clean_bidding_announce_detail_data(self,data):

        # 1.清洗发布时间
        publish_time = data.get('publish_time')
        text_list = publish_time.split(' ')
        publish_date = text_list[0]
        data['publish_time'] = publish_date

        # 2.清洗地区
        site = data.get('site')
        district = ''
        if site == 'bidding_changchun':
            district = '吉林省'
            title = data['title']
            if title is not None:
                if '长春' in title or '公主岭' in title or '榆树市' in title or '九台区' in title or '绿园区' in title or '朝阳' in title or '双阳' in title \
                        or '南关' in title or '宽城' in title or '净月' in title or '乐山镇' in title or '德惠' in title or '桃源街道' in title or '红旗街道' in title \
                        or '全安街道' in title or '富裕街道' in title or '南岭街道' in title or '新春街道' in title or '农安县' in title or '鸿城街道' in title or '锦程街道' in title \
                        or '东盛街道' in title or '林园街道' in title or '吉林街道' in title or '鸿城街道' in title or '二道' in title or '永春镇' in title or '八里堡街道' in title \
                        or '远达街道' in title or '荣光街道' in title or '集安市' in title or '泉眼镇' in title or '边岗乡' in title or '新立城镇' in title or '莲花山' in title \
                        or '湖西街道' in title or '大岭' in title or '双营乡' in title or '达家沟镇' in title or '兰家镇' in title or '春城街道' in title or '毛城子镇' in title \
                        or '博硕街道' in title or '红梅街' in title or '重庆街道' in title or '大榆树镇' in title or '响水镇' in title or '前程街道' in title or '柳影街道' in title \
                        or '合隆' in title or '桂林街道' in title or '岔路口镇' in title or '波泥河街道' in title or '范家屯镇' in title or '三盛玉镇' in title or '彩织街道' in title \
                        or '靠山镇' in title or '富民街道' in title or '布海镇' in title or '天台镇' in title or '万宝镇' in title or '新湖镇' in title or '普阳街道' in title \
                        or '兴隆山镇' in title or '太平镇' in title or '前进街道' in title or '天台镇' in title or '万宝镇' in title or '新湖镇' in title or '普阳街道' in title:
                    district = district + '长春市'
                elif '通化' in title or '东昌区' in title or '梅河口' in title or '集安市' in title:
                    district = district + '通化市'
                elif '延边' in title or '安图' in title:
                    district = district + '延边朝鲜族自治州'
                elif '白山' in title or '靖宇县' in title:
                    district = district + '白山市'
                elif '长岭县' in title or '松原市' in title:
                    district = district + '松原市'
                elif '辽源' in title or '东丰' in title:
                    district = district + '辽源市'
                elif '四平' in title or '伊通满族自治县' in title:
                    district = district + '四平市'
                elif '桦甸市' in title or '吉林市' in title or '永吉' in title or '磐石市' in title or '舒兰市' in title:
                    district = district + '吉林市'
                elif '洮南市' in title or '白城市' in title or '镇赉县' in title or '延吉市' in title or '通榆' in title:
                    district = district + '白城市'


        elif site == 'bidding_haerbin':
            district = '黑龙江哈尔滨市'
        elif site == 'bidding_shenyang':
            district = '辽宁省沈阳市'
        elif site == 'bidding_dalian':
            district = '辽宁省大连市'
        else:
            raise Exception("异常站点，需要补充地区映射！")

        data['district'] = district

        # 3.清洗编号
        number = data.get('number')
        if number is not None:
            number = number.replace('1.3资金来源：财政资金', '').replace('（二次）', '').replace('1包：', '')
            number = number.replace('【', '[').replace('】', ']').replace('（', '(').replace('）', ')').replace('－',
                                                                                                            '-').replace(
                ' ', '').replace('：', '').replace(':', '')
            number_list = re.findall(r'[\[\]\d()\-/a-zA-Z—\.]+', number)
            number = ''
            if len(number_list) > 0:
                number = number_list[0]

        data['number'] = number

        # 4.清洗供应商
        winner = data.get('winner')
        if winner is not None:
            winner = winner.replace('、', ',')
            winner = re.sub(r'公司(?!,).*', '公司', winner)
            winner = re.sub(r'供应商.*', '', winner)
            winner = re.sub(r'统一社会信用代码.*', '', winner)
            if '为满足长春市规划' in winner:
                winner = ""
            if winner.replace(',', '').strip() == "":
                winner = ""
            winner = winner.replace('1,单位名称', '').replace('中标', '').strip('；').strip(';').strip(':').strip('：').strip(
                "》")
            winner = re.sub(r'\d+\.', '', winner)
        else:
            winner = ''

        data['winner'] = winner.strip()

        # 5.清洗成交金额
        winning_amount = data.get('winning_amount')
        if winning_amount is not None:
            if '单' in winning_amount or '费' in winning_amount or '系数' in winning_amount or '每' in winning_amount or '餐' in winning_amount \
                    or '/' in winning_amount or '率' in winning_amount or '比例' in winning_amount or '路' in winning_amount or '一' in winning_amount \
                    or '服务时间' in winning_amount or '2020—0115—01' in winning_amount or '挖掘机' in winning_amount or '保险' in winning_amount or '号' in winning_amount \
                    or '住宅' in winning_amount or '定点' in winning_amount or "集中采购" in winning_amount or "公司" in winning_amount or '无' in winning_amount \
                    or "据实结算" in winning_amount or "大写" in winning_amount or "项目" in winning_amount or "肆佰零捌" in winning_amount or "定点" in winning_amount:
                winning_amount = None
            else:
                winning_amount = re.sub(r'.*?￥', '', winning_amount)
                winning_amount = winning_amount.replace('人民币', '')
                find = re.findall(r'[\d\.]+', winning_amount)
                if find is not None and len(find) > 0:
                    winning_amount = ','.join(find)

        if winning_amount is None or winning_amount.replace(',', '').strip() == "":
            winning_amount = ''
        data['winning_amount'] = winning_amount.strip()
        # 6.清洗招标单位
        organization = data.get('organization')
        if organization is not None:
            organization = re.sub(r'联\s*系\s*人.*', '', organization)
            organization = re.sub(r'招标代理机构.*', '', organization)
            organization = re.sub(r'统一社会信用代码.*', '', organization)
            organization = re.sub(r'统一信用代码.*', '', organization)
            organization = re.sub(r'信用代码.*', '', organization)
            organization = re.sub(r'地\s*址.*', '', organization)
            organization = re.sub(r'采购人.*', '', organization)
            organization = re.sub(r'\d+\..*', '', organization)
            organization = organization.replace('&#13;', '')
            organization = re.sub(r'统一代码.*', '', organization)
            organization = re.sub(r'代建单位.*', '', organization)
            organization = re.sub(r'姓名.*', '', organization)
            organization = re.sub(r'信用代码.*', '', organization)
            organization = re.sub(r'联系方式.*', '', organization)
            organization = re.sub(r'招标代理机构.*', '', organization)
            organization = re.sub(r'六、.*', '', organization)
            organization = re.sub(r'[？]+', '', organization)
            organization = re.sub(r'采购人.*', '', organization)
            organization = re.sub(r'采购单位.*', '', organization)
            organization = re.sub(r'二、.*', '', organization)
            organization = re.sub(r'询价公告.*', '', organization)
            organization = re.sub(r'采购代理机构.*', '', organization)
            organization = re.sub(r'组织机构代码.*', '', organization)
            organization = re.sub(r'供应商代码.*', '', organization)

            organization = organization.strip()
        if organization is None:
            organization = ''
        data['organization'] = organization.strip()
        return data

    # 把数据转换成千里马desc表的类型
    def convert_bidding_desc_data(self,data):
        result = dict()
        result['id'] = data['id']
        result['bidding_id'] = data['bidding_id']
        result['bidding_desc'] = data['text']
        result['url'] = data['url']
        result['md5'] = data['md5']
        result['create_time'] = data['create_time']
        result['update_time'] = data['update_time']
        result['batchnum'] = data['batchnum']
        result['sync_status'] = data['sync_status']
        result['is_file'] = data['is_file']
        return result

    # 把数据转换成千里马announce_detail表的类型
    def convert_bidding_announce_detail_data(self,data):
        data = self.clean_bidding_announce_detail_data(data)
        result = dict()
        result['id'] = data['id']
        result['bidding_id'] = data['bidding_id']
        result['title'] = data['title']
        result['publish_date'] = data['publish_time']
        result['bidding_no'] = data['number']
        result['bidding_endtime'] = ''
        result['district'] = data['district']
        result['data_type'] = '招标结果'
        result['bidding_unit'] = data['organization']
        result['bidding_contact'] = ''
        result['bidding_contact_no'] = ''
        result['bidding_agency'] = ''
        result['bidding_agency_contact'] = ''
        result['bidding_agency_contact_no'] = ''
        result['bidding_winner'] = data['winner']
        result['bidding_winner_contact'] = ''
        result['bidding_winner_contact_no'] = ''
        result['evaluation_price'] = ''
        result['winning_amount'] = data['winning_amount']
        result['reviewer'] = ''
        result['url'] = data['url']
        result['md5'] = data['md5']
        result['create_time'] = data['create_time']
        result['update_time'] = data['update_time']
        result['sync_status'] = data['sync_status']
        result['is_del'] = 0
        result['batchnum'] = data['batchnum']
        return result

    # 把数据转换成千里马file_data表的类型
    def convert_bidding_file_data(self,data):
        result = dict()
        result['id'] = data['id']
        result['bidding_id'] = data['bidding_id']
        result['file_url'] = data['file_url']
        result['ext_name'] = data['ext_name']
        result['file_md5'] = data['file_md5']
        result['url'] = data['url']
        result['md5'] = data['md5']
        result['create_time'] = data['create_time']
        result['update_time'] = data['update_time']
        result['batchnum'] = data['batchnum']
        result['sync_status'] = data['sync_status']
        result['file_name'] = data['file_name']
        return result

    # 将源表数据转换成千里马对应表的类型
    def convert_data(self,src_table, data):
        if src_table == 'cih_{}_desc'.format(self.name):
            return self.convert_bidding_desc_data(data)
        elif src_table == 'cih_{}_announce_detail'.format(self.name):
            return self.convert_bidding_announce_detail_data(data)
        elif src_table == 'cih_{}_file'.format(self.name):
            return self.convert_bidding_file_data(data)
        else:
            raise Exception("缺少源表转换函数！")

    def get_src_data(self, src_table):
        """
        获取未同步数据
        :param src_table:数据来源表
        :return:
        """
        where = [[["sync_status", "=", 0]]]
        columns = ["top 100 *"]
        return self.business_db.get_all(src_table, where, columns)

    def check_exist(self, dst_table, unique_dict):
        """
        检查目标表记录是否存在

        :param dst_table:
        :param unique_dict:
        :return:
        """
        where = [[[key, "=", value] for key, value in unique_dict.items()]]
        return self.spider_db.get_one(dst_table, where)

    def update_data(self, dst_table, unique_dict, data):
        """
        更新数据
        :param dst_table: 目标表
        :param unique_dict: 搜索条件
        :param data: 更新的数据
        :return:
        """

        for key in unique_dict:
            del data[key]
        where = [[[key, "=", value] for key, value in unique_dict.items()]]
        self.spider_db.update(dst_table, data, where)

    def insert_data(self, dst_table, data):
        """
        向目标表插入数据
        :param dst_table:目标表
        :param data:数据
        :return:
        """
        self.spider_db.insert_one(dst_table, data)

    def update_sync_status(self, src_table, primary_key, sync_status):
        """
        更新源表同步状态
        :param src_table:来源表
        :param primary_key: 主键
        :param sync_status: 同步状态码
        :return:
        """
        value_dict = dict({
            "sync_status": sync_status
        })
        where = [[["id", "=", primary_key]]]
        self.business_db.update(src_table, value_dict=value_dict, where=where)

    def insert_error_log(self, table_name, data_id, error_message):
        """
        插入错误日志
        :param table_name:表名
        :param data_id: 数据id
        :param error_message:错误信息
        :return:
        """

        value_dict = dict({
            "city": self.city,
            "table_name": table_name,
            "data_id": data_id,
            "error_message": error_message
        })
        self.business_db.insert_one(self.error_log_table, value_dict)


    def sync_table(self, src_table, dst_table, unique_key):
        """
        将源表和目标表按唯一键同步
        :param src_table:
        :param dst_table:
        :param unique_key:
        :return:
        """
        data_list = self.get_src_data(src_table)
        print(len(data_list))
        while len(data_list) > 0:
            print(len(data_list))
            for data in data_list:
                primary_key = ""
                try:
                    primary_key = data['id']
                    data = self.convert_data(src_table, data)
                    data['sync_status'] = 0
                    if 'create_time' in data:
                        del data['create_time']
                    if 'update_time' in data:
                        del data['update_time']
                    if 'id' not in unique_key:
                        del data['id']
                    if 'batchnum' not in unique_key:
                        del data['batchnum']

                    unique_dict = {key: data[key] for key in unique_key}


                    exist = self.check_exist(dst_table, unique_dict)
                    if exist:
                        self.update_data(dst_table, unique_dict, data)
                    else:
                        self.insert_data(dst_table, data)
                    self.update_sync_status(src_table, primary_key, 2)
                except Exception:
                    self.update_sync_status(src_table, primary_key, 3)
                    error_message = traceback.format_exc()
                    print(error_message)
                    self.insert_error_log(src_table, primary_key, error_message)
            #data_list=[]
            data_list = self.get_src_data(src_table)

    def sync_data(self,mode='production'):

        # 同步中标公告描述
        src_table = self.src_desc_table
        dst_table = "cm_qianlima_desc"
        if mode=='test':
            dst_table=dst_table+'_test'
        unique_key = ['bidding_id']
        self.sync_table(src_table, dst_table, unique_key)
        print("中标公告描述表同步成功！")

        # 同步中标公告详情
        src_table = self.src_excel_table
        dst_table = "cm_qianlima_excel"
        if mode=='test':
            dst_table=dst_table+'_test'
        unique_key = ['bidding_id']
        self.sync_table(src_table, dst_table, unique_key)
        print("中标公告详情表同步成功！")

        # 同步中标公告文件
        src_table = self.src_file_table
        dst_table = "cm_qianlima_file"
        if mode=='test':
            dst_table=dst_table+'_test'
        unique_key = ['bidding_id', 'file_md5']
        self.sync_table(src_table, dst_table, unique_key)
        print("中标公告文件表同步成功！")

if __name__=="__main__":
    city='changchun'
    sync = SyncBiddingData(city)
    sync.sync_data(mode='test')



