from flask import Flask
import json

# Create Flask application
app = Flask(__name__)

from backend import routes
