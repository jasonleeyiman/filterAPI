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
    selectedSMS=[]
    unselectedSMS=[]
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
               selected_data={
                   "_id": S["_id"],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
                    "email": have_common_item(chinese_words,tasks)['email']
               }
               selectedSMS.append(selected_data)
           else:
               unselected_data={
                   "_id": S["_id"],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
               }
               unselectedSMS.append(unselected_data)
        else:
           english_words = S['smsBody'].split()
           if have_common_item(english_words,tasks)['status'] & common(english_words,keywords):
               selected_data={
                   "_id": S["_id"],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
                    "email": have_common_item(english_words,tasks)['email']
               }
               selectedSMS.append(selected_data)
           else:
               unselected_data={
                   "_id": S["_id"],
                    "phoneNo": S["phoneNo"],
                    "smsBody": S['smsBody'],
               }
               unselectedSMS.append(unselected_data)
    return jsonify({"selectedSMS":selectedSMS,"unselectedSMS":unselectedSMS})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)