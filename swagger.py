import requests
from pprint import pprint
import json


base_url = "http://localhost:8100/csa-service/api-docs"
grp_response = requests.get(base_url)
if (grp_response.ok):
    j_data = json.loads(grp_response.content)
    tags_value = j_data['apis']
    for path1 in tags_value:
        if 'path' in path1:
            path1['name'] = path1.pop("path")
    parent_dict = {"swagger":"1.2","host": "localhost:8100", "basePath": "/csa-service",
                   "tags": tags_value, "schemes": ["http"] }
    parent_dict["info"] = {"version": "1.0.0", "title": "CSA-WSI Swagger Documentation",
                           "description": "This document contains the documentation for "
                                          "all APIs within WSI sorted according to groups"}
    parent_dict["paths"] = {}
    groups = [list['name'] for list in tags_value]
    l = {}
    for group in groups:
            api_url = base_url + group
            api_response = requests.get(api_url)
            if api_response.ok:
                api_data = json.loads(api_response.content)
                for api in api_data['apis']:
                    for index, param in enumerate(api['operations'][0]['parameters']):
                        if 'type' in param:
                            if param['type'][0].isupper():
                                type = api['operations'][0]['parameters'][index]['type']
                                obj = {
                                    "schema": {
                                        "$ref": "#/definitions/"+type
                                    }
                                }
                                api['operations'][0]['parameters'][index].update(obj)
                    if api['operations'][0]['parameters']:
                        api['operations'][0]['parameters'][0]['in'] = api['operations'][0]['parameters'][0].pop('paramType')
                    if 'produces' in api['operations'][0] and 'consumes' in api['operations'][0]:
                        parent_dict["definitions"] = {}
                        parent_dict['paths'].update({
                            api['path']: {
                                api['operations'][0]['method'].lower(): {
                                    'tags':[group],
                                    "summary": api['operations'][0]['summary'],
                                    "type": api['operations'][0]['type'],
                                    "nickname":api['operations'][0]['nickname'],
                                    "produces": api['operations'][0]['produces'],
                                    "consumes": api['operations'][0]['consumes'],
                                    "responses": {},
                                    "parameters": api['operations'][0]['parameters']
                                }
                            }
                        })
                    elif 'produces' in api['operations'][0]:
                        parent_dict["definitions"] = {}
                        parent_dict['paths'].update({
                            api['path']: {
                                api['operations'][0]['method'].lower(): {
                                    'tags': [group],
                                    "summary": api['operations'][0]['summary'],
                                    "type": api['operations'][0]['type'],
                                    "nickname": api['operations'][0]['nickname'],
                                    "produces": api['operations'][0]['produces'],
                                    "responses": {},
                                    "parameters": api['operations'][0]['parameters']
                                }
                            }
                        })
                    elif 'consumes' in api['operations'][0]:
                        parent_dict["definitions"] = {}
                        parent_dict['paths'].update({
                            api['path']: {
                                api['operations'][0]['method'].lower(): {
                                    'tags':[group],
                                    "summary": api['operations'][0]['summary'],
                                    "type": api['operations'][0]['type'],
                                    "nickname": api['operations'][0]['nickname'],
                                    "consumes": api['operations'][0]['consumes'],
                                    "responses": {},
                                    "parameters": api['operations'][0]['parameters']
                                }
                            }
                        })
                    else:
                        parent_dict["definitions"] = {}
                        parent_dict['paths'].update({
                            api['path']: {
                                api['operations'][0]['method'].lower(): {
                                    'tags':[group],
                                    "summary": api['operations'][0]['summary'],
                                    "type": api['operations'][0]['type'],
                                    "nickname": api['operations'][0]['nickname'],
                                    "responses":{},
                                    "parameters": api['operations'][0]['parameters']
                                }
                            }
                        })
                    if 'responseMessages' in api['operations'][0]:
                        for res in api['operations'][0]['responseMessages']:
                            if 'responseModel' in res:
                                value = res['responseModel']
                                parent_dict['paths'][api['path']][api['operations'][0]['method'].lower()]['responses'].update({
                                    res['code']:{
                                        'description':res['message'],
                                        # 'responseModel': res['responseModel'],
                                        "schema": {
                                            "$ref": "#/definitions/" + value
                                        }
                                    }
                                })
                            else:
                                parent_dict['paths'][api['path']][api['operations'][0]['method'].lower()]['responses'].update({
                                    res['code']: {
                                        'description': res['message'],
                                    }
                                })
                    if 'models' in api_data:
                        for key in list(api_data['models'].keys()):
                            temp = api_data['models'][key]
                            temp.update({
                                'type':'object'
                            })
                            l.update({
                                key:temp
                            })

    all_keys = list(l.keys())
    for defi in l:
        l[defi].update({"xml": {
                            "name": defi
                        }})
        for prop in l[defi]['properties']:
            if "$ref" in l[defi]['properties'][prop]:
                value = l[defi]['properties'][prop]['$ref']
                if value in all_keys:
                    l[defi]['properties'][prop]['$ref'] = "#/definitions/" + value
                else:
                    l[defi]['properties'][prop].pop('$ref')
                    l[defi]['properties'][prop].update({
                        "type":"string"
                    })

    parent_dict.update({
        'definitions':l
    })
    data = json.dumps(parent_dict)
    with open('data.json', 'w') as outfile:
        outfile.write(data)
