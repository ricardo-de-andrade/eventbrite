import json
import urllib3

from flask import Flask, jsonify, request as flask_request
app = Flask(__name__)

APIKEY = "<KEY>"
db = None

class Datastore:
  """ In memory datastore """

  db = {}

  def __init__(self):
    EVENTBRITE_URL = 'https://www.eventbriteapi.com/v3/events/search/?page={}'

    headers = {
      'Authorization': 'Bearer <CREDS>',
      'Content-Type': 'application/json'
    }

    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    # pre load 4 pages of events in memory 
    for p in range(4):
      print(p)

      events = http.request('GET', EVENTBRITE_URL.format(p+1), headers=headers)

      for e in json.loads(events.data)["events"]:
        self.db[e["id"]] = e

    print(len(self.db))

  def get_events(self):
    return self.db

  def update_event(self, id, event):
    self.db[id] = event
    return event


db=Datastore()

@app.route("/events", methods=['GET'])
def events():
  source = db.get_events().values()
  events = list(source)
  is_free = flask_request.args.get('isFree')
  event_name = flask_request.args.get('name')
  event_start_date = flask_request.args.get('startDate')
  org_name = flask_request.args.get('orgName')

  apikey = flask_request.args.get('apiKey')
  if (apikey != APIKEY):
    return (jsonify({"message":"Invalid or missing API key"}), 401)

  # filter events based on 'cost', ie, free/paid
  if (is_free):
    if (is_free.lower() == 'true'):
      events = (([event for event in source if event["is_free"] == True]))
    else:
      events = (([event for event in source if event["is_free"] == False]))
  print(events)

  #filter events based on event name
  if (events):
    source = events
  print(events)

  if (event_name != None):
      events = (([event for event in source if event['name']['text'] == event_name]))

  print(events)
  if (len(events) == 0):
    return (jsonify({"message":"No events Found"}), 404)

  return jsonify(events)

@app.route("/events/<event_id>", methods=['GET'])
def event_entity(event_id):
  print("Event entity")

  apikey = flask_request.args.get('apiKey')
  if (apikey != APIKEY):
    return (jsonify({"message":"Invalid or missing API key"}), 401)

  return (jsonify(([event for event in db.get_events().values() if event["id"] == event_id])[0]))

@app.route("/events/<event_id>", methods=['PUT'])
def update_event(event_id):
  print("Update event entity")
  print(flask_request.json)

  apikey = flask_request.args.get('apiKey')
  if (apikey != APIKEY):
    return (jsonify({"message":"Invalid or missing API key"}), 401)
  
  event = None
  events = [event for event in db.get_events().values() if event["id"] == event_id]
  if (events): event = events[0]

  if (event):
    db.update_event(event_id,flask_request.json)
  else:
    return (jsonify({"message":"Event Not Found"}), 404)

  return (flask_request.json)

if __name__ == '__main__':
    app.run(debug=True)  
