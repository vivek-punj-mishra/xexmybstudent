# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 -- All rights reserved.
# Author: Prakash Singh <prakash@exmyb.com>
#
# This file is part of the ExMyb project.
#
###############################################################################
from exmyb_app import app
import requests
import json


class TwoFactorSMS:
    _url = app.config['TF_SMS_URL']
    _auth_key = app.config['TF_AUTH_KEY']
    _expire = '5'  # in minute -> expire time setup from system
    _template_name = app.config['TF_TEMP_NAME']
    _headers = {"Content-Type": "application/json"}

    def send_otp(self, mobile):
        res = {"status": 0, "data": {}, "err": ""}
        try:
            self.method = 'GET'
            self.endpoint = self._auth_key + '/SMS/' + mobile + '/AUTOGEN/' + self._template_name
            resp = self.send_request()
            if resp.status_code == requests.codes.ok:
                data = resp.json()
                app.logger.info("TwoFactorSMS::send_otp:: {}".format(data))
                if data['Status'] == "Success":
                    res.update({"status": 1, 'data':{'session_id':data['Details']},'message':"OTP Sent!"})
                else:
                    res.update({"err": data['Details']})
            else:
                res.update({"err": resp.json()['Details']})
        except Exception as e:
            res.update({"err": str(e)})
        return res

    def validate_otp(self, session_id, otp):
        res = {"status": 0, "message": "", "err": ""}
        try:
            self.method = 'GET'
            self.endpoint = self._auth_key + '/SMS/VERIFY/' + session_id + '/' + otp
            resp = self.send_request()
            if resp.status_code == requests.codes.ok:
                data = resp.json()
                app.logger.info("TwoFactorSMS::validate_otp:: {}".format(data))
                if data['Status'] == "Success" and data['Details']=="OTP Matched":
                    res.update({"status": 1, "message": data['Details']})
                else:
                    res.update({"err": data['Details']})
            else:
                res.update({"err": "something went wrong"})

        except Exception as e:
            res.update({"err": "something went wrong"})
        return res

    def send_request(self):
        if self.method == 'GET':
            resp = requests.get(self._url + self.endpoint, headers=self._headers)
        return resp
