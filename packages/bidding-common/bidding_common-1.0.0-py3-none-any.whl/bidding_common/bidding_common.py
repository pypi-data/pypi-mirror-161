import re
from cih_spider_tools.dbdriver import Dbdriver
# 根据公告id,更新其parse_status
def update_status(table_name,bidding_id,parse_status):
	spider_db = Dbdriver("yjy_Academe_Business_admin")
	spider_db.update(table_name, {"parse_status": parse_status},
						  [[["bidding_id", "=", bidding_id]]])



#将异常中标公告存入ctt_bidding_analysis_announcement_error中
def abnormal_announcement_processing(bidding_id,site,text,url,name):

	spider_db = Dbdriver("yjy_enterprise_test_admin")
	error_table = "ctt_bidding_analysis_announcement_error"
	error_dict = {'bidding_id':bidding_id,"site": site,'text':text, 'url':url,'parse_status':0,'name':name,}
	try:
		spider_db.insert_one(error_table, error_dict)
	except Exception as e:
		if "duplicate" not in str(e):
			raise e
