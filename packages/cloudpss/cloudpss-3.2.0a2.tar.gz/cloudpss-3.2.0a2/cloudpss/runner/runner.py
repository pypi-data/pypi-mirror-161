import threading
import json
import time
import random
from .receiver import Receiver
from .result import PowerFlowResult, EMTResult, Result, IESResult
from .storage import Storage
from ..utils import request

RECEIVER = {
    'default': Receiver,
}
RESULT_DB = {
    'job-definition/cloudpss/emtp': EMTResult,
    'job-definition/cloudpss/sfemt': EMTResult,
    'job-definition/cloudpss/power-flow': PowerFlowResult,
    'job-definition/cloudpss/ies-simulation': IESResult,
    'job-definition/cloudpss/ies-optimization': IESResult,
    'job-definition/cloudpss/three-phase-powerFlow': PowerFlowResult,
}


class Runner(object):
    def __init__(self, taskId, name, job, config, revision, modelRid,
                 **kwargs):

        self.taskId = taskId
        self.db = Storage(taskId, name, job, config, revision, modelRid)
        result = RESULT_DB.get(job['rid'], EMTResult)
        self.result = result(self.db)
        self.receiver = None

    def __listenStatus(self):
        if self.receiver is None:
            return False
        if self.receiver.status() == -1:
            raise Exception(self.receiver.error)
        return self.receiver.isOpen

    def status(self):
        """
        运行状态
        :return: 运行状态  0/1/-1 1 表示正常结束，0 表示运行中， -1 表示数据接收异常


        >>>> runner.status()  
        """
        if self.receiver is None:
            raise Exception('not find receiver')
        return self.receiver.status()

    def __listen(self, **kwargs):

        receiver = kwargs.get('RECEIVER', 'default')
        if type(receiver) is str:
            if receiver not in RECEIVER:
                receiver = RECEIVER['default']
            else:
                receiver = RECEIVER[receiver]
        self.receiver = receiver(self.taskId, self.db, **kwargs)
        self.receiver.connect()

    def terminate(self):
        """
        结束当前运行的算例

        """
        r = request("DELETE", 'api/simulation/runner/' + str(self.taskId))

    @staticmethod
    def create(revisionHash, job, config, name=None, rid='', **kwargs):
        '''
            创建一个运行任务

            :params: revision 项目版本号
            :params: job 调用仿真时使用的计算方案，为空时使用项目的第一个计算方案
            :params: config 调用仿真时使用的参数方案，为空时使用项目的第一个参数方案
            :params: name 任务名称，为空时使用项目的参数方案名称和计算方案名称
            :params: rid 项目rid，可为空

            :return: 返回一个运行实例

            >>> runner = Runner.runRevision(revision,job,config,'')
        '''
        taskId = str(int(time.time() * random.random()))
        runner = Runner(taskId, name, job, config, revisionHash, rid, **kwargs)
        event = threading.Event()

        thread = threading.Thread(target=runner.__listen, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()
        payload = {
            'args': config['args'],
            'job': job,
            'implement': kwargs.get('topology', None)
        }
        while not runner.__listenStatus():
            time.sleep(1)
        r = request('POST',
                    'api/simulation/runner/' + revisionHash + '/' +
                    str(taskId),
                    data=json.dumps(payload))

        return runner
