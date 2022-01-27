from datetime import datetime, date, timedelta
import pytz
from exmyb_app import app
from exmyb_app.helper.Google import Google
from exmyb_app.helper.TFACTOR import TwoFactorSMS
from exmyb_app.helper.amazon_ses_mailer import AmazonSESMailSend
from exmyb_app.helper.auth_utils import generate_jwt_token, decode_jwt_token
from exmyb_app.models.users_model import UsersModel
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
import random
import string
from exmyb_app.models.usr_verfication_model import UsrVerificationModel
from exmyb_app.helper.mailer import mailer

class UserService:

    def custom_signup(self, email, password, user_type, first_name, last_name, country_code, mobile_number):
        res = {'data': {}, 'err': '', 'status': 0, 'message': ''}
        try:
            status_code = 201
            user = UsersModel.find_by_email(email)
            if not user:
                if country_code and mobile_number:
                    if UsersModel.find_by_mobile(country_code.strip(), mobile_number.strip()):
                        res['err'] = "Mobile Number already exists."
                        return res, 400
                elif country_code and not mobile_number:
                    res['err'] = "Mobile Number can not be blank."
                    return res, 400
                elif not country_code and mobile_number:
                    res['err'] = "Country Code can not be blank."
                    return res, 400

                password = UsersModel.generate_password_hash(password)
                user = UsersModel(email=email, password=password, user_type=user_type, first_name=first_name,
                                    last_name=last_name, country_code=country_code, mobile_number=mobile_number,
                                    signup_type='email')
                if self.generate_otp_email(email, user_type):
                    res['data'] = {'email': email, 'user_type': user_type}
                    res['message'] = 'sent otp to your Email Id !'
                    res['status'] = 1
                else:
                    res['err'] = 'Error while sending mail for verification'
                    res['status'] = 0
                    status_code = 500

            elif country_code and mobile_number:
                if UsersModel.find_by_mobile(country_code.strip(), mobile_number.strip()):
                    res['err'] = "Mobile Number already exists."
                    return res, 400
            elif country_code and not mobile_number:
                res['err'] = "Mobile Number can not be blank."
                return res, 400
            elif not country_code and mobile_number:
                res['err'] = "Country Code can not be blank."
                return res, 400
            else:
                res['err'] = "User already exists!"
                status_code = 403
        except Exception as e:
            app.logger.error("UserService:custom_signup:: {}".format(str(e)))
            res['err'] = 'Something went wrong'
            status_code = 500
        user.save()
        return res, status_code
    
    def generate_otp_email(self, email, user_type=None):
        try:
            otp = ""
            for i in range(4):
                otp += str(random.randint(0, 9))

            usr_verify = UsrVerificationModel(usr_type=user_type, verification_id=email, otp=otp, is_expired=False,
                                              verification_type='email', otp_time=datetime.utcnow())
            html_body = """\
            <html>
            <head></head>
            <body> 
                <p> Verification Code <br> {} <br> Here is your Verification Code.</p>
            </body>
            </html>
            """.format(otp)

            # is_send, msg = mailer('Email Verification', app.config['EMAIL_FROM_ADDR'], app.config['EMAIL_PASSWORD'],
            #                      [email], html_body=html_body)
            aws_mail_obj = AmazonSESMailSend(app.config['AWS_FROM_EMAIL_ADDR'])
            is_send, msg = aws_mail_obj.send_mail('Email Verification', [email], html_message=html_body)
            usr_verify.is_send = is_send
            usr_verify.message = msg
            usr_verify.save()
            return is_send
        except Exception as e:
            app.logger.error("UserService:generate_otp_email:: {}".format(str(e)))
            return False

    def validate_otp_email(self, email, user_type, otp, user=None):
        res = {'data': {}, 'err': '', 'status': 0, 'message': ''}
        try:
            status_code = 201
            usr_verify = UsrVerificationModel.query.order_by(UsrVerificationModel.otp_time.desc()).filter_by(
                verification_id=email, usr_type=user_type).first()

            if usr_verify:
                if usr_verify.is_expired:
                    app.logger.info("user verify data is expired ....{}.".format(str(usr_verify.is_expired)))
                    res['err'] = "OTP has been expired !"
                    status_code = 410
                elif otp.strip() == usr_verify.otp:
                    otp_time = int(
                        (datetime.utcnow() - usr_verify.otp_time).total_seconds() / 60)
                    app.logger.info("OTP Expire Now Time:{}".format(str(datetime.utcnow())))
                    app.logger.info("OTP Time:{}".format(str(usr_verify.otp_time)))
                    app.logger.info("OTP Time min:{}".format(str(otp_time)))
                    if otp_time > 1500:
                        usr_verify.is_expired = True
                        usr_verify.save()
                        res['err'] = "OTP has been expired !"
                        status_code = 410
                    else:
                        if user:
                            user.email_verify = True
                            user.email = email
                        else:
                            user = UsersModel.find_by_email_and_usr_type(email, user_type)
                            user.email_verify = True
                            user.access_token = create_access_token(identity=str(user.id), expires_delta=False)
                        # create_refresh_token(identity = str(user.id))
                        user.save()
                        res.update({'data': user.to_json(), 'status': 1, 'message': "Email validated !"})
                else:
                    res.update({'err': 'You entered invalid OTP.'})
                    status_code = 400
            else:
                res.update({'err': 'You entered invalid OTP.'})
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:validate_otp_email:: {}".format(str(e)))
            res.update({'err': str(e)})
            status_code = 500
        return res, status_code

    def get_user(self, user_id):
        app.logger.info("fetch user: {}".format(user_id))
        res = {'data': {}, 'err': '', 'status': 0}
        status_code = 200
        try:
            user = UsersModel.find_by_id(user_id)
            if user:
                res.update({'data': user.to_json(), 'status': 1})
            else:
                res['err'] = 'User not found!'
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:get_user:: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code

    def custom_login(self, email, password, user_type):
        res = {'data': {}, 'err': '', 'status': 0}
        status_code = 201
        app.logger.info("custom login with email {}".format(email))
        try:
            user = UsersModel.find_by_email_and_usr_type(email, user_type)
            if user:
                if UsersModel.verify_hash(password, user.password):
                    user.last_login = datetime.utcnow()
                    user.last_login_type = 'email'
                    if user.access_token is None or user.access_token == '':
                        user.access_token = create_access_token(identity=str(user.id), expires_delta=False)
                    user.save()
                    res.update({'data': user.to_json(), 'status': 1, 'message':'User has been loggedIn successfully !!'})
                else:
                    res['err'] = "Invalid Password !"
                    status_code = 400
            else:
                res['err'] = "Email Id does not exist"
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:custom_login:: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code

    
    def google_login(self, email, g_access_token, user_type):
        res = {'data': {}, 'err': '', 'status': 0}
        status_code = 201
        app.logger.info("UserService:google_login::email {}".format(email))
        try:
            user_obj = Google(g_access_token)
            user_obj_data = user_obj.getUser()
            print("888888888888",user_obj)

            if user_obj_data['status'] and user_obj_data['data']['email_verified']:
                user_res = user_obj_data['data']
                print("???????????",user_res)
                if email == user_res['email']:
                    user = UsersModel.find_by_email(email)
                    if not user:
                        app.logger.info("UserService:google_login::create_new_user {}".format(email))
                        if not user_res['first_name'] and user_res['name'].strip():
                            name = user_res['name'].split(' ')
                            user_res['last_name'] = name[-1]
                            user_res['first_name'] = ''.join(name[:-1])

                        user = UsersModel(email=email, user_type=user_type, first_name=user_res['first_name'].strip(),
                                            last_name=user_res['last_name'].strip(), social_type='google',
                                            signup_type='social',
                                            email_verify=True, last_login_type='google')
                        user.save()
                        user.created_by = user.updated_by = user.id
                        user.access_token = create_access_token(identity=str(user.id), expires_delta=False)
                        user.save()
                    else:
                        app.logger.info("UserService:google_login::existing_new_user {}".format(email))
                        if user.user_type == user_type:
                            user.last_login = datetime.utcnow()
                            user.last_login_type = 'google'
                            user.save()
                        else:
                            res['err'] = "User already exist as a {}".format(user.user_type)
                            status_code = 400
                    res.update({'data': user.to_json(), 'status': 1, 'message':"User has been loggedIn successfully !"})
                else:
                    res['err'] = "Invalid email !!"
                    status_code = 400
            else:
                res['err'] = "Unauthorized User !!"
                status_code = 401
        except Exception as e:
            res['err'] = str(e)
            app.logger.error("UserService:google_login::error: {}".format(str(e)))
            status_code = 500
        return res, status_code


    def opt_verifying_email_mob(self, user_id, _type, email=None, country_code=None, mobile_number=None):
        """

        :rtype: object
        """
        res = {'message': '', 'err': '', 'status': 0, 'data':{}}
        try:
            status_code = 201
            user = UsersModel.find_by_id(user_id)
            if user:
                if _type == 'email':
                    ex_user = UsersModel.find_by_email(email)
                    print("999999999999",ex_user)
                    if ex_user and ex_user.id != user.id:
                        res.update({"err": "This email Id does not belong to you, so can't verify it."})
                        return res, 400
                    elif ex_user is None:
                        pass
                        #user.email = email
                        #user.save()
                    else:
                        pass
                    if self.generate_otp_email(email, user.user_type):
                        res['message'] = 'sent otp to your registered Email Id !!'
                        res['status'] = 1
                    else:
                        res['err'] = 'Error while sending mail for verification'
                        res['status'] = 0
                        status_code = 500
                elif _type == 'mobile':
                    ex_user = UsersModel.find_by_mobile(country_code, mobile_number)
                    if ex_user and ex_user.id != user.id:
                        res.update({"err": "This Mobile Number does not belong to you, so can't verify it."})
                        return res, 400
                    elif ex_user is None:
                        #user.country_code = country_code
                        #user.mobile_number = mobile_number
                        #user.save()
                        pass
                    else:
                        pass
                    if country_code and mobile_number != '' :
                        mobile = country_code + mobile_number
                        sent_otp = TwoFactorSMS().send_otp(mobile)
                        if sent_otp['status']:
                            res['data']= {'session_id':sent_otp['data']['session_id']}
                            res["message"]=sent_otp['message']
                            res['status'] = 1
                        else:
                            res['err'] = sent_otp['err']
                            status_code = 400
                    else:
                        res['err'] = "mobile number doesn't exist"
                        status_code = 400
            else:
                res['err'] = 'User not found'
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:opt_verifying_email_mob:error: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code

    def validate_email_mobile(self, user_id, _type, otp, email=None, session_id=None, country_code=None, mobile_number=None):
        res = {'data': {}, 'status': 0, 'message': '', 'err': ''}
        try:
            status_code = 200
            user = UsersModel.find_by_id(user_id)
            if user:
                if _type == 'email':
                    return self.validate_otp_email(email, user.user_type, otp, user)
                elif _type == 'mobile':
                    verify_otp = TwoFactorSMS().validate_otp(session_id, otp)
                    if verify_otp['status']:
                        user.country_code = country_code
                        user.mobile_number = mobile_number
                        user.mobile_verify = True
                        user.save()
                        res.update({'data': user.to_json(), 'status': 1, 'message': "mobile validated !"})
                    else:
                        res['err'] = "Invalid OTP"
                        status_code = 400
                else:
                    res['err'] = "Invalid type"
                    status_code = 400
            else:
                res['err'] = "User Not Found!"
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:validate_email_mobile:error: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code
        
    def resend_email_otp(self, email, user_type):
        res = {'status': 0, 'err': '', 'data': {}, 'message': ''}
        try:
            status_code = 201
            is_send, msg = self._regenerate_email_otp(email, user_type)
            if is_send:
                res['data'] = {'email': email, 'user_type': user_type}
                res['message'] = 'Sent OTP to your Email Id !'
                res['status'] = 1
            else:
                res['err'] = msg
                res['status'] = 0
                status_code = 500

        except Exception as e:
            app.logger.error("UserService:resend_email_otp:: {}".format(str(e)))
            res.update({'err': str(e)})
            status_code = 500
        return res, status_code

    def _regenerate_email_otp(self, email, user_type):
        try:
            otp = ""
            is_send = False
            for i in range(4):
                otp += str(random.randint(0, 9))

            html_body = """\
            <html>
            <head></head>
            <body> 
                <p> Verification Code <br> {} <br> Here is your Verification Code.</p>
            </body>
            </html>
            """.format(otp)
            usr_verify = UsrVerificationModel.query.order_by(UsrVerificationModel.otp_time.desc()).filter_by(
                verification_id=email, usr_type=user_type).first()
            aws_mail_obj = AmazonSESMailSend(app.config['AWS_FROM_EMAIL_ADDR'])
            if usr_verify:
                if usr_verify.attempts < 3:
                    # is_send, msg = mailer('Email Verification', app.config['EMAIL_FROM_ADDR'], app.config['EMAIL_PASSWORD'],
                    #                       [email], html_body=html_body)
                    is_send, msg = aws_mail_obj.send_mail('Email Verification', [email], html_message=html_body)
                    usr_verify.otp = otp
                    usr_verify.is_expired = False
                    usr_verify.otp_time = datetime.utcnow()
                    usr_verify.updated_at = datetime.utcnow()
                    usr_verify.attempts += 1
                else:
                    msg = "limit has been exceeded. Please try after 15 minutes."
            else:
                usr_verify = UsrVerificationModel(usr_type=user_type, verification_id=email, otp=otp, is_expired=False,
                                                  verification_type='email', otp_time=datetime.utcnow())

                # is_send, msg = mailer('Email Verification', app.config['EMAIL_FROM_ADDR'], app.config['EMAIL_PASSWORD'],
                #                      [email], html_body=html_body)

                is_send, msg = aws_mail_obj.send_mail('Email Verification', [email], html_message=html_body)
                usr_verify.attempts += 1

            usr_verify.is_send = is_send
            usr_verify.message = msg
            usr_verify.save()

        except Exception as e:
            is_send, msg = (is_send, str(e))
            app.logger.error("UserService:_regenerate_email_otp:: {}".format(str(e)))
        return is_send, msg

    def forgot_password(self, email):
        try:
            status_code = 201
            res = {'status': 0, "err": "", "message": ""}
            user = UsersModel.find_by_email(email)
            if user:
                reset_token = generate_jwt_token(email)
                reset_url = app.config['REST_PASSWORD_URL'] + reset_token

                html_body = """\
                <html>
                <head></head>
                <body>
                    <p>Dear, User</p>
                    <p>
                        To reset your password
                        <a href={}>
                            click here
                        </a>.
                    </p>
                    <p>If you have not requested a password reset simply ignore this message.</p>
                    <p>Sincerely</p>
                    <p>ExMyB Support Team</p>
                </body>
                </html>
                """.format(reset_url)

                aws_mail_obj = AmazonSESMailSend(app.config['AWS_FROM_EMAIL_ADDR'])
                is_send, msg = aws_mail_obj.send_mail('[ExMyB] Reset Your Password', [user.email],
                                                      html_message=html_body)
                if is_send:
                    res.update({"status": 1, "message": msg})
                else:
                    res['err'] = msg
                    status_code = 500
            else:
                res['err'] = "Email Id does not exist"
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:forgot_pawword::error: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code


    def reset_password(self, password, code):
        try:
            res = {'status': 0, "err": "", "message": ""}
            status_code = 201

            token = decode_jwt_token(code)
            if 'err' in token:
                res['err'] = "Invalid Token!"
                status_code = 400

            elif password:
                user = UsersModel.find_by_email(token['_id'])
                if user:
                    password = UsersModel.generate_password_hash(password)
                    user.password = password
                    user.save()
                    res.update({'status': 1, "message": 'reset your password successfully'})
                else:
                    res['err'] = "user is not found !"
                    status_code = 400
        except Exception as e:
            app.logger.error("UserService:reset_pawword::error: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code

    def update_user(self, user_id, data):
        res = {'data': {}, 'err': '', 'status': 0}
        try:
            app.logger.info("UserService:update_user:data: {}".format(str(data)))
            user = UsersModel.find_by_id(user_id)
            status_code = 200
            is_update = False
            if user:
                columns = [col.name for col in user.__table__.columns if col.name != 'password']
                for u_data in data:
                    if u_data == 'mobile_number' and data['mobile_number']:
                        if data['country_code'] == '' or not data['country_code']:
                            res.update({'err': "Country Code can not be blank"})
                            return res, 400
                        ex_user = UsersModel.find_by_mobile(data['country_code'], data['mobile_number'])
                        if ex_user and ex_user.id != user.id:
                            res.update({"err":"This Mobile Number does not belong to you, so can't update it."})
                            return res, 400
                        elif ex_user and not ex_user.mobile_verify:
                            res.update({"err": "Mobile Number is not verified"})
                            return res, 400
                        else:
                            pass
                            #user.mobile_verify = False
                    if u_data == 'email' and data['email']:
                        ex_user = UsersModel.find_by_email(data['email'])
                        if ex_user and ex_user.id != user.id:
                            res.update({"err":"This Email Id does not belong to you, so can't update it."})
                            return res, 400
                        elif ex_user and not ex_user.email_verify:
                            res.update({"err": "Email Id is not verified"})
                            return res, 400
                        else:
                            pass
                            #user.email_verify = False
                    if u_data in columns:
                        setattr(user, u_data, data[u_data])
                        is_update = True
                if is_update:
                    user.updated_by = user.id
                    user.updated_at = datetime.utcnow()
                    user.save()
                res['data'] = user.to_json()
                res['status'] = 1
                res['message'] = "User has been updated successfully"
            else:
                res['err'] = "User is not found !"
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:update_user:: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code

    def create_exmyb_user(self, data, user_id):
        res = {'err': '', 'status': 0, 'message': ''}
        try:
            app.logger.info("UserService:create_exmyb_user:data: {}".format(str(data)))
            status_code = 201
            m_user = UsersModel.find_by_mobile(data['country_code'], data['mobile_number'])
            if m_user:
                res['err'] = 'Mobile already exist !!'
                return res, 400

            e_user = UsersModel.find_by_email(data['email'])
            if e_user:
                res['err'] = 'Email already exist !!'
                return res, 400

            password = self.__generate_random_password()
            if not password:
                app.logger.error(
                    "UserService:create_exmyb_user:Error while generating password:user_id {}".format(user_id))
                res['err'] = "Error while generating password !"
                return res, 500
            hash_password = UsersModel.generate_password_hash(password)
            user_obj = UsersModel(email=data['email'], mobile_number=data['mobile_number'],
                                  country_code=data['country_code'],
                                  first_name=data['first_name'], last_name=data['last_name'],
                                  designation=data['designation'],
                                  user_type='exmyb', password=hash_password)
            user_obj.created_by = user_obj.updated_by = user_id
            user_obj.email_verify = True
            user_obj.mobile_verify = True
            # user_obj.access_token = create_access_token(identity=str(user_obj.id), expires_delta=False)
            sent_mail = self.__user_creation_mail(data['first_name'] + " " + data['last_name'], data['email'],
                                                     password)
            if sent_mail['status']:
                user_obj.save()
                res['message'] = "User Created Successfully !!"
                res['status'] = 1
            else:
                res['err'] = sent_mail['err']
                status_code = 500
        except Exception as e:
            app.logger.error(
                "UserService:create_exmyb_user:Error: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code

    @staticmethod
    def __user_creation_mail(name, email, password):
        app.logger.info(
            "UserService:create_exmyb_user:__user_creation_mail:email: {}".format(email))
        html_body = """\
                 <html>
                   <head></head>
                   <body>
                      <p>
                         Hi {},
                      </p>
                      <p>
                         Welcome to the ExpandMyBusiness Team. Please find your login details below.
                      </p>
                      <p><b>Username:</b> {}</p>
                      <p><b>Password:</b> {}</p>
                      <p>
                         <b>Click here: </b><a href="https://exmyb.com/change_password/">To Start Using ExMyB KAM Dashboard</a>
                      </p>
                      <p>If you have any questions, please let us know by sending an email to support@exmyb.com</p>
                      <p>Thank You,</p>
                      <p>ExMyB Support Team</p>
                   </body>
                </html>
                """.format(name, email, password)

        aws_mail_obj = AmazonSESMailSend(app.config['AWS_FROM_EMAIL_ADDR'])
        is_send, msg = aws_mail_obj.send_mail('Welcome To ExMyB Family', [email], html_message=html_body)
        if is_send:
            return {"status": 1, 'message': msg}
        else:
            return {"status": 0, 'err': msg}

    @staticmethod
    def __generate_random_password():
        try:
            app.logger.info("UserService: generate password")
            characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
            random.shuffle(characters)
            select_chars = []
            for _ in range(10):
                select_chars.append(random.choice(characters))
            random.shuffle(select_chars)
            password = "".join(select_chars)
            return password

        except Exception as e:
            app.logger.error("UserService: generate password: Error: {}".format(str(e)))
            return

    def change_password(self, user_id, old_password, new_password):
        res = {'err': '', 'status': 0, 'message': ''}
        try:
            app.logger.info(
                "UserService:change_password:user_id: {}".format(user_id))
            status_code = 201
            user = UsersModel.find_by_id(user_id)
            if user:
                if UsersModel.verify_hash(old_password, user.password):
                    user.password = UsersModel.generate_password_hash(new_password)
                    user.updated_by = user_id
                    user.updated_at = datetime.utcnow()
                    user.save()
                    res.update({'status': 1, 'message':'Password has been changed'})
                else:
                    res['err'] = "Invalid Password !"
                    status_code = 400
            else:
                res['err'] = 'User Not Found !'
                status_code = 400
        except Exception as e:
            app.logger.error(
                "UserService:change_password:error: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code

    def user_search(self, user_id, user_type, query):
        try:
            res = {'err': '', 'status': 0, 'message': '', 'data':[]}
            app.logger.info(
                "UserService:user_search:user_id: {}".format(user_id))
            status_code = 200
            user = UsersModel.find_by_id(user_id)
            if user:
                users = UsersModel.query.filter(UsersModel.first_name.like('%'+query+'%')|UsersModel.last_name.like(
                    '%'+query+'%'),UsersModel.user_type == user_type, UsersModel.active==True).all()
                for user in users:
                    res['data'].append({
                        'id':user.id,
                        'first_name':user.first_name,
                        'last_name': user.last_name,
                        'profile_pic':user.profile_pic,
                        'email': user.email,
                        'country_code': user.country_code,
                        'mobile_number': user.mobile_number,
                        'email_verify': user.email_verify,
                        'mobile_verify': user.mobile_verify
                    })
                res['status'] = 1
            else:
                res['err'] = 'User Not Found !'
                status_code = 400
        except Exception as e:
            app.logger.error("UserService:user_search:error: {}".format(str(e)))
            res['err'] = str(e)
            status_code = 500
        return res, status_code