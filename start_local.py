from AEDeveloper.developer import app
import sys

port = 5000 if not len(sys.argv) == 2 else int(sys.argv[1])

app.run('127.0.0.1', port=port, debug=True)

