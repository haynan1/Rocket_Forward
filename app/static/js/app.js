const toastQueue=[];
let toastVisible=false;
function showNextToast(){
 if(toastVisible||!toastQueue.length)return;
 toastVisible=true;
 const {msg,type}=toastQueue.shift();
 const t=document.createElement('div');t.className='toast'+(type?' '+type:'');t.textContent=msg;
 if(msg.includes('Conquista desbloqueada')){
  t.classList.add('achievement-toast');
  ['#ffd36b','#a99bff','#ff8e76','#78d9bb','#fff'].forEach((color,index)=>{
   const particle=document.createElement('i');particle.className='space-confetti';
   const angle=(Math.PI*2*index)/5;const distance=38+(index%2)*16;
   particle.style.setProperty('--confetti-color',color);
   particle.style.setProperty('--confetti-x',`${Math.cos(angle)*distance}px`);
   particle.style.setProperty('--confetti-y',`${Math.sin(angle)*distance}px`);
   t.appendChild(particle);
  });
 }
 document.body.appendChild(t);
 setTimeout(()=>{t.remove();toastVisible=false;showNextToast();},4000);
}
function showToast(msg,type){
 toastQueue.push({msg,type});showNextToast();
}
document.querySelectorAll('.toast').forEach(t=>{
 const type=t.classList.contains('error')?'error':'success';
 showToast(t.textContent,type);t.remove();
});
if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
 document.querySelectorAll('.stat b, .stats-list b').forEach(element=>{
  const match=element.textContent.trim().match(/^(\d+)(.*)$/);
  if(!match)return;
  const target=Number(match[1]);const suffix=match[2];const started=performance.now();
  const tick=now=>{
   const progress=Math.min((now-started)/700,1);
   element.textContent=`${Math.round(target*(1-(1-progress)**3))}${suffix}`;
   if(progress<1)requestAnimationFrame(tick);
  };
  element.textContent=`0${suffix}`;requestAnimationFrame(tick);
 });
}
const motivationalPhrase=document.querySelector('.motivational-phrase[data-phrases]');
if(motivationalPhrase){
 try{
  const phrases=JSON.parse(motivationalPhrase.dataset.phrases||'[]');
  const interval=Number(motivationalPhrase.dataset.interval)||1800000;
  if(phrases.length>1){
   let current=Math.floor(Date.now()/interval)%phrases.length;
   const changePhrase=()=>{
    current=(current+1)%phrases.length;
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(!reduced)motivationalPhrase.classList.add('changing');
    setTimeout(()=>{
     motivationalPhrase.textContent=`“${phrases[current]}”`;
     motivationalPhrase.classList.remove('changing');
    },reduced?0:180);
   };
   setInterval(changePhrase,interval);
  }
 }catch(error){ console.warn('Não foi possível carregar as frases motivacionais.',error); }
}
const authPage=document.body.classList.contains('auth-page');
if(authPage&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
 const backgrounds=['','auth-background-1','auth-background-2','auth-background-3'];
 let current=0;
 setInterval(()=>{
  document.body.classList.remove(...backgrounds.slice(1));
  current=(current+1)%backgrounds.length;
  if(backgrounds[current])document.body.classList.add(backgrounds[current]);
 },30000);
}
const board=document.querySelector('.board');
if(board){
 const csrfToken=document.querySelector('meta[name="csrf-token"]').content;
 let dragged=null;
 const updateCount=list=>{list.closest('.board-col').querySelector('.board-col-head b').textContent=list.querySelectorAll('.board-card').length;};
 board.querySelectorAll('.board-card').forEach(card=>{
  card.addEventListener('dragstart',()=>{dragged=card;card.classList.add('dragging');});
  card.addEventListener('dragend',()=>card.classList.remove('dragging'));
 });
 board.querySelectorAll('.board-list').forEach(list=>{
  list.addEventListener('dragover',e=>{e.preventDefault();list.classList.add('drag-over');});
  list.addEventListener('dragleave',()=>list.classList.remove('drag-over'));
  list.addEventListener('drop',e=>{
   e.preventDefault();list.classList.remove('drag-over');
   if(!dragged)return;
   const from=dragged.closest('.board-list');
   if(from===list)return;
   const id=dragged.dataset.id;const status=list.dataset.status;const occurrence=dragged.dataset.occurrence;
   const moved=dragged;from.removeChild(moved);list.appendChild(moved);moved.classList.add('board-card-settling');setTimeout(()=>moved.classList.remove('board-card-settling'),350);updateCount(from);updateCount(list);
   const update={status};if(occurrence)update.occurrence=occurrence;
   fetch(`/api/goals/${id}`,{method:'PATCH',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken},body:JSON.stringify(update)})
    .then(r=>{if(!r.ok)throw new Error();return r.json();})
    .then(data=>(data.achievements||[]).forEach(achievement=>showToast(`🏆 Conquista desbloqueada: ${achievement.title}`,'success')))
    .catch(()=>{
     list.removeChild(dragged);from.appendChild(dragged);updateCount(from);updateCount(list);
     showToast('Não foi possível mover a meta.','error');
    });
  });
 });
}
const sidebarToggle=document.getElementById('sidebar-toggle');
if(sidebarToggle){
 const setSidebarState=()=>{const collapsed=document.body.classList.contains('sidebar-collapsed');sidebarToggle.setAttribute('aria-expanded',String(!collapsed));sidebarToggle.title=collapsed?'Expandir painel lateral':'Recolher painel lateral'};
 if(localStorage.getItem('rocket-sidebar-collapsed')==='true')document.body.classList.add('sidebar-collapsed');
 setSidebarState();
 sidebarToggle.addEventListener('click',()=>{document.body.classList.toggle('sidebar-collapsed');localStorage.setItem('rocket-sidebar-collapsed',document.body.classList.contains('sidebar-collapsed'));setSidebarState()});
}
const deadlineToggle=document.getElementById('has-deadline');
if(deadlineToggle){
 const form=deadlineToggle.closest('form');
 const dateInput=form.querySelector('input[name="date"]');
 // Campos de data recebem a data local da máquina, evitando que o formulário abra vazio.
 if(dateInput&&!dateInput.value){
  const now=new Date();
  const localDate=[now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('-');
  dateInput.value=localDate;
 }
 const updateDeadline=()=>form.classList.toggle('no-deadline',!deadlineToggle.checked);
 updateDeadline();deadlineToggle.addEventListener('change',updateDeadline);
 const recurrence=form.querySelector('select[name="recurrence_type"]');
 const updateRecurrence=()=>{
  const value=recurrence.value;
  form.querySelectorAll('[data-recurrence]').forEach(field=>{
   const kind=field.dataset.recurrence;
   field.hidden=!((kind==='count'&&value==='count')||(kind==='end'&&['weekdays','weekends'].includes(value)));
  });
 };
 if(recurrence){updateRecurrence();recurrence.addEventListener('change',updateRecurrence);}
}
const avatarInput=document.getElementById('avatar-input');
if(avatarInput){
 const csrfToken=document.querySelector('meta[name="csrf-token"]').content;
 avatarInput.addEventListener('change',()=>{
  if(!avatarInput.files.length)return;
  const data=new FormData();data.append('avatar',avatarInput.files[0]);
  fetch(avatarInput.dataset.uploadUrl,{method:'POST',body:data,headers:{'X-CSRFToken':csrfToken}}).then(()=>location.reload());
 });
 const avatarRemove=document.getElementById('avatar-remove');
 if(avatarRemove)avatarRemove.addEventListener('click',()=>{
  fetch(avatarRemove.dataset.removeUrl,{method:'POST',headers:{'X-CSRFToken':csrfToken}}).then(()=>location.reload());
 });
}
const historyCanvas=document.getElementById('historyChart');
if(historyCanvas){
 const chartData=JSON.parse(historyCanvas.dataset.chart);
 const chartLabels=JSON.parse(historyCanvas.dataset.labels);
 new Chart(historyCanvas,{type:'bar',data:{labels:chartLabels,datasets:[{data:chartData,backgroundColor:'#3b69ff',borderRadius:8}]},options:{plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{beginAtZero:true,ticks:{stepSize:1}}}}});
}

function enhanceSelect(select){
 const wrap=document.createElement('div');wrap.className='select-wrap';
 select.parentNode.insertBefore(wrap,select);wrap.appendChild(select);
 select.tabIndex=-1;select.setAttribute('aria-hidden','true');select.classList.add('select-native');
 const trigger=document.createElement('button');
 trigger.type='button';trigger.className='select-trigger';
 trigger.setAttribute('aria-haspopup','listbox');trigger.setAttribute('aria-expanded','false');
 if(select.disabled)trigger.disabled=true;
 const label=document.createElement('span');label.className='select-trigger-label';
 trigger.append(label);trigger.insertAdjacentHTML('beforeend','<i class="bi bi-chevron-down"></i>');
 const listbox=document.createElement('ul');listbox.className='select-options';listbox.setAttribute('role','listbox');listbox.hidden=true;
 wrap.append(trigger,listbox);
 const items=[...select.options].map((opt,i)=>{
  const li=document.createElement('li');
  li.className='select-option';li.setAttribute('role','option');li.textContent=opt.textContent;li.tabIndex=-1;
  if(opt.disabled)li.setAttribute('aria-disabled','true');
  listbox.appendChild(li);
  return li;
 });
 const sync=()=>{
  label.textContent=select.options[select.selectedIndex]?.textContent||'';
  items.forEach((li,i)=>li.classList.toggle('selected',i===select.selectedIndex));
 };
 sync();
 const close=()=>{listbox.hidden=true;trigger.setAttribute('aria-expanded','false');trigger.classList.remove('open')};
 const open=()=>{
  if(trigger.disabled)return;
  document.querySelectorAll('.select-options').forEach(l=>{if(l!==listbox)l.hidden=true;l.previousElementSibling?.classList.remove('open')});
  listbox.hidden=false;trigger.setAttribute('aria-expanded','true');trigger.classList.add('open');
  (items[select.selectedIndex]||items[0])?.focus();
 };
 trigger.addEventListener('click',()=>listbox.hidden?open():close());
 trigger.addEventListener('keydown',e=>{
  if(['ArrowDown','ArrowUp','Enter',' '].includes(e.key)){e.preventDefault();open();}
  else if(e.key==='Escape')close();
 });
 items.forEach((li,i)=>{
  li.addEventListener('click',()=>{
   if(select.options[i].disabled)return;
   select.selectedIndex=i;sync();close();trigger.focus();
   select.dispatchEvent(new Event('change',{bubbles:true}));
  });
  li.addEventListener('keydown',e=>{
   if(e.key==='Enter'||e.key===' '){e.preventDefault();li.click();}
   else if(e.key==='ArrowDown'){e.preventDefault();(items[i+1]||li).focus();}
   else if(e.key==='ArrowUp'){e.preventDefault();(items[i-1]||trigger).focus();if(!items[i-1])close();}
   else if(e.key==='Escape'){close();trigger.focus();}
  });
 });
 select.addEventListener('change',sync);
 document.addEventListener('click',e=>{if(!wrap.contains(e.target))close();});
}
document.querySelectorAll('select').forEach(enhanceSelect);
