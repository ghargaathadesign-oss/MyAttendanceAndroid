(function(){
'use strict';
var dictionary=__HINDI_DICTIONARY__,reverse={},language='en',texts=new WeakMap(),attrs=new WeakMap(),queued=false,applying=false;
Object.keys(dictionary).forEach(function(key){reverse[dictionary[key]]=key});
try{language=localStorage.getItem('attendance_language_v15515')==='hi'?'hi':'en'}catch(e){}
function english(s){return reverse[s]||s}
function translate(s){s=english(String(s));if(language!=='hi')return s;if(dictionary[s])return dictionary[s];
 var days=s.match(/^(\d+(?:\.\d+)?) (days?|\/ year · .*|days \/ year ÷ 12 = (\d+(?:\.\d+)?) days \/ month)$/);if(days&&/^days?$/.test(days[2]))return days[1]+' दिन';
 var allowance=s.match(/^(\d+) \/ year · (\d+(?:\.\d+)?) \/ month$/);if(allowance)return allowance[1]+' / वर्ष · '+allowance[2]+' / महीना';
 var months={January:'जनवरी',February:'फ़रवरी',March:'मार्च',April:'अप्रैल',May:'मई',June:'जून',July:'जुलाई',August:'अगस्त',September:'सितंबर',October:'अक्टूबर',November:'नवंबर',December:'दिसंबर'};
 var date=s.match(/^([A-Z][a-z]+) (\d{4})$/);if(date&&months[date[1]])return months[date[1]]+' '+date[2];
 var policy=s.match(/^You get ([\d.]+) days each month\.$/);if(policy)return 'आपको हर महीने '+policy[1]+' दिन की छुट्टी मिलती है।';
 var record=s.match(/^(\d+) records?$/);if(record)return record[1]+' रिकॉर्ड';
 var hourly=s.match(/^([\d.]+)× (?:normal )?hourly rate$/);if(hourly)return hourly[1]+'× प्रति घंटे की दर';
 return s;
}
function excluded(el){return !el||el.closest('script,style,[data-no-translate],#profileCardName,#profileOptionName,#cloudName,#cloudEmail,#profileCardJob,#profileCardCompany,#profileCardExtra,.docInfo,.friendlyLeaveRecordText small');}
function text(node){if(excluded(node.parentElement)||node.parentElement.closest('textarea'))return;var val=node.nodeValue,trim=val.trim();if(!trim)return;var rec=texts.get(node);if(!rec||val!==rec.last)rec={source:english(trim)};var out=translate(rec.source);var next=val.slice(0,val.indexOf(trim))+out+val.slice(val.indexOf(trim)+trim.length);if(val!==next)node.nodeValue=next;rec.last=next;texts.set(node,rec)}
var scanStats={fullPasses:0,incrementalPasses:0,textVisits:0},pending=new Set();
function ignored(node){var el=node&&node.nodeType===1?node:node&&node.parentElement;return !el||!!el.closest('svg,[data-lottie],script,style,[data-no-translate]')}
function apply(root){if(applying)return;root=root||document.body;if(ignored(root))return;applying=true;if(root===document.body)scanStats.fullPasses++;else scanStats.incrementalPasses++;
 try{if(root.nodeType===3){scanStats.textVisits++;text(root);return}
 var walker=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT,{acceptNode:function(node){if(ignored(node))return NodeFilter.FILTER_REJECT;return node.nodeType===3?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_SKIP}}),node;
 while(node=walker.nextNode()){scanStats.textVisits++;text(node)}
 var elements=Array.from(root.querySelectorAll('[placeholder],[aria-label],[title]'));if(root.matches&&root.matches('[placeholder],[aria-label],[title]'))elements.unshift(root);
 elements.forEach(function(el){if(excluded(el)||ignored(el))return;var record=attrs.get(el)||{};['placeholder','aria-label','title'].forEach(function(name){if(!el.hasAttribute(name))return;var current=el.getAttribute(name),rec=record[name];if(!rec||current!==rec.last)rec={source:english(current)};var output=translate(rec.source);if(output!==current)el.setAttribute(name,output);rec.last=output;record[name]=rec});attrs.set(el,record)});
 }finally{applying=false}
}
function schedule(mutations){if(language!=='hi'||document.hidden)return;
 mutations.forEach(function(m){if(ignored(m.target))return;if(m.type==='characterData')pending.add(m.target);else m.addedNodes.forEach(function(node){if(!ignored(node))pending.add(node)})});
 if(queued||!pending.size)return;queued=true;requestAnimationFrame(function(){queued=false;var roots=Array.from(pending);pending.clear();if(language!=='hi'||document.hidden)return;roots.forEach(function(root){if(document.documentElement.contains(root)&&!roots.some(function(other){return other!==root&&other.nodeType===1&&other.contains(root)}))apply(root)})});
}
function select(code){language=code==='hi'?'hi':'en';try{localStorage.setItem('attendance_language_v15515',language)}catch(e){}document.documentElement.lang=language;document.getElementById('languageEnglish').classList.toggle('selected',language==='en');document.getElementById('languageHindi').classList.toggle('selected',language==='hi');apply();document.dispatchEvent(new Event('attendance-language-changed'))}
window.AttendanceI18n={t:translate,apply:apply,setLanguage:select,getLanguage:function(){return language},stats:scanStats};
document.documentElement.lang=language;
function init(){document.querySelectorAll('[data-language]').forEach(function(el){el.onclick=function(){select(el.dataset.language)}});select(language);new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true,characterData:true});}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
