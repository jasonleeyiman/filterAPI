from flask import Flask,jsonify,request
from pymongo import MongoClient
import jieba
app = Flask(__name__)
client=MongoClient('mongodb+srv://yimanlee529:0YecEwoxlHf2hfxv@moblieapp.nlzrhao.mongodb.net/')
db=client['MoblieApp']
SMS=db['SMS']
@app.route('/filter', methods=['POST'])
def filter():
    SMSs=list(SMS.find({'status': 0}))
    SMSList=[]
    data=request.get_json()
    tasks=data.get('tasks',[])
    keywords=data.get('keywords',[])
    def have_common_item(list1, list2):
        for i in list1:
            for j in list2:  
                if i in j["task"]:
                    return {"email": j['email'], "status": True}
        return {"email": "", "status": False}
    def common(list1, list2):
        for i in list1:
            for j in list2:  
                if i in j:
                    return True
        return False
    for S in SMSs:
        S['_id']=str(S['_id'])
        if any('\u4e00' <= char <= '\u9fff' for char in S['smsBody']):
           chinese_words = list(jieba.lcut(S['smsBody']))
           if have_common_item(chinese_words,tasks)['status'] & common(chinese_words,keywords):
               smsData={
                    "_id": S["_id"],
                    "smsID":S['smsID'],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
                    "email": have_common_item(chinese_words,tasks)['email'],
                    "selected": True
               }
               SMSList.append(smsData)
           else:
               smsData={
                    "_id": S["_id"],
                    "smsID":S['smsID'],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
                    "email": None,
                    "selected": False
                    
               }
               SMSList.append(smsData)
        else:
           english_words = S['smsBody'].split()
           if have_common_item(english_words,tasks)['status'] & common(english_words,keywords):
               smsData={
                    "_id": S["_id"],
                    "smsID":S['smsID'],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
                    "email": have_common_item(english_words,tasks)['email'],
                    "selected": True
               }
               SMSList.append(smsData)
           else:
               smsData={
                    "_id": S["_id"],
                    "smsID":S['smsID'],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
                    "email": None,
                    "selected": False
               }
               SMSList.append(smsData)
    return jsonify(SMSList)
# 在手機處於運行狀態時收到了一條SMS，插入MongoDB以及做篩選
@app.route('/filter/one/sms', methods=['POST'])
def filterOne():
    data=request.get_json()
    tasks=data.get('tasks',[])
    keywords=data.get('keywords',[])
    sms=data.get('sms',{})
    def have_common_item(list1, list2):
        for i in list1:
            for j in list2:  
                if i in j["task"]:
                    return {"email": j['email'], "status": True}
        return {"email": "", "status": False}
    def common(list1, list2):
        for i in list1:
            for j in list2:  
                if i in j:
                    return True
        return False
    sms_object={}
    if sms:
        result=SMS.insert_one(sms)
        inserted_id=str(result.inserted_id)
        if any('\u4e00' <= char <= '\u9fff' for char in sms['smsBody']):
            chinese_words = list(jieba.lcut(sms['smsBody']))
            if have_common_item(chinese_words,tasks)['status'] & common(chinese_words,keywords):
               sms_object={
                    "_id": inserted_id,
                    "smsID": sms['smsID'],
                    "phoneNo": sms["phoneNo"],
                    "smsBody": sms['smsBody'],
                    "email": have_common_item(chinese_words,tasks)['email'],
                    "selected": True
               }
            else:
                sms_object={
                    "_id": inserted_id,
                    "smsID": sms['smsID'],
                    "phoneNo": sms["phoneNo"],
                    "smsBody": sms['smsBody'],
                    "email": None,
                    "selected": False
               }
        else:
            english_words = sms['smsBody'].split()
            if have_common_item(english_words, tasks)['status']& common(english_words, keywords):
                sms_object={
                    "_id": inserted_id,
                    "smsID": sms['smsID'],
                    "phoneNo": sms["phoneNo"],
                    "smsBody": sms['smsBody'],
                    "email": have_common_item(english_words,tasks)['email'],
                    "selected": True
                }
            else:
                sms_object={
                    "_id": inserted_id,
                    "smsID": sms['smsID'],
                    "phoneNo": sms["phoneNo"],
                    "smsBody": sms['smsBody'],
                    "email": None,
                    "selected": False
                }
        return jsonify({"message": sms_object})
    else:
        return jsonify({"message": "SMS is empty"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)