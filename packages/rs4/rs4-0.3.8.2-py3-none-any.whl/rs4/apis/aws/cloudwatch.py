from . import cw
from datetime import datetime, timedelta

INSTANCE_CREDITS = dict (
    nano = 72, micro = 144, small = 288, medium = 576, large = 864, xlarge = 1296
)
INSTANCE_CREDITS ["2xlarge"] = 1958

def get_credit_balance (instance):
    if not instance.instance_type.startswith ("t"):
        return

    response = cw.get_metric_statistics (
        Namespace='AWS/EC2',
        MetricName='CPUCreditBalance',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance.id
            },
        ],
        StartTime=datetime.utcnow () - timedelta (hours = 1),
        EndTime=datetime.utcnow () - timedelta (hours = 0),
        Period=300,
        Statistics=['Average', 'Minimum', 'Maximum'],
        Unit='Count'
    )
    lastest = response ["Datapoints"][-1]

    t, c = instance.instance_type.split (".")
    max_credits = INSTANCE_CREDITS [c]
    if t != 't2' and c in ('nano', 'micro', 'small'):
        max_credits *= 2

    return int (lastest ["Average"]), max_credits
