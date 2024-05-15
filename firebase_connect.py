import re
import locale
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
import json

class FireBase:
    def _init_(self, certificate_path:str=''):
        # Initialize Firebase
        self.cred = credentials.Certificate(certificate_path)
        initialize_app(self.cred)

        # Get a reference to the Firestore database
        self.db = firestore.client()
        return

    def is_today(self, date):
        # Remove day name from date string
        date = re.sub(r'.*, ', '', date).strip()

        # Set locale to read Indonesion Month
        locale.setlocale(locale.LC_TIME, "id_ID.UTF-8")

        date_obj = datetime.strptime(date, "%d %B %Y").date()
        today = datetime.now().date()
        return date_obj == today

    def get_data(self, user_id):
        data = {'user_id': user_id}
        
        # Data From Diary
        diary_ref = self.db.collection(user_id+'_diary')
        diary_data = None
        for diary in diary_ref.stream():
            if(self.is_today(diary.to_dict()['diaryDate'])):
                diary_data = diary.to_dict()
                break
        
        if (diary_data != None):
            data['diary_date'] = diary_data.get('diaryDate', None)
            data['activities'] = diary_data.get('activities', None)
            data['body_metrics'] = diary_data.get('bodyMetrics', None)
            data['consumptions'] = diary_data.get('consumptions', None)

        # Data From Profile
        user_data = self.db.collection('user').document(user_id).get()
        if user_data.exists:
            user_data = user_data.to_dict()
        else:
            user_data = {}

        data['birth_date'] = user_data.get('birth_date', None)
        data['have_smoked'] = user_data.get('haveSmoked', None)
        data['have_smoked_ecigarette'] = user_data.get('haveSmokedECigarette', None)
        data['sleep_time'] = user_data.get('sleepTime', None)
        data['wake_time'] = user_data.get('wakeTime', None)

        data_json = json.dumps(data)

        return data_json

    



