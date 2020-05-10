# py_ver == "3.6.9"
import flask


app = flask.Flask(__name__)


import time
import logging


logging.basicConfig(filename="/var/log/secnotify/secnotify.log",
                    level=logging.DEBUG,
                    format='%(asctime)s:%(module)s:%(name)s:%(levelname)s:%(message)s')
logging.debug("secnotify startup")
logger = logging.getLogger()


@app.after_request
def after_request(response):
    timestamp = time.strftime('[%Y-%b-%d %H:%M]')
    app.logger.error(
                     '%s %s %s %s %s %s %s %s',
                                               timestamp,
                                               request.remote_addr,
                                               request.method,
                                               request.full_path,
                                               request.cookies,
                                               request.data,
                                               response.status,
                                               response.data
                    )
    return response


@app.route("/colour")
def set_colour():
    return """
            <html>
            <script>
            window.changeColour = function() {
            document.body.style.backgroundColor = location.hash.replace('#', '');
            document.getElementsByName("text")[0].innerHTML = decodeURI(location.hash.replace('#', ''));
            }
            </script>
            <body>
            <p name="text"></p>
            <div style="height:100vh" onmousemove=changeColour()></div>
            </body>
            </html>
            """


@app.route('/send_host')
def set_target():
    return """
            <html>
                <title>Target selection</title>
                <body>
                    <form action="/scan">
                        Enter target IP: <input name="ip" type="text" />
                        <input name="submit" type="submit">
                    </form>
                </body>
            </html>
"""


import os


@app.route('/scan')
def scanner():
    ip = flask.request.args.get('ip')
    result = os.popen('nmap ' + ip).read()
    return "%s" % result


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Content-Security-Policy'] = "default-src 'self'"
    return response


if __name__ == '__main__':
    app.run()
