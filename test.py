import json
from sendinblue.client import Client

api = Client('xjTqIa43VmQ0GnyX')

data = api.get_forms()
# data = api.get('scenarios/getForms')
# data = api.get_list(6)

print(json.dumps(data))
# print('\n')

# to retrieve all campaigns of type 'classic' & status 'queued'
# data = { "type":"classic",
# 	"status":"queued",
# 	"page":1,
# 	"page_limit":10
# }
#
# campaigns = m.get_campaigns_v2(data)
