import boto3


SESSION_ARGS = ('aws_access_key_id',
                'aws_secret_access_key',
                'aws_session_token',
                'region_name',
                'botocore_session',
                'profile_name')

SERVICE_ARGS = ('region_name',
                'api_version',
                'use_ssl',
                'verify',
                'endpoint_url',
                'aws_access_key_id',
                'aws_secret_access_key',
                'aws_session_token',
                'config')


def dict_subset(keys, **kwargs):
    return {k: v for k, v in kwargs.items() if k in keys}


class Account:

    def __init__(self, **kwargs):
        self.instances = list()
        self.session = None
        self.ec2 = None
        self._new_session(**dict_subset(SESSION_ARGS, **kwargs))

    def _new_session(self, **kwargs):
        self.session = boto3.Session(**kwargs)
        self.ec2 = self.session.resource('ec2', **dict_subset(SERVICE_ARGS, **kwargs))

    def update_instances(self):
        self.instances = self.ec2.instances.all()

    def __len__(self):
        return len([i for i in self.instances])


class InstanceSet:

    def __init__(self, label, account):
        self.label = label
        self.account = account
        self.instances = [i for i in account.instances]

    def reset(self):
        self.instances = [i for i in self.account.instances]

    def get_names(self):
        names = list()
        for i in self.instances:
            d = dict()
            for tag in i.tags:
                d[tag['Key']] = tag['Value']
                names.append(d['Name'])
        return names

    def get_ids(self):
        return [i.instance_id for i in self.instances]

    def filter_on_names(self, names, mode='blacklist'):
        z = zip(self.get_names(), self.instances)
        self._filter(mode, names, z)

    def filter_on_ids(self, ids, mode='blacklist'):
        z = zip(self.get_ids(), self.instances)
        self._filter(mode, ids, z)

    def _filter(self, mode, labels, z):
        # Z is a zip object with format zip(label, instance)
        if mode not in ['whitelist', 'blacklist']:
            raise ValueError('Expected mode to be "whitelist" or "blacklist".')
        new = list()
        if isinstance(labels, str):
            labels = [labels]
        for label, instance in z:
            if label in labels and mode == 'blacklist':
                continue
            elif label not in labels and mode == 'whitelist':
                continue
            else:
                new.append(instance)
        self.instances = new
