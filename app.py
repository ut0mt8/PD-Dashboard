from chalice import Chalice, Response
from datetime import datetime, timedelta
import jinja2
import os
import pypd

app = Chalice(app_name='PD-Dashboard')
maxresults = 10
delta = datetime.now() - timedelta(hours = 2)
maxtime = delta.strftime('%Y-%m-%d %H:%M:%S')

def search(service_id=''):
    triggered = []
    acknowledged = []

    pypd.api_key = os.environ['PD_API_KEY']

    if service_id: 
      incidents  = pypd.Incident.find(service_ids=[service_id], sort_by='created_at:DESC', statuses=['triggered','acknowledged'] )
      resolved  = pypd.Incident.find(service_ids=[service_id], sort_by='created_at:DESC', statuses=['resolved'], maximum=maxresults, since=maxtime)
    else:
      incidents  = pypd.Incident.find(sort_by='created_at:DESC', statuses=['triggered','acknowledged'] )
      resolved  = pypd.Incident.find(sort_by='created_at:DESC', statuses=['resolved'], maximum=maxresults, since=maxtime)

    for incident in incidents:
        if incident['status'] == "triggered":
            triggered.append(incident)
        elif incident['status'] == "acknowledged":
            acknowledged.append(incident)

    return (triggered, acknowledged, resolved)

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)

def publish(triggered, acknowledged, resolved):
    context = {'triggered' : triggered, 'acknowledged' : acknowledged, 'resolved' : resolved}
    template = render('chalicelib/templates/index.html', context)
    return Response(template, status_code=200, headers={'Content-Type': 'text/html'})

@app.route('/')
def index():
    (triggered, acknowledged, resolved) = search()
    return publish(triggered, acknowledged, resolved)

@app.route('/service/{id}')
def service(id):
    (triggered, acknowledged, resolved) = search(id)
    return publish(triggered, acknowledged, resolved)
