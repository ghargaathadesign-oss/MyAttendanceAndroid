(function(){
'use strict';
var selected='',selectedName='',selectedEmail='',owner=!!(window.attendanceInitialAuth&&attendanceInitialAuth.supportOwner),tab='help',busy=false,loaded=false,timer=null,messages=[],threads=[];
function E(id){return document.getElementById(id)}
function t(s){return window.AttendanceI18n?AttendanceI18n.t(s):s}
function status(s){E('supportStatus').textContent=t(s)}
function active(){return E('screen-setting-help').classList.contains('active')&&!document.hidden&&tab!=='help'}
function bridge(method,args){if(!window.Android||typeof Android[method]!=='function'){status('Chat is available in the Android app.');return false}try{Android[method]((args||[])[0]||'',(args||[])[1]||'');return true}catch(e){status('Could not connect. Try again.');return false}}
function refresh(){if(busy)return;busy=true;status('Loading messages…');if(!bridge('supportLoad',[selected]))busy=false}
function setTab(next){if(next==='messages'&&!owner)return;tab=next==='help'?'help':owner?'messages':'chat';render();enter()}
function render(){
 E('supportAdminMessagesTab').hidden=!owner;E('supportChatTab').hidden=owner;
 if(tab!=='help')tab=owner?'messages':'chat';
 ['help','chat','messages'].forEach(function(key){var el=E(key==='help'?'supportHelpTab':key==='chat'?'supportChatTab':'supportAdminMessagesTab');el.setAttribute('aria-selected',String(tab===key));el.tabIndex=tab===key?0:-1});
 E('supportHelpPanel').hidden=tab!=='help';E('supportChatPanel').hidden=tab==='help';E('supportChatPanel').setAttribute('aria-labelledby',owner?'supportAdminMessagesTab':'supportChatTab');
 E('supportContactTitle').textContent=t(owner?'Support inbox':'Need more help?');E('supportContactText').textContent=t(owner?'Read and reply to user messages.':'Your conversation stays private between you and support.');E('supportOpenChat').textContent=t(owner?'Open messages':'Start chat');
 var inbox=owner&&!selected;
 E('supportTitle').textContent=t(inbox?'Received messages':owner?'Conversation':'Chat with support');E('supportSubtitle').textContent=t(inbox?'Choose a conversation to reply.':'Messages are shared only with support.');
 E('supportInbox').hidden=!inbox;E('supportForm').hidden=inbox;E('supportMessages').hidden=inbox;E('supportClear').hidden=inbox;E('supportBack').hidden=!owner||inbox;E('supportConversation').hidden=inbox;
 E('supportChatPerson').textContent=owner?(selectedName||selectedEmail||t('User')):t('Support');E('supportChatEmail').textContent=owner?selectedEmail:t('Private conversation');E('supportChatAvatar').textContent=owner?(selectedName||selectedEmail||'U').slice(0,1).toUpperCase():'S';
 if(inbox){var box=E('supportInbox');box.replaceChildren();threads.forEach(function(thread){var b=document.createElement('button');b.type='button';b.className='supportThread';b.setAttribute('data-no-translate','');var avatar=document.createElement('span');avatar.className='supportThreadAvatar';avatar.textContent=(thread.name||thread.email||'U').slice(0,1).toUpperCase();var copy=document.createElement('span');copy.className='supportThreadCopy';var name=document.createElement('b');name.textContent=thread.name||thread.email||t('User');var detail=document.createElement('small');detail.textContent=thread.email||thread.uid;copy.append(name,detail);var arrow=document.createElement('span');arrow.textContent='›';b.append(avatar,copy,arrow);b.onclick=function(){if(busy)return;selected=thread.uid;selectedName=thread.name||'';selectedEmail=thread.email||'';messages=[];loaded=false;render();refresh()};box.appendChild(b)});if(!threads.length){var empty=document.createElement('div');empty.className='supportEmpty';empty.textContent=t('No help chats yet.');box.appendChild(empty)}return}
 var box=E('supportMessages'),bottom=box.scrollHeight-box.scrollTop-box.clientHeight<40;box.replaceChildren();messages.forEach(function(m){var item=document.createElement('div');item.className='supportBubble'+(m.mine?' mine':'');item.setAttribute('data-no-translate','');item.textContent=m.text;var caption=document.createElement('small');caption.textContent=t(m.mine?'You':m.support?'Support':'User')+' · '+new Date(m.createdAt).toLocaleString(document.documentElement.lang==='hi'?'hi-IN':'en-IN',{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});item.appendChild(caption);box.appendChild(item)});if(!messages.length){var empty=document.createElement('div');empty.className='supportEmpty';empty.textContent=t('No messages yet. Ask your first question below.');box.appendChild(empty)}if(bottom)box.scrollTop=box.scrollHeight;
}
window.onSupportState=function(payload){busy=false;var data;try{data=JSON.parse(payload)}catch(e){status('Could not load messages. Try again.');return}if(!data.ok){status(data.error||'Could not connect. Try again.');return}owner=!!data.owner;threads=data.threads||[];messages=data.messages||[];loaded=true;render();status('Messages are up to date.');};
window.onSupportSent=function(ok,error){busy=false;E('supportSend').disabled=false;if(ok){E('supportText').value='';refresh()}else status(error||'Message was not sent. Try again.');};
window.onSupportCleared=function(ok,error){busy=false;if(ok){messages=[];render();refresh()}else status(error||'Could not clear chat. Try again.');};
function enter(){if(active()){if(!loaded)refresh();if(!timer)timer=setInterval(function(){if(active())refresh()},15000)}else if(timer){clearInterval(timer);timer=null}}
function init(){
 E('loginPrivacyPolicy').onclick=function(){var dialog=appDialog(t('Privacy Policy'),'',[{label:t('Close'),kind:'primary'}]);var content=E('screen-setting-policy').querySelector('.policyContent').cloneNode(true);content.style.cssText='max-height:60vh;overflow:auto;text-align:left';dialog.querySelector('.appDialogText').appendChild(content);if(window.AttendanceI18n)AttendanceI18n.apply(dialog)};
 E('supportHelpTab').onclick=function(){setTab('help')};E('supportChatTab').onclick=function(){setTab('chat')};E('supportAdminMessagesTab').onclick=function(){setTab('messages')};E('supportOpenChat').onclick=function(){setTab(owner?'messages':'chat')};
 document.querySelector('.supportTabs').onkeydown=function(e){if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;e.preventDefault();var visible=[E('supportHelpTab'),E(owner?'supportAdminMessagesTab':'supportChatTab')],index=visible.indexOf(document.activeElement);var next=visible[index===0?1:0];next.click();next.focus()};
 E('supportRefresh').onclick=refresh;E('supportBack').onclick=function(){if(busy)return;selected='';selectedName='';selectedEmail='';loaded=false;render();refresh()};
 E('supportForm').onsubmit=function(e){e.preventDefault();var value=E('supportText').value.trim();if(!value||busy)return;busy=true;E('supportSend').disabled=true;status('Sending message…');if(!bridge('supportSend',[selected,value])){busy=false;E('supportSend').disabled=false}};
 E('supportClear').onclick=function(){appDialog(t('Clear this chat?'),t('This removes the conversation for you and support.'),[{label:t('Clear chat'),kind:'danger'},{label:t('Cancel'),kind:'outline'}],function(i){if(i===0&&!busy){busy=true;if(!bridge('supportClear',[selected]))busy=false}})};
 new MutationObserver(enter).observe(E('screen-setting-help'),{attributes:true,attributeFilter:['class']});document.addEventListener('visibilitychange',enter);document.addEventListener('attendance-language-changed',render);render();enter();
}
window.AttendanceSupport16={setTab:setTab};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
