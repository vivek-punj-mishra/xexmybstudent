from exmyb_app import api
from exmyb_app.controllers.users_controller import CustomSignup, ValidateEmailOTP, Users,  SocialLogin, \
    VerifyMobEmail, ResendEmailMobileOTP, ForgotPassword, ResetPassword, CreateExmybUser,  ChangePassword, UserSearch
#     MobileVerifyLogin, VerifyMobEmail,

# users
api.add_resource(CustomSignup, '/api/v1/user/signup')
api.add_resource(ValidateEmailOTP, '/api/v1/validate_email/otp')
api.add_resource(Users, '/api/v1/user', '/api/v1/user/<user_id>')
api.add_resource(SocialLogin, '/api/v1/social_login')
api.add_resource(VerifyMobEmail, '/api/v1/<vtype>/verify')
api.add_resource(ResendEmailMobileOTP, '/api/v1/<vtype>/resend_otp')
api.add_resource(ForgotPassword, '/api/v1/forgot_password')
api.add_resource(ResetPassword, '/api/v1/reset_password')
api.add_resource(CreateExmybUser, '/api/v1/exmyb/user')
api.add_resource(ChangePassword, '/api/v1/user/change_password')
api.add_resource(UserSearch, '/api/v1/user_search/<type>')
