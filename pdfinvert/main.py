from jivago.jivago_application import JivagoApplication

import pdfinvert.wsgi

application = JivagoApplication(pdfinvert.wsgi, debug=True)

if __name__ == '__main__':
    application.run_dev(port=8080)
