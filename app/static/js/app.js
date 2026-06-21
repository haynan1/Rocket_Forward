const toastQueue=[];
let toastVisible=false;
function showNextToast(){
 if(toastVisible||!toastQueue.length)return;
 toastVisible=true;
 const {msg,type}=toastQueue.shift();
 const t=document.createElement('div');t.className='toast'+(type?' '+type:'');t.textContent=msg;
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
   from.removeChild(dragged);list.appendChild(dragged);updateCount(from);updateCount(list);
   fetch(`/api/goals/${id}`,{method:'PATCH',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken},body:JSON.stringify({status,occurrence})})
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
