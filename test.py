#!/usr/bin/env python3
# coding: utf-8

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask is running!'

@app.route('/data')
def names():
    data = {"names": ["John", "Jacob", "Julie", "Jennifer"]}
    return jsonify(data)

if __name__ == '__main__':
    app.config.ssl_context=('ssl/server.crt', 'ssl/server.key')
    app.run(host= '0.0.0.0')
