from chalice import Chalice, Response
from datetime import date, timedelta
import jinja2
import os
import pypd


app = Chalice(app_name='PD-Dashboard')


def search(service_id=''):
    pypd.api_key = os.environ['PD_API_KEY']

    fromdate = date.today() - timedelta(days=30)

    if service_id == '': 
      incidents  = pypd.Incident.find(maximum=100, sort_by='created_at:DESC', since=fromdate.strftime('%Y-%m-%d'))
    else:
      incidents  = pypd.Incident.find(service_ids=[id], maximum=100, sort_by='created_at:DESC', since=fromdate.strftime('%Y-%m-%d'))

    triggered = [incident for incident in incidents if incident.json['status'] == 'triggered'];
    acknowledged = [incident for incident in incidents if incident.json['status'] == 'acknowledged'];
    resolved = [incident for incident in incidents if incident.json['status'] == 'resolved'];

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
