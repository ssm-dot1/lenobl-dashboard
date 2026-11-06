"""Секция «Генератор постов» для сайта: форма, подсказки тем из контент-плана, свежие цифры с сайта."""
import html as _h
import json

E = _h.escape

RUBRICS = ["Без рубрики", "Инструкция для инвестора", "Земля: шаг за шагом", "Деньги для проекта", "Сравниваем",
           "Вопрос — ответ", "Мифы об инвестициях", "Дедлайны месяца", "Словарь инвестора", "История успеха",
           "Крутая Локация", "Цифра дня", "Меры поддержки"]


def _d(s):
    p = str(s or '')[:10].split('-')
    return '.'.join(reversed(p)) if len(p) == 3 else str(s or '')


def _facts(data):
    out = []
    m = {x.get('indicator'): x for x in data.get('macro', []) if isinstance(x, dict)}
    def add(key, tpl):
        x = m.get(key)
        if x and x.get('value') is not None:
            out.append(tpl.format(v=str(x['value']).replace('.', ','), d=_d(x.get('date'))))
    add('key_rate', 'Ключевая ставка Банка России — {v}% (решение от {d}).')
    nm = m.get('next_meeting')
    if nm: out.append(f'Следующее заседание Банка России по ставке — {_d(nm.get("date"))}.')
    add('ru_infl', 'Годовая инфляция в России — {v}% (на {d}).')
    add('lo_infl', 'Годовая инфляция в Ленинградской области — {v}% (на {d}).')
    add('lo_unemp', 'Безработица по методологии МОТ в Ленобласти — {v}% (на {d}).')
    add('lo_invest', 'Инвестиции в основной капитал в Ленобласти — +{v}% г/г (на {d}).')
    add('lo_pmef', 'На ПМЭФ-2026 Ленобласть подписала инвестсоглашения на {v} млрд ₽.')
    s = [x for x in data.get('lo_series', []) if isinstance(x, dict) and x.get('indicator') == 'loans_biz']
    if s:
        x = max(s, key=lambda r: r.get('period', ''))
        out.append(f'Кредиты бизнесу в Ленобласти — {str(x["value"]).replace(".", ",")}% г/г (на {x["period"][5:7]}.{x["period"][:4]}).')
    fx = data.get('fx') or []
    if fx:
        x = fx[-1]
        out.append(f'Курс доллара ЦБ — {x["usd"]:.2f} ₽ (на {_d(x["date"])}).'.replace('.', ',', 1))
    return '\n'.join(out)


def build(data, api_url):
    ideas = [x for x in data.get('content_ideas', []) if isinstance(x, dict)][:6]
    chips = ''.join(
        f'<button type="button" class="pg-chip" data-topic="{E(x.get("title", "") + ". " + x.get("angle", ""))}" '
        f'data-rubric="{E(x.get("rubric", "").replace(" (спецвыпуск)", ""))}">{E(x.get("title", ""))}</button>'
        for x in ideas)
    rub = ''.join(f'<option>{E(r)}</option>' for r in RUBRICS)
    facts = _facts(data)
    off = '' if api_url else ' pg-off'
    return f'''<section class="ix-sec" id="postgen"><h2 class="ix-sec-h">Генератор постов для бизнеса</h2>
<div class="pg{off}" data-api="{E(api_url or '')}">
 <form class="ix pg-form" autocomplete="off">
  <div class="ix-top"><span class="ix-h">О чём написать</span><span class="ic">✎</span></div>
  <textarea name="topic" rows="3" maxlength="600" placeholder="Например: как малому бизнесу получить льготный заём на оборудование" required></textarea>
  <div class="pg-chips"><span class="ix-t">Темы из контент-плана:</span>{chips}</div>
  <div class="pg-grid">
   <label>Рубрика<select name="rubric">{rub}</select></label>
   <label>Формат<select name="format"><option value="telegram">Пост в Telegram / MAX</option><option value="vk">Пост ВКонтакте</option><option value="cards">Карусель карточек</option><option value="short">Короткий анонс</option></select></label>
   <label>Для кого<select name="audience"><option value="all">Предприниматели и инвесторы</option><option value="msp">Малый бизнес и ИП</option><option value="investors">Инвесторы</option><option value="industry">Промышленность</option></select></label>
   <label>Объём<select name="length"><option value="short">Короткий</option><option value="medium" selected>Средний</option><option value="long">Длинный</option></select></label>
  </div>
  <label class="pg-facts">Факты и цифры (необязательно) <button type="button" class="pg-link" data-facts="{E(facts)}">подставить свежие цифры с сайта</button>
   <textarea name="facts" rows="3" maxlength="2500" placeholder="Сроки, суммы, условия, ссылки — нейросеть использует только их и не будет придумывать свои"></textarea></label>
  <div class="ix-row"><button type="submit" class="pg-go">Написать пост</button><span class="pg-status ix-sub"></span></div>
 </form>
 <div class="ix pg-out">
  <div class="ix-top"><span class="ix-h">Результат</span><button type="button" class="pg-copy" disabled>Копировать</button></div>
  <div class="pg-text pg-empty">Здесь появится готовый текст. Его можно отредактировать прямо в этом поле.</div>
  <div class="pg-check" hidden><b>Проверить перед публикацией</b><div></div></div>
  <div class="ix-note">Текст пишет нейросеть YandexGPT. Перед публикацией сверьте цифры, даты и названия.</div>
 </div>
</div></section>'''


CSS = '''
.pg{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}
@media (max-width:900px){.pg{grid-template-columns:1fr}}
.pg .ix{gap:12px}
.pg textarea,.pg select{width:100%;box-sizing:border-box;font:inherit;font-size:15px;color:var(--color-fg);background:rgba(255,255,255,.6);border:1px solid rgba(123,77,219,.22);border-radius:14px;padding:10px 12px;resize:vertical}
.pg select{padding:9px 10px;margin-top:4px}
.pg textarea:focus,.pg select:focus{outline:2px solid var(--ac);outline-offset:1px}
.pg-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.pg label{font-size:13px;font-weight:600;color:var(--color-fg-muted);display:block}
.pg-facts textarea{margin-top:6px}
.pg-chips{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.pg-chip{font:inherit;font-size:12px;border:1px solid rgba(123,77,219,.25);background:var(--ac-3);color:var(--ac-deep);border-radius:999px;padding:5px 10px;cursor:pointer;text-align:left}
.pg-chip:hover{border-color:var(--ac)}
.pg-link{font:inherit;font-size:12px;background:none;border:0;color:var(--ac);cursor:pointer;text-decoration:underline;padding:0 0 0 6px}
.pg-go{font:inherit;font-weight:700;font-size:15px;color:#fff;background:linear-gradient(135deg,var(--ac),var(--ac-2));border:0;border-radius:999px;padding:12px 24px;cursor:pointer;box-shadow:0 8px 20px rgba(123,77,219,.35)}
.pg-go:disabled{opacity:.6;cursor:wait}
.pg-copy{font:inherit;font-size:13px;font-weight:600;border:1px solid var(--ac);color:var(--ac);background:transparent;border-radius:999px;padding:6px 14px;cursor:pointer}
.pg-copy:disabled{opacity:.4;cursor:default}
.pg-text{white-space:pre-wrap;font-size:15px;line-height:1.55;min-height:260px;background:rgba(255,255,255,.5);border:1px solid rgba(123,77,219,.15);border-radius:14px;padding:14px 16px;outline:none}
.pg-empty{color:var(--color-fg-muted)}
.pg-check{font-size:13px;background:rgba(253,188,22,.14);border-radius:14px;padding:10px 14px;white-space:pre-wrap}
.pg-check b{display:block;margin-bottom:4px}
.pg-off .pg-go{opacity:.6}
[data-theme="dark"] .pg textarea,[data-theme="dark"] .pg select,[data-theme="dark"] .pg-text{background:rgba(255,255,255,.06);border-color:rgba(179,155,245,.25)}
[data-theme="dark"] .pg-chip{background:rgba(179,155,245,.14);color:#e6dcff}
'''

JS = r'''
(function(){var root=document.querySelector('.pg');if(!root)return;
var api=root.getAttribute('data-api'),f=root.querySelector('form'),st=root.querySelector('.pg-status'),
out=root.querySelector('.pg-text'),chk=root.querySelector('.pg-check'),cp=root.querySelector('.pg-copy'),go=root.querySelector('.pg-go');
root.querySelectorAll('.pg-chip').forEach(function(b){b.addEventListener('click',function(){f.topic.value=b.getAttribute('data-topic');
 var r=b.getAttribute('data-rubric');for(var i=0;i<f.rubric.options.length;i++)if(f.rubric.options[i].text===r)f.rubric.selectedIndex=i;f.topic.focus();});});
var fl=root.querySelector('.pg-link');fl.addEventListener('click',function(){var v=fl.getAttribute('data-facts');f.facts.value=(f.facts.value?f.facts.value+'\n':'')+v;});
if(!api){st.textContent='Генератор скоро заработает: подключаем нейросеть.';}
f.addEventListener('submit',function(e){e.preventDefault();if(!api){st.textContent='Генератор скоро заработает: подключаем нейросеть.';return;}
 var body={topic:f.topic.value,rubric:f.rubric.value,format:f.format.value,audience:f.audience.value,length:f.length.value,facts:f.facts.value};
 go.disabled=true;st.textContent='Пишем пост… обычно 10–30 секунд';
 fetch(api,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j};});})
 .then(function(x){if(!x.ok||!x.j.post)throw new Error(x.j&&x.j.error||'Ошибка');out.textContent=x.j.post;out.classList.remove('pg-empty');out.contentEditable='true';cp.disabled=false;
  if(x.j.check){chk.hidden=false;chk.querySelector('div').textContent=x.j.check;}else chk.hidden=true;st.textContent='Готово. Можно поправить текст и скопировать.';})
 .catch(function(err){st.textContent=(err&&err.message&&err.message!=='Failed to fetch')?err.message:'Не получилось связаться с нейросетью, попробуйте ещё раз.';})
 .then(function(){go.disabled=false;});});
cp.addEventListener('click',function(){var t=out.innerText;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){cp.textContent='Скопировано';setTimeout(function(){cp.textContent='Копировать';},1500);},function(){var r=document.createRange();r.selectNodeContents(out);var s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');});});
})();
'''
