import sys
sys.path.insert(0,"..")
from pyrena import *
from time import sleep

client = Arena(
    "somearenacustomer@some-company.com",
    "sqldjsqdlkjsqdldjsqdlk",
    "some_env"
    )
#print(client)
sleep(5)
client.logout()