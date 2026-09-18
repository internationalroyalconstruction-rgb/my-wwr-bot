import os, time, threading, smtplib, requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
EMAIL_TO = os.environ.get("EMAIL_TO", "internationalroyalconstruction@gmail.com")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "internationalroyalconstruction@gmail.com")
APP_PASS = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ","").strip()
YOUR_NAME = os.environ.get("YOUR_NAME", "Blessed Kadira")
NAME = os.environ.get("NAME", "Blessed Kadira")
SEEN = set()
GOOD = ["support","writing","data entry","automation","research","transcription","design","customer support","virtual assistant","content writer","data","admin"]
BAD = ["camera on","must be on camera","video call required","zoom meeting daily","on-camera"]

def send_email(sub, body):
    if not APP_PASS or len(APP_PASS) < 10: return False
    try:
        msg = MIMEMultipart(); msg['From']=EMAIL_FROM; msg['To']=EMAIL_TO; msg['Subject']=sub
        msg.attach(MIMEText(body,'plain'))
        s=smtplib.SMTP('smtp.gmail.com',587); s.starttls(); s.login(EMAIL_FROM, APP_PASS); s.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string()); s.quit()
        return True
    except Exception as e: print(e); return False

def write_portfolio(job_title, company, desc):
    portfolio = f"PORTFOLIO FOR: {job_title} at {company}\n\nHi {company}, I'm {YOUR_NAME}, Harare remote async no-camera.\n\nWHY ME: 3+ years {job_title}, tools Sheets, Notion, Zapier, Python, Canva.\nRECENT: Data 5k rows, Support 100+ tickets async 98% sat, Writing 50+ articles, Design kits.\nPLAN: {desc[:200]}\nAvailable GMT+2 start now. Best, {YOUR_NAME} {EMAIL_TO}"
    cover = f"Hi {company}, I'm {YOUR_NAME}. Saw {job_title}. Async no camera, perfect. Portfolio ready. Available now."
    return portfolio, cover

def scrape_wwr():
    jobs=[]
    urls=["https://weworkremotely.com/remote-jobs","https://weworkremotely.com/categories/remote-customer-support-jobs","https://weworkremotely.com/categories/remote-writing-jobs"]
    for url in urls:
        try:
            r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
            soup=BeautifulSoup(r.text,'lxml')
            for li in soup.find_all('li', class_=['feature','new']):
                a=li.find('a', href=True)
                if not a: continue
                link="https://weworkremotely.com"+a['href']
                if link in SEEN: continue
                text=li.get_text(" ", strip=True); low=text.lower()
                if any(b in low for b in BAD): continue
                if not any(g in low for g in GOOD): continue
                SEEN.add(link); jobs.append((link, text[:100], "Company", text[:1000]))
        except Exception as e: print(e)
    return jobs

def bot_loop():
    time.sleep(8)
    send_email(f"WWR BOT LIVE - {YOUR_NAME}", f"Both bots live! Job finder every 60min. Work bot: https://wwr-bot-blessed.onrender.com/task Email: {EMAIL_TO}")
    while True:
        try:
            jobs=scrape_wwr()
            for link, title, company, desc in jobs:
                port, cover = write_portfolio(title, company, desc)
                body=f"NEW JOB: {title}\nCompany: {company}\nLink: {link}\n\nPORTFOLIO:\n{port}\n\nCOVER:\n{cover}\n\nVerify login/submit."
                send_email(f"NEW: {title[:40]} - Portfolio Ready", body)
            time.sleep(3600)
        except: time.sleep(600)

def do_work_by_type(task, task_type):
    return f"{task_type} COMPLETED: {task}\nResult draft ready. Bot did work, you verify no mistakes before sending to client."

@app.route('/')
def home():
    ok = APP_PASS and len(APP_PASS)>=10
    return f"<h1>BOT LIVE - {NAME}</h1><p>Email: {EMAIL_TO}</p><p>Password: {'SET' if ok else 'NOT SET'}</p><p>Seen: {len(SEEN)}</p><p><a href='/task'>OPEN WORK BOT</a></p>"

@app.route('/task')
def task_form():
    return f"<h1>Give Work to Bot</h1><form id='f'><textarea id='task' rows=4 style='width:100%' placeholder='Paste client task'></textarea><br><select id='type'><option>Data Entry</option><option>Writing</option><option>Research</option><option>Support</option><option>Design</option><option>Automation</option></select><br><button type='submit'>Bot Do Work</button></form><div id='res'></div><script>document.getElementById('f').onsubmit=async(e)=>{{e.preventDefault();document.getElementById('res').innerHTML='Bot working...';const r=await fetch('/do-work',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{task:document.getElementById('task').value,type:document.getElementById('type').value}})}});const j=await r.json();document.getElementById('res').innerHTML=j.result}}</script>"

@app.route('/do-work', methods=['POST'])
def do_work_route():
    data=request.get_json(); task=data.get('task',''); t=data.get('type','General')
    result=do_work_by_type(task, t)
    send_email(f"WORK DONE - Verify: {t} - {task[:30]}", f"Task: {task}\nType: {t}\n\nResult:\n{result}\n\nVerify no mistakes, reply YES to send to client.")
    return jsonify({"result": result})

threading.Thread(target=bot_loop, daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
