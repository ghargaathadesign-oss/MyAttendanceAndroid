from pathlib import Path
import sys,shutil,json
p=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
def rep(s,a,b):
 if a not in s:raise SystemExit('Missing v15526 anchor '+a[:100])
 return s.replace(a,b,1)
h=(p/'index.html').read_text()
# Insert options with explicit values so translated labels never change stored statuses.
h=h.replace('<option>Half Day</option>','<option>Half Day</option><option value="Half Day Holiday">Half Day Holiday</option>')
for prefix,status in [('holiday26','statusInput'),('editHoliday26','editPopupStatus')]:
 anchor='<select id="'+status+'"';a=h.index(anchor);b=h.index('</select></div>',a)+len('</select></div>')
 control='''<div class="holidayTarget26" id="PREFIX" hidden><div class="label">Work target for full-day credit</div><div class="targetFields26"><label>Hours<input id="PREFIXHours" type="number" inputmode="numeric" min="0" max="23" step="1" aria-label="Required working hours"></label><label>Minutes<input id="PREFIXMinutes" type="number" inputmode="numeric" min="0" max="59" step="1" aria-label="Required working minutes"></label></div><p>Complete this work target for a full paid day. The remaining time is holiday; paid leave is not used. Any work shortfall reduces pay proportionally.</p></div>'''.replace('PREFIX',prefix)
 h=h[:b]+control+h[b:]
for id in ['checkInRow','editInRow']:
 a=h.index('id="'+id+'"');b=h.rfind('<div class="row2">',0,a);assert b>=0
 h=h[:b]+h[b:].replace('<div class="row2">','<div class="row2 punchFields26">',1)
h=h.replace('</head>','<link rel="stylesheet" href="v15526-attendance.css"></head>',1)
(p/'index.html').write_text(h)
f=p/'app.js';s=f.read_text();helper='''function holidayTargetSync26(edit,record){var prefix=edit?'editHoliday26':'holiday26',status=E(edit?'editPopupStatus':'statusInput');E(prefix).hidden=status.value!=='Half Day Holiday';if(record||E(prefix+'Hours').value===''){var minutes=record&&record.holidayWorkMinutes?record.holidayWorkMinutes:Math.round(AttendancePolicy.standardMinutes(setGet())/2);E(prefix+'Hours').value=Math.floor(minutes/60);E(prefix+'Minutes').value=minutes%60}}
function holidayTargetRead26(record,edit){if(record.status!=='Half Day Holiday')return true;var prefix=edit?'editHoliday26':'holiday26',hr=E(prefix+'Hours').value,mi=E(prefix+'Minutes').value,h=Number(hr),m=Number(mi),total=h*60+m;if(hr===''||mi===''||!Number.isInteger(h)||!Number.isInteger(m)||h<0||h>23||m<0||m>59||total<1||total>AttendancePolicy.standardMinutes(setGet())){toast('Enter a work target greater than zero and no longer than your standard workday');return false}record.holidayWorkMinutes=total;return true}
'''
s=rep(s,'function statusChanged(){',helper+'function statusChanged(){holidayTargetSync26(false);')
s=rep(s,"syncLeaveCategory();triggerControlChange('leaveCategoryInput')}","syncLeaveCategory();E('holiday26Hours').value='';holidayTargetSync26(false);triggerControlChange('leaveCategoryInput')}")
s=rep(s,"for(i=0;i<a.length;i++)if(a[i].id===e.id){idx=i;break}","if(!holidayTargetRead26(e,false))return;for(i=0;i<a.length;i++)if(a[i].id===e.id){idx=i;break}")
s=rep(s,"E('editPopupNotes').value=x.notes||'';ids=", "E('editPopupNotes').value=x.notes||'';holidayTargetSync26(true,x);ids=")
s=rep(s," if(isSundayDate(updated.date)){updated.status='Week Off';updated.specialOT=true}"," if(!holidayTargetRead26(updated,true))return false;\n if(isSundayDate(updated.date)){updated.status='Week Off';updated.specialOT=true}")
s=rep(s,"E('punchBtn').onclick=punch;", "E('editPopupStatus').addEventListener('change',function(){holidayTargetSync26(true)});E('punchBtn').onclick=punch;")
s=rep(s,"for(i=0;i<a.length;i++)if(a[i].date===date){x=a[i];break}\n if(!x){x=", "for(i=0;i<a.length;i++)if(a[i].date===date){x=a[i];break}\n if(x&&x.status==='Half Day Holiday'&&!sunday)flagged=false;\n if(!x){x=")
s=rep(s,"else if(x.status!=='Holiday'&&x.status!=='Week Off'){x.status='Present';x.specialOT=false}","else if(x.status!=='Holiday'&&x.status!=='Week Off'&&x.status!=='Half Day Holiday'){x.status='Present';x.specialOT=false}")
s=rep(s,"x.checkIn=t;x.checkOut='';x.status=def;","x.checkIn=t;x.checkOut='';if(x.status!=='Half Day Holiday'||sunday||flagged)x.status=def;")
s=s.replace("'Half Day':'half',","'Half Day':'half','Half Day Holiday':'halfholiday',")
f.write_text(s)
# Preserve the visible holiday status while all summaries count the completed target as a full day.
for name in ['v15-features.js','v14-features.js']:
 f=p/name;s=f.read_text().replace("'Half Day':'half',","'Half Day':'half','Half Day Holiday':'halfholiday',").replace("'Half Day':'HD',","'Half Day':'HD','Half Day Holiday':'HDH',")
 s=s.replace("x.status==='Present'||x.status==='Half Day'||x.status==='Short Day'","x.status==='Present'||x.status==='Half Day'||x.status==='Short Day'||x.status==='Half Day Holiday'")
 f.write_text(s)
f=p/'v15521-home.js';s=f.read_text();s=rep(s,"if(st==='Half Day')partial++;\n  else if(st==='Present')present++;", "if(st==='Half Day Holiday'){if(d.pending||AttendancePolicy.workedMinutes(r)>=AttendancePolicy.requiredMinutes(r,settings))present++;else partial++;}\n  else if(st==='Half Day')partial++;\n  else if(st==='Present')present++;");f.write_text(s)
f=p/'v112-fixes.js';s=f.read_text().replace("if(st==='Paid Leave'||st==='Holiday')return'FFE5EDFF'","if(st==='Paid Leave'||st==='Holiday'||st==='Half Day Holiday')return'FFE5EDFF'");f.write_text(s)
f=p/'v1559-salary.js';s=f.read_text();s=rep(s,"if(r.status==='Holiday')hol++;","if(r.status==='Holiday')hol++;if(r.status==='Half Day Holiday')hol+=1-AttendancePolicy.requiredMinutes(r,A().setGet())/AttendancePolicy.standardMinutes(A().setGet());");s=rep(s,"hol+' / '+off","num(hol)+' / '+off");f.write_text(s)
shutil.copy('ci/v15526-attendance.css',p/'v15526-attendance.css')
# Add translations to the already-built dictionary without touching earlier patch anchors.
f=p/'v15515-i18n.js';s=f.read_text();dictionary={'Half Day Holiday':'आधा दिन छुट्टी','Work target for full-day credit':'पूरे दिन के वेतन हेतु कार्य समय','Required working hours':'आवश्यक कार्य घंटे','Required working minutes':'आवश्यक कार्य मिनट','Complete this work target for a full paid day. The remaining time is holiday; paid leave is not used. Any work shortfall reduces pay proportionally.':'पूरे दिन का वेतन पाने के लिए निर्धारित कार्य समय पूरा करें। शेष समय छुट्टी है; सवेतन अवकाश नहीं कटेगा। कम काम करने पर वेतन अनुपात में कम होगा।','Enter a work target greater than zero and no longer than your standard workday':'शून्य से अधिक और सामान्य कार्यदिवस से कम या बराबर कार्य समय दर्ज करें'}
s=rep(s,'Object.keys(dictionary)', 'Object.assign(dictionary,'+json.dumps(dictionary,ensure_ascii=False)+');\nObject.keys(dictionary)');f.write_text(s)
print('v15.5.26 half-day holiday target, full-day salary credit and stacked punches prepared')
