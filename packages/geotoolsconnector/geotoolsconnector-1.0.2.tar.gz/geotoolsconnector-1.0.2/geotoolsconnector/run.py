from flask import Flask, render_template, request, send_from_directory
import os, requests, asyncio
from geotoolspipe import GeoToolsPipe

class GeoToolsConnector:
    def __init__(self, enableGUI=False):
        self.enableGUI = enableGUI

        if (self.enableGUI): self.serveGUI()

    def serveGUI(self):

        loop = asyncio.get_event_loop()
        app = Flask(__name__)
        pipeClass = GeoToolsPipe()

        @app.route("/")
        def main():
            return render_template('gui.html')

        @app.route("/<path:path>")
        def logo(path):
            return send_from_directory('public', path)

        def main():
            return render_template('gui.html')

        @app.route("/dissolve", methods=['POST'])
        def dissolve():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.dissolve(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/intersection", methods=['POST'])
        def intersection():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.intersection(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/centroid", methods=['POST'])
        def centroid():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.centroid(data))
            if (res): return res, 200
            return 'error', 500
            return 'error', 500

        @app.route("/difference", methods=['POST'])
        def difference():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.difference(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/polygonize", methods=['POST'])
        def polygonize():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.polygonize(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/contours", methods=['POST'])
        def contours():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.contours(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/simplify", methods=['POST'])
        def simplify():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.simplify(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/multiparttosingleparts", methods=['POST'])
        def multiparttosingleparts():
            data = request.get_json(force=True)
            res = loop.run_until_complete(self.multiparttosingleparts(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/adddatapipe", methods=['POST'])
        def adddatapipe():
            data = request.get_json(force=True)
            res = loop.run_until_complete(pipeClass.addData(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/addprocesspipe", methods=['POST'])
        def addprocesspipe():
            data = request.get_json(force=True)
            res = loop.run_until_complete(pipeClass.addProcess(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/addresultspipe", methods=['POST'])
        def addresultspipe():
            data = request.get_json(force=True)
            res = loop.run_until_complete(pipeClass.addResults(data))
            if (res): return res, 200
            return 'error', 500

        @app.route("/pipe", methods=['POST'])
        def pipe():
            reqJson = loop.run_until_complete(pipeClass.buildJSON())
            res = loop.run_until_complete(self.pipe(reqJson))
            loop.run_until_complete(pipeClass.clearPipe())
            if (res): return res, 200
            return 'error', 500

        if __name__ == '__main__':
            port = int(os.environ.get('PORT', 4444))
            app.run(debug=True, host='0.0.0.0', port=port)

    async def makePostRequest(self, command, body):
        res = requests.post('https://geotools-dev.lgb.si/{}'.format(command), json=body)
        return res

    async def dissolve(self, data):
        dissolve = await self.makePostRequest('dissolve', data)
        return dissolve.text

    async def intersection(self, data):
        intersection = await self.makePostRequest('intersection', data)
        return intersection.text

    async def centroid(self, data):
        centroid = await self.makePostRequest('centroid', data)
        return centroid.text

    async def difference(self, data):
        difference = await self.makePostRequest('difference', data)
        return difference.text

    async def polygonize(self, data):
        polygonize = await self.makePostRequest('polygonize', data)
        return polygonize.text

    async def contours(self, data):
        contours = await self.makePostRequest('contours', data)
        return contours.text

    async def simplify(self, data):
        simplify = await self.makePostRequest('simplify', data)
        return simplify.text

    async def multiparttosingleparts(self, data):
        multiparttosingleparts = await self.makePostRequest('multiparttosingleparts', data)
        return multiparttosingleparts.text

    async def pipe(self, data):
        pipe = await self.makePostRequest('pipe', data)
        return pipe.text