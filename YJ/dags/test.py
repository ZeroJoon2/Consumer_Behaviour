from dotenv import load_dotenv
import os
dotenv_path = os.path.abspath(os.path.join(os.getcwd(), "..", ".env"))
load_dotenv(dotenv_path)

print(os.getenv('host_ip'))
print(os.getenv('user_id'))
print(os.getenv('user_password'))
print(os.getenv('DATABASE'))
