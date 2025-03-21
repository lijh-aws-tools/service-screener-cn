import boto3, json, botocore
from botocore.exceptions import BotoCoreError
from botocore.config import Config as bConfig
from utils.Config import Config
from datetime import datetime
from utils.Tools import _warn
import time

## --others '{"WA": {"region": "ap-southeast-1", "reportName":"SS_Report", "newMileStone":0}}'

class WATools():
    DEFAULT_REPORTNAME = 'SS_Report'
    DEFAULT_NEWMILESTONE = 0
    waInfo = {
        'isExists': False,
        'WorkloadId': None,
        'LensesAlias': 'wellarchitected'
    }

    HASPERMISSION = True

    def __init__(self, pillarId):
        self.pillarId = pillarId
        pass

    def preCheck(self, params):
        if not 'reportName' in params:
            params['reportName'] = self.DEFAULT_REPORTNAME

        if not 'newMileStone' in params:
            params['newMileStone'] = 0

        if not 'region' in params:
            params['region'] = Config.get('REGIONS_SELECTED')[0]

        print("*** [WATool] Attempting to deploy WA Tools in this region: {}".format(params['region']))
        self.region = params['region']
        
        return True

    def init(self, cfg):
        self.cfg = cfg 
        self.stsInfo = Config.get('stsInfo')

        boto3Config = bConfig(region_name = cfg['region'])
        ssBoto = Config.get('ssBoto', None)

        self.waClient = ssBoto.client('wellarchitected', config=boto3Config)


    def checkIfReportExists(self):
        workload_name = self.cfg['reportName']
        try:
            # List workloads with the given name prefix
            response = self.waClient.list_workloads(
                WorkloadNamePrefix=workload_name,
                MaxResults=50  # Adjust this value as needed
            )

            # Check if any workload matches the exact name
            for workload in response.get('WorkloadSummaries', []):
                if workload['WorkloadName'] == workload_name:
                    self.waInfo['isExists'] = True 
                    self.waInfo['WorkloadId'] = workload['WorkloadId']

        except Exception as e:
            _warn(f"Error checking if workload exists: {str(e)}")
            self.HASPERMISSION = False
            return False, None
        
    def createReportIfNotExists(self):
        workload_name = self.cfg['reportName']
        self.checkIfReportExists()

        if self.HASPERMISSION == False:
            return False

        if self.waInfo['isExists'] == True:
            return True

        wLargs = {
            'WorkloadName': workload_name,
            'Description': 'Auto generated by ServiceScreener',
            'Environment': 'PRODUCTION',
            'AccountIds': [self.stsInfo['Account']],
            'AwsRegions': self.region,
            'ReviewOwner': self.stsInfo['Arn'],
            'Lenses': [self.waInfo['LensesAlias']]
        }

        try:
            response = self.waClient.create_workload(**wLargs)
            self.waInfo['WorkloadId'] = response['WorkloadId']
            return True
        except Exception as e:
            self.HASPERMISSION = False
            print(f"An error occurred while creating the workload: {str(e)}")
            return False
        
    def createMilestoneIfNotExists(self):
        if self.cfg['newMileStone'] == 1:
            self.createMilestone()
            return

        all_milestones = []
        next_token = None

        try:
            while True:
                params = {
                    'WorkloadId': self.waInfo['WorkloadId'],
                    'MaxResults': 20
                }
                if next_token:
                    params['NextToken'] = next_token

                response = self.waClient.list_milestones(**params)
                all_milestones.extend(response['MilestoneSummaries'])

                next_token = response.get('NextToken')
                if not next_token:
                    break  # No more pages, exit the loop

            if not all_milestones:
                print(f"No milestones found for workload {workload_id}... creating milestone...")
                self.createMilestone()
                return None

            # Sort milestones by date (most recent first)
            sorted_milestones = sorted(
                all_milestones,
                key=lambda x: x['RecordedAt'],
                reverse=True
            )

            # Get the latest milestone
            latest_milestone = sorted_milestones[0]
            self.waInfo['MilestoneName'] = latest_milestone['MilestoneName']
            self.waInfo['MilestoneNumber'] = latest_milestone['MilestoneNumber']
        
        except BotoCoreError as e:
            print(f"An error occurred: {str(e)}")
            return None
        
    def createMilestone(self):
        cdate = datetime.now().strftime('%Y%m%d%H%M%S')
        milestoneName = 'SS-{}'.format(cdate)

        try:
            resp = self.waClient.create_milestone(
                WorkloadId=self.waInfo['WorkloadId'],
                MilestoneName=milestoneName
            )
            
            print(f"Milestone Number: {resp['MilestoneNumber']}")

            self.waInfo['MilestoneName'] = milestoneName
            self.waInfo['MilestoneNumber'] = resp['MilestoneNumber']

            return True
        except BotoCoreError as e:
            self.HASPERMISSION = False
            _warn(f"An error occurred while creating the milestone: {str(e)}")
            return None
        
    def listAnswers(self):
        if self.HASPERMISSION == False:
            return None

        next_token = None
        ansArgs = {
            'WorkloadId': self.waInfo['WorkloadId'],
            'LensAlias': self.waInfo['LensesAlias'],
            'PillarId': self.pillarId,
            # 'MilestoneNumber': self.waInfo['MilestoneNumber'],
            'MaxResults': 50
        }

        isSuccess = False
        maxRetry = 3
        currAttempt = 0
        while True:
            currAttempt = currAttempt + 1
            try:
                resp = self.waClient.list_answers(**ansArgs)
                isSuccess = True
                break
            except botocore.errorfactory.ResourceNotFoundException:
                # wait for 3 seconds before retrying
                print("*** [WATools] ListAnswer failed, waiting workload to be generated, retry in 3 seconds")
                if currAttempt >= maxRetry:
                    break
                time.sleep(3)
                
        if isSuccess == False:
            print("*** [WATools] Unable to retrieve list of checklists, skipped WATool integration")
            return None

        answers = []
        try:
            while True:
                if next_token:
                    ansArgs['nextToken'] = next_token

                resp = self.waClient.list_answers(**ansArgs)
                # print(resp['AnswerSummaries'])
                answers.extend(resp['AnswerSummaries'])

                next_token = resp.get('NextTOken')
                if not next_token:
                    break
        except BotoCoreError as e:
            _warn(f"[ERROR - WATOOLS]: {str(e)}")
            self.HASPERMISSION = False
            return None

        i = 1
        j = 1
        answerSets = {}
        for ans in answers:
            j = 1
            answerSets[f'{i:02}'] = [ans['QuestionId'], ans['QuestionTitle']]
            # print(ans['QuestionId'])
            for choice in ans['Choices']:
                # print(choice)
                fkey = f'{i:02}::{j:02}'
                answerSets[fkey] = [choice['ChoiceId'], choice['Title']]
                j = j+1
        
            i = i+1
            
        self.answerSets = answerSets
    
    def updateAnswers(self, questionId, selectedChoices, unselectedNotes):
        if self.HASPERMISSION == False:
            return None

        ansArgs = {
            'WorkloadId': self.waInfo['WorkloadId'],
            'LensAlias': self.waInfo['LensesAlias'],
            'QuestionId': questionId, 
            'SelectedChoices': selectedChoices,
            'Notes': unselectedNotes
        }

        try:
            resp = self.waClient.update_answer(**ansArgs)
        except BotoCoreError as e:
            _warn(f"[ERROR - WATOOLS]: {str(e)}")
            self.HASPERMISSION = False
            return None

        pass
'''
stsInfo = {'UserId': 'AIDA55JZ3XKTBZPEJU5K7', 'Account': '956288449190', 'Arn': 'arn:aws:iam::956288449190:user/macbook-ss'}
Config.set('stsInfo', stsInfo)

Config.set('REGIONS_SELECTED', ['ap-southeast-1', 'us-east-1'])

boto3args = {'region_name': 'ap-southeast-1'}
Config.set('ssBoto', boto3.Session(**boto3args))

myCfg = '{"WA": {"region": "ap-southeast-1", "reportName":"SS_Report", "newMileStone":0}}'
cfg = json.loads(myCfg)

o = WATools()
o.init(cfg['WA'])
o.createReportIfNotExists()
resp = o.listAnswers('security')
# resp = o.createMilestoneIfNotExists()
print(o.waInfo)
print(resp)
'''