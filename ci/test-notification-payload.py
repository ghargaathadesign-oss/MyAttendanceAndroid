"""Verify production pushes reach the app's receive handler without duplicate topics."""
import os,sys,types,runpy,json
from unittest.mock import patch
calls=[]
class Credentials:
    token='test-token'
    @classmethod
    def from_service_account_info(cls,*a,**kw):return cls()
    def refresh(self,*a):pass
class Response:
    ok=True
    def json(self):return {'name':'test-accepted'}
def post(url,**kw):calls.append(kw['json']['message']);return Response()
mods={'requests':types.SimpleNamespace(post=post),'google':types.ModuleType('google'),'google.auth':types.ModuleType('google.auth'),'google.auth.transport':types.ModuleType('google.auth.transport'),'google.auth.transport.requests':types.SimpleNamespace(Request=lambda:None),'google.oauth2':types.ModuleType('google.oauth2'),'google.oauth2.service_account':types.SimpleNamespace(Credentials=Credentials)}
env={'FIREBASE_SERVICE_ACCOUNT_JSON':json.dumps({'project_id':'test'}),'UPDATE_VERSION':'15.5.10','UPDATE_VERSION_CODE':'44','UPDATE_APK_URL':'https://example.com/test.apk','UPDATE_APK_SHA256':'a'*64,'FCM_TOPIC':'attendance_updates'}
with patch.dict(sys.modules,mods),patch.dict(os.environ,env):runpy.run_path('ci/send_update_fcm.py')
assert len(calls)==1,'One notification per subscribed device channel'
m=calls[0];assert 'notification' not in m and 'notification' not in m['android']
assert m['android']['priority']=='high' and m['data']['id']=='update-44'
assert m['data']['versionCode']=='44' and m['topic']=='attendance_updates'
print('Notification payload checks passed')
