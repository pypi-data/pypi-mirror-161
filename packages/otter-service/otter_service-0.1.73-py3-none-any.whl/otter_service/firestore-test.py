import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from datetime import datetime
from pytz import timezone
import pytz

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': os.environ.get("GCP_PROJECT_ID"),
})

db = firestore.client()
date_format = "%Y-%m-%d %H:%M:%S %Z"
date = datetime.now(tz=pytz.utc)
date = date.astimezone(timezone('US/Pacific'))
data = {
    'user': '543',
    'grade': 1.0,
    'section': '2',
    'lab': 'lab01',
    'date': date.strftime(date_format)
}
doc = db.collection("otter-test").add(data)[1]
doc_ref = db.collection("otter-test").document(f'{doc.id}')
doc = doc_ref.get()
print(doc.to_dict())
