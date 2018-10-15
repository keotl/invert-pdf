import os

from jivago.jivago_application import JivagoApplication

import pdfinvert.wsgi

application = JivagoApplication(pdfinvert.wsgi)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))

    application.run_dev(port=port, host="0.0.0.0")
