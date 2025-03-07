from dotenv import load_dotenv
import os

load_dotenv()

baseUrl= os.getenv('BASE_URL')

sandBoxUrl = 'https://sandbox.aamarpay.com/index.php'
verificationSandBoxUrl = 'https://sandbox.aamarpay.com/api/v1/trxcheck/request.php'
verificationProductionUrl = 'https://secure.aamarpay.com/api/v1/trxcheck/request.php'
productionUrl = 'https://secure.aamarpay.com/index.php'
succesUrl = baseUrl+'/finance/success-payment/'
failUrl = baseUrl+'/finance/cancel-payment/'
cancelUrl = baseUrl+'/finance/cancel-payment/'
signature = 'dbb74894e82415a2f7ff0ec3a97e4183'
storeID = 'aamarpaytest'
sandboxReturnUrl = 'https://sandbox.aamarpay.com'
productionReturnUrl = 'https://sandbox.aamarpay.com'
frontUrl = 'http://localhost:3000/payment-status'
