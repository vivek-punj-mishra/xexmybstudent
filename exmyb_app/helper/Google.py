# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 -- All rights reserved.
# Author: Prakash  Singh <prakash@exmyb.com>
#
# This file is part of the exmyb project.
#
###############################################################################

import requests

class Google:

    _url = "https://oauth2.googleapis.com"

    def __init__(self, access_token):
        self.id_token = access_token
        self.headers = []

    def getUser(self):
        self.endpoint = 'tokeninfo?id_token=' + self.id_token
        self.method = 'GET'
        resp = self.sendRequest()
        if resp.status_code == requests.codes.ok:
            data = resp.json()
            return {"status": 1, "data": {"id": data['sub'], "email": data['email'], "name": data['name'],
            'first_name': data.get('given_name', ''), 'last_name':data.get('family_name', ''),
             'email_verified':data['email_verified'], "picture": data['picture']}}
        else:
            return {"status": 0}


    def sendRequest(self):

        if self.method == 'GET':
            resp = requests.get(self._url + '/' + self.endpoint, headers=self.headers)
        return resp
