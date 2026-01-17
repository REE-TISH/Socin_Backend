from razorpay import Client
from decouple import config

client = Client(auth=(config('RAZORPAY_API_KEY'), config('RAZORPAY_SECRET_KEY')))