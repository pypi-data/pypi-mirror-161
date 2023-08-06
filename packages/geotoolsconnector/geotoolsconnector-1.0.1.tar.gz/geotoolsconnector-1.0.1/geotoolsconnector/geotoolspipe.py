import asyncio

class GeoToolsPipe:
    def __init__(self):
        self.Data = []
        self.Processes = []
        self.Results = []

    async def buildJSON(self):
        JSON = {}
        JSON['Data'] = self.Data
        JSON['Processes'] = self.Processes
        JSON['Result'] = self.Results

        return JSON

    async def addData(self, input):
        self.Data.append(input)
        return 'OK'
    
    async def addProcess(self, input):
        if (input['Type'] == 'Intersection' or input['Type'] == 'Difference' or input['Type'] == 'Dissolve' or input['Type'] == 'Simplify' or input['Type'] == 'Multiparttosingleparts'):
            self.Processes.append({ "Type": input['Type'], "Input1": input['Input1'], "Input2": input['Input2'], "Result": input['Result'] })
        else:
            self.Processes.append({ "Type": input['Type'], "Input": input['Input'], "Result": input['Result'] })
        return 'OK'

    async def addResults(self, input):
        self.Results = input
        return 'OK'
    
    async def clearPipe(self):
        self.Data = []
        self.Processes = []
        self.Results = []