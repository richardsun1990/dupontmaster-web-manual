
(function () {
  const toggle = document.getElementById('menuButton');
  const menu = document.getElementById('mobileMenu');
  const setMenu = (open) => {
    menu.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? '关闭导航' : '打开导航');
  };
  toggle.addEventListener('click', () => setMenu(menu.hidden));
  menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', (event) => { if(event.key === 'Escape') setMenu(false); });
  window.addEventListener('resize', () => { if(window.innerWidth > 860) setMenu(false); });
  const values = [
    { step:'第 01 步 / 认识所有权', number:'01', title:'买股票，就是买公司。',copy:'持有股票，意味着持有企业的一部分股权。先把注意力从每天的股价波动转回企业本身：它卖什么，向谁销售，为什么能持续经营？',link:'#philosophy' },
    { step:'第 02 步 / 观察生意',number:'02',title:'先看看它怎么赚钱。',copy:'选择一家自己熟悉的公司，了解产品、客户、竞争对手和行业。没有理解生意之前，财务数字也很难真正说明问题。',link:'#practice' },
    { step:'第 03 步 / 验证判断',number:'03',title:'用财报检验最初的认识。',copy:'观察长期资本回报、利润来源、资产负债与自由现金流。利润来自什么？赚到的钱能否回来？增长需要投入多少资本？',link:'#practice' },
    { step:'第 04 步 / 价格与价值',number:'04',title:'好公司，也要有好价格。',copy:'试着估算企业未来现金流能创造多少价值。估值有误差，因此要留出足够的安全边际，而不是预测明天涨跌。',link:'#principles' },
    { step:'第 05 步 / 长期跟踪',number:'05',title:'持有不是研究的终点。',copy:'重视真实现金流与合理分红，在价值与价格合适时积累股权，并持续复盘竞争优势和经营变化。',link:'#tool' }
  ];
  const choices = [...document.querySelectorAll('.journey-choice')];
  const refs = {step:document.getElementById('detail-step'),number:document.getElementById('detail-number'),title:document.getElementById('detail-title'),copy:document.getElementById('detail-copy'),link:document.getElementById('detail-link')};
  choices.forEach((button)=> button.addEventListener('click',()=>{
     const index=Number(button.dataset.index); const v=values[index]; if(!v)return;
     choices.forEach((el)=> {const on = el === button;el.classList.toggle('active',on);el.setAttribute('aria-pressed',String(on));});
     refs.step.textContent=v.step;refs.number.textContent=v.number;refs.title.textContent=v.title;refs.copy.textContent=v.copy;refs.link.href=v.link;
  }));
})();


(function () {
  'use strict';
  const yearElements = document.querySelectorAll('[data-current-year]');
  const currentYear = new Date().getFullYear();
  yearElements.forEach(node => { node.textContent = String(currentYear); });
})();
