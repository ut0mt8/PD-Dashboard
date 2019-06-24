from chalice import Chalice, Response
import jinja2
import os
import pypd

pypd.api_key = "XXXX"
app = Chalice(app_name='PD-Dashboard')

def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)

@app.route("/")
def index():
    triggereds = pypd.Incident.find(statuses=['triggered'])
    acknowledgeds = pypd.Incident.find(statuses=['acknowledged'])
    context = {'triggereds' : triggereds, 'acknowledgeds' : acknowledgeds}
    template = render('chalicelib/templates/index.html', context)
    return Response(template, status_code=200, headers={"Content-Type": "text/html"})

@app.route("/service/{id}")
def service(id):
    triggereds = pypd.Incident.find(service_ids=[id], statuses=['triggered'])
    acknowledgeds = pypd.Incident.find(service_ids=[id], statuses=['acknowledged'])
    context = {'triggereds' : triggereds, 'acknowledgeds' : acknowledgeds}
    template = render('chalicelib/templates/index.html', context)
    return Response(template, status_code=200, headers={"Content-Type": "text/html"})

