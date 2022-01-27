
import os
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from exmyb_app import app
from exmyb_app.services.user_service import UserService

class Users(Resource):
    @jwt_required()
    def get(self, user_id=None):
        try:
            current_user_id = get_jwt_identity()
            if user_id is None:
                return UserService().get_user(current_user_id)
            elif current_user_id == user_id:
                return UserService().get_user(user_id)
            else:
                return {'err': 'Unauthorized User !!', 'status':0, 'data':{}}, 401
        except Exception as e:
            return {'err': str(e), 'status':0, 'data':{}}, 500


    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, help='Name can not be blank', required=True)
            parser.add_argument('password', type=str, help='Password can not be blank', required=True)
            parser.add_argument('user_type', type=str, help='user_type can not be blank', required=True)

            args = parser.parse_args()
            app.logger.debug("Users:CustomLogin::post::params::{}".format(args))
            return UserService().custom_login(args['email'], args['password'], args['user_type'])

        except Exception as e:
            app.logger.error("Users:CustomLogin:post:: {}".format(e))
            return {'err': 'Something went wrong', 'status': 0, 'data': {}}, 500

    @jwt_required()
    def put(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('data', type=dict, help='User data can not be blank', required=True)

            args = parser.parse_args()
            app.logger.info("Users:CustomLogin::put::params::{}".format(args))

            current_user_id = get_jwt_identity()
            if current_user_id:
                app.logger.info("Users:CustomLogin::put:user_id:{}".format(current_user_id))
                return UserService().update_user(current_user_id, args['data'])
            else:
                return {'err': 'Unauthorized User !!', 'status':0, 'data':{}}, 401
        except Exception as e:
            app.logger.error("Users:CustomLogin:post:: {}".format(e))
            return {'err': str(e), 'status':0, 'data':{}}, 500


class CustomSignup(Resource):

    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('email', type=str, help='Name can not be blank', required=True)
            parser.add_argument('password', type=str, help='Password can not be blank', required=True)
            parser.add_argument('user_type', type=str, help='user_type can not be blank', required=True)
            parser.add_argument('first_name', type=str)
            parser.add_argument('last_name', type=str)
            parser.add_argument('country_code', type=str)
            parser.add_argument('mobile_number', type=str)

            args = parser.parse_args()
            app.logger.debug("Users:CustomSignup::post::params::{}".format(args))
            return UserService().custom_signup(args['email'], args['password'], args['user_type'], args['first_name'],
                                              args['last_name'], args['country_code'], args['mobile_number'])

        except Exception as e:
            app.logger.error("User:CustomSignup:post:: {}".format(e))
            return {'err': 'Something went wrong', 'status': 0, 'data':{}}, 500


class ValidateEmailOTP(Resource):


    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('email', type=str, help='Email can not be blank', required=True)
            parser.add_argument('otp', type=str, help='OTP can not be blank', required=True)
            parser.add_argument('user_type', type=str, help='UserType can not be blank', required=True)

            args = parser.parse_args()
            app.logger.debug("Users:ValidateEmailOTP::post::params::{}".format(args))
            return UserService().validate_otp_email(args['email'], args['user_type'], args['otp'])

        except Exception as e:
            app.logger.error("ValidateEmailOTP::post:: {}".format(e))
            return {'err': 'Something went wrong', 'status': 0, 'data':{}}, 500

    

class SocialLogin(Resource):

    def post(self):
        try:
            parser = reqparse.RequestParser()

            parser.add_argument('email', type=str, help='Email can not be blank', required=True)
            parser.add_argument('access_token', type=str)
            parser.add_argument('user_type', type=str, help='UserType can not be blank', required=True)
            parser.add_argument('social_type', type=str, help='ScoialType can not be blank', required=True)

            args = parser.parse_args()
            app.logger.debug("SocialLogin::post::params::{}".format(args))
            if args['social_type'] == 'google':
                if args['access_token']:
                    return UserService().google_login(args['email'], args['access_token'], args['user_type'].strip())
                else:
                    app.logger.error("SocialLogin::post:google:{}: {}".format(args['email'],
                                                                            'access_token can not be blank'))
                    return {'data':{}, 'status':0, 'err':'access_token can not be blank'}, 400
            else:
                app.logger.error("SocialLogin::post:google:{}: {}".format(args['email'],'not a valid social type'))
                return {'data': {}, 'status': 0, 'err': 'not a valid social type'}, 400

        except Exception as e:
            app.logger.error("SocialLogin::post:: {}".format(e))
            return {'err': 'Something went wrong', 'status': 0, 'data': {}}, 500


class VerifyMobEmail(Resource):

    @jwt_required()
    def post(self, vtype):
        try:
            app.logger.info("VerifyMobEmail::post:type {}".format(vtype))
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str)
            parser.add_argument('country_code', type=str)
            parser.add_argument('mobile_number', type=str)
            args = parser.parse_args()
            app.logger.info("VerifyMobEmail::post::params::{}".format(args))

            current_user_id = get_jwt_identity()
            if current_user_id:
                app.logger.info("VerifyMobEmail::post:id {}".format(current_user_id))
                if vtype == 'email':
                    if args['email'] is None or args['email'] == '':
                        return {'status':0, 'err':'Email Id can not be blank', 'message':''}, 400
                    return UserService().opt_verifying_email_mob(current_user_id, vtype,
                                                                 email=args['email'].strip())
                elif vtype == 'mobile':
                    if args['country_code'] is None or args['country_code'] == '':
                        return {'status':0, 'err':'CountryCode can not be blank', 'message':''}, 400
                    if args['mobile_number'] is None or args['mobile_number'] == '':
                        return {'status': 0, 'err': 'Mobile Number can not be blank', 'message':''}, 400
                    return UserService().opt_verifying_email_mob(current_user_id, vtype,
                            country_code=args['country_code'].strip(), mobile_number=args['mobile_number'].strip())
                else:
                    return {'status': 0, 'err': 'Not valid type for verifying', 'message':''}, 400

            else:
                return {'err': 'Unauthorized User !!', 'status':0, 'message':''}, 401
        except Exception as e:
            app.logger.error("VerifyMobEmail::get:error: {}".format(str(e)))
            return {'err': str(e), 'status':0, 'message': ''}, 500

    @jwt_required()
    def put(self, vtype):
        try:
            app.logger.info("VerifyMobEmail::put:type {}".format(vtype))
            parser = reqparse.RequestParser()
            parser.add_argument('otp', type=str, help='OTP can not be blank', required=True)
            parser.add_argument('email', type=str)
            parser.add_argument('session_id', type=str)
            parser.add_argument('country_code', type=str)
            parser.add_argument('mobile_number', type=str)
            args = parser.parse_args()
            app.logger.info("VerifyMobEmail::put::params::{}".format(args))
            if vtype == 'email':
                if args['email'] is None or args['email'] == '':
                    return {'status': 0, 'err': 'Email Id can not be blank', 'message': ''}, 400
            elif vtype == 'mobile':
                if args['session_id'] is None or args['session_id'] == '':
                    return {'status': 0, "error": "Session Id can not be blank", "data": {}}, 400
                if args['country_code'] is None or args['country_code'] == '':
                    return {'status': 0, "error": "country_code can not be blank", "data": {}}, 400
                if args['mobile_number'] is None or args['mobile_number'] == '':
                    return {'status': 0, "error": "mobile_number can not be blank", "data": {}}, 400
            else:
                return {'status': 0, 'err': 'Not valid type for verifying', 'message': ''}, 400
            current_user_id = get_jwt_identity()
            if current_user_id:
                app.logger.info("VerifyMobEmail::put:id {}".format(current_user_id))
                return UserService().validate_email_mobile(current_user_id, vtype, args['otp'],
                                                           email=args['email'],
                                                           session_id=args['session_id'],
                                                           country_code=args['country_code'],
                                                           mobile_number=args['mobile_number'])
            else:
                return {'err': 'Unauthorized User !!', 'status': 0, 'message': ''}, 401
        except Exception as e:
            app.logger.error("VerifyMobEmail::put:error: {}".format(str(e)))
            return {'err': str(e), 'status':0, 'message': '', 'data':{}}, 500
            


class ResendEmailMobileOTP(Resource):

    def post(self, vtype):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('mobile_number', type=str, )
            parser.add_argument('country_code', type=str, )
            parser.add_argument('email', type=str)
            parser.add_argument('user_type', type=str, help='UserType can not be blank', required=True)

            args = parser.parse_args()
            app.logger.info("ResendEmailMobileOTP::post::params::{}".format(args))

            if args['user_type'] == '':
                return {'status': 0, "error": "UserType can not be blank", 'data':{}}, 400
            if args['user_type'] not in app.config['USER_TYPE']:
                return {'status': 0, "error": "Invalid UserType", 'data':{}}, 400
            if vtype == 'email':
                if args['email'] is None or args['email'] == '':
                    return {'status': 0, "error": "Email Id can not be blank", 'data':{}}, 400
                else:
                    return UserService().resend_email_otp(args['email'].strip(), args['user_type'])

            elif vtype == 'mobile':
                if args['mobile_number'] is None or args['mobile_number'] == '':
                    return {'status': 0, "error": "Mobile Number can not be blank"}, 400
                if args['country_code'] is None or args['country_code'] == '':
                    return {'status': 0, "error": "Country Code can not be blank"}, 400

                if args['country_code'].strip() == '+91':
                    args['mobile_number'] = args['mobile_number'].strip()
                    if args['mobile_number'][0] == 0 and len(args['mobile_number']) != 11:
                        return {'status': 0, "error": "Invalid Mobile Number", "data": {}}, 400
                    elif len(args['mobile_number']) != 10:
                        return {'status': 0, "error": "Invalid Mobile Number", "data": {}}, 400
                    else:
                        return UserService().resend_mobile_otp(args['country_code'].strip(), args['mobile_number'],
                                                                 args['user_type'].strip())
                else:
                    return UserService().resend_mobile_otp(args['country_code'].strip(), args['mobile_number'],
                                                           args['user_type'].strip())

        except Exception as e:
            app.logger.error("ResendEmailMobileOTP::post::error::{}".format(str(e)))
            return {'status': 0, "error": str(e), "data": {}}, 500


class ForgotPassword(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('email', type=str, help='Email can not be blank', required=True)

            args = parser.parse_args()
            app.logger.debug("Users:ForgotPassword::post::params::{}".format(args))
            return UserService().forgot_password(args['email'])
        except Exception as e:
            app.logger.error("ForgotPassword::post:: {}".format(e))
            return {'err': 'Something went wrong', 'status': 0, 'data':{}}, 500


class ResetPassword(Resource):

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('password', type=str, help='Password can not be blank', required=True)
            parser.add_argument('code', type=str, help='Code can not be blank', required=True)
            args = parser.parse_args()
            app.logger.debug("Users:ResetPassword::post::params::{}".format(args))

            if args['password'] =='':
                return {'status': 0, 'err': 'Password can not be blank', 'data': {}}, 400
            if args['code'] =='':
                return {'status': 0, 'err': 'Code can not be blank', 'data': {}}, 400

            return UserService().reset_password(args['password'], args['code'].strip())

        except Exception as e:
            app.logger.error("ResetPassword::post:: {}".format(e))
            return {'err': 'Something went wrong', 'status': 0, 'data':{}}, 500


class CreateExmybUser(Resource):
    @jwt_required()
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('first_name', type=str, help='First Name can not be blank', required=True)
            parser.add_argument('last_name', type=str, help='Last Name can not be blank', required=True)
            parser.add_argument('email', type=str, help='Email can not be blank', required=True)
            parser.add_argument('country_code', type=str, help='Country Code can not be blank', required=True)
            parser.add_argument('mobile_number', type=str, help='Mobile can not be blank', required=True)
            parser.add_argument('designation', type=str)
            parser.add_argument('user_type', type=str)
            args = parser.parse_args()
            app.logger.debug("Users:CreateExmybUser::post::params::{}".format(args))

            if args['first_name'] == '':
                return {'status': 0, 'err': 'First Name can not be blank', 'data': {}}, 400
            if args['last_name'] == '':
                return {'status': 0, 'err': 'Last Name can not be blank', 'data': {}}, 400
            if args['email'] == '':
                return {'status': 0, 'err': 'Email can not be blank', 'data': {}}, 400
            if args['country_code'] == '':
                return {'status': 0, 'err': 'Country Code can not be blank', 'data': {}}, 400
            if args['mobile_number'] == '':
                return {'status': 0, 'err': 'Mobile can not be blank', 'data': {}}, 400
            current_user_id = get_jwt_identity()
            if current_user_id:
                app.logger.info("CreateExmybUser::post:user_id {}".format(current_user_id))
                data={'first_name': args['first_name'], 'last_name': args['last_name'], 'email': args['email'],
                       'country_code': args['country_code'], 'mobile_number': args['mobile_number'],
                       'designation': args['designation']
                       }
                return UserService().create_exmyb_user(data, current_user_id)
            else:
                return {'err': 'Unauthorized User !!', 'status':0, 'message':''}, 401

        except Exception as e:
            app.logger.error("CreateExmybUser::post:: {}".format(e))
            return {'err': 'Something went wrong', 'status': 0, 'data':{}}, 500


class ChangePassword(Resource):
    @jwt_required()
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('old_password', type=str, help='Old Password can not be blank', required=True)
            parser.add_argument('new_password', type=str, help='New Password can not be blank', required=True)
            args = parser.parse_args()
            app.logger.debug("Users:ChangePassword::post::params::{}".format(args))

            if args['old_password'] == '':
                return {'status': 0, 'err': 'Old Password can not be blank', 'data': {}}, 400
            if args['new_password'] == '':
                return {'status': 0, 'err': 'New Password can not be blank', 'data': {}}, 400

            current_user_id = get_jwt_identity()
            if current_user_id:
                app.logger.info("ChangePassword::post:user_id {}".format(current_user_id))
                return UserService().change_password(current_user_id, args['old_password'].strip(),
                                                     args['new_password'].strip())
            else:
                return {'err': 'Unauthorized User !!', 'status':0, 'message':''}, 401

        except Exception as e:
            print(e)
            app.logger.error("ChangePassword::post:: {}".format(str(e)))
            return {'err': 'Something went wrong', 'status': 0}, 500


class UserSearch(Resource):
    @jwt_required()
    def get(self, type=None):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('query', type=str, help='Query can not be blank', required=True)
            args = parser.parse_args()
            app.logger.debug("Users:UserSearch::get::params::{}".format(args))
            if args['query'] == '':
                return {'err': 'Query can not be blank', 'status':0, 'message':'', 'data':[]}, 400
            if not type:
                return {'err': 'UserType can not be blank', 'status':0, 'message':'', 'data':[]}, 400
            current_user_id = get_jwt_identity()
            if current_user_id:
                app.logger.info("Users:UserSearch::get:user_id {}".format(current_user_id))
                return UserService().user_search(current_user_id, type.strip(), args['query'].strip())
            else:
                return {'err': 'Unauthorized User !!', 'status':0, 'message':'', 'data':[]}, 401

        except Exception as e:
            return {'err': str(e), 'status':0, 'data':[]}, 500





