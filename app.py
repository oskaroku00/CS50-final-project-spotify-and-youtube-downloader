from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.debug = True

app.secret_key = '8f42a73054b1749f8f58848be5e6502c'

CLIENT_ID = 'd5248a9df7094903900ac146b3fd8687'
CLIENT_SECRET = '464d694b440d4b308e64d3da16409b9f'
REDIRECT_URI = 'http://127.0.0.1:5000/'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'







@app.route("/")
def index():
    return "My spotify app. Log in to start: <a herf='/login'>LOG IN<a>"