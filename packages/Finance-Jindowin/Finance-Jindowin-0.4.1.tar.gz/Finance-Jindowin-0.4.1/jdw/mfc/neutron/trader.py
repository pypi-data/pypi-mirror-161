from nameko.standalone.rpc import ClusterRpcProxy
from utils import current_date
from jdw.mfc import MQ_URL
from jdw.utils import split_list, create_task_id
import itertools,os

class Trader(object):
    def rodis(self, **kwargs):
        listeners = split_list(kwargs['listeners'],1)
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        trade_date = current_date().strftime(
            '%Y-%m-%d') if 'trade_date' not in kwargs else kwargs['trade_date']
        with ClusterRpcProxy(config) as rpc:
            for param in itertools.product(listeners):
                session_id = create_task_id(param)
                rpc.realtime_servicer.futures_rodis(
                    listeners=param,
                    trade_date=trade_date,
                    task_id=task_id, session=session_id)
        return task_id

    def staub(self, **kwargs):
        task_id = create_task_id(kwargs)
        config = {'AMQP_URI': MQ_URL}
        trade_date = current_date().strftime(
            '%Y-%m-%d') if 'trade_date' not in kwargs else kwargs['trade_date']
        with ClusterRpcProxy(config) as rpc:
            session_id = create_task_id(kwargs)
            rpc.realtime_servicer.futures_staub(
                listeners=kwargs['listeners'],
                account=kwargs['account'],
                trade_date=trade_date,
                task_id=task_id, session=session_id
            )