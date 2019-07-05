from chalice import Chalice, Response
import jinja2
import os
import pypd


app = Chalice(app_name='PD-Dashboard')

def search(service_id=''):
    pypd.api_key = os.environ['PD_API_KEY']

    if service_id: 
      triggered  = pypd.Incident.find(service_ids=[service_id], sort_by='created_at:DESC', maximum=50, statuses=['triggered'] )
      acknowledged  = pypd.Incident.find(service_ids=[service_id], sort_by='created_at:DESC', maximum=50, statuses=['acknowledged'] )
      resolved  = pypd.Incident.find(service_ids=[service_id], sort_by='created_at:DESC', maximum=20, statuses=['resolved'] )
    else:
      triggered  = pypd.Incident.find(sort_by='created_at:DESC', maximum=50, statuses=['triggered'] )
      acknowledged  = pypd.Incident.find(sort_by='created_at:DESC', maximum=50, statuses=['acknowledged'] )
      resolved  = pypd.Incident.find(sort_by='created_at:DESC', maximum=20, statuses=['resolved'] )

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
