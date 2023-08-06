from collections import defaultdict
from glob import glob
import logging
import os
import posixpath
import socket
import sys
from typing import Sequence, Dict

from raft import task
import yaml
from boto3 import Session
from sewer.auth import ErrataItemType
from sewer.client import Client
from sewer.config import ACME_DIRECTORY_URL_STAGING  # noqa: F401, pylint: disable=unused-import
from sewer.dns_providers.common import dns_challenge
from sewer.dns_providers.route53 import Route53Dns as SewerRoute53Dns


log = logging.getLogger(__name__)


class Route53Dns(SewerRoute53Dns):
    def __init__(self, profile=None):
        super().__init__()
        self.session = Session(profile_name=profile)
        self.r53 = self.session.client('route53', config=self.aws_config)
        self.waiter = self.r53.get_waiter('resource_record_sets_changed')
        self.resource_records = defaultdict(set)

    def setup(self, challenges: Sequence[Dict[str, str]]) -> Sequence[ErrataItemType]:
        for x in challenges:
            domain_name = x['ident_value']
            value = dns_challenge(x['key_auth'])
            challenge_domain = f'_acme-challenge.{domain_name}.'
            self.resource_records[challenge_domain].add(value)
        self.create_dns_record(domain_name=None, domain_dns_value=None)
        return []

    def change_batch(self, action, changes):
        return {
            'Comment': f'letsencrypt dns certificate validation {action}',
            'Changes': [{
                'Action': action,
                'ResourceRecordSet': {
                    'Name': name,
                    'Type': 'TXT',
                    'TTL': self.ttl,
                    'ResourceRecords': [
                        dict(Value=f'"{value}"')
                        for value in values
                    ],
                },
            } for name, values in changes.items()],
        }

    def by_zone_id(self):
        by_zone_id = defaultdict(lambda: defaultdict(set))
        for name, values in self.resource_records.items():
            zone_id = self._find_zone_id_for_domain(name)
            by_zone_id[zone_id][name] = values
        return by_zone_id

    def wait(self, zone_id, change_id):
        log.info('[route53 / %s] waiting for %s', zone_id, change_id)
        self.waiter.wait(Id=change_id, WaiterConfig=dict(
            Delay=5,
            MaxAttempts=24,
        ))
        log.info('[route53 / %s] change is complete', zone_id)

    def create_dns_record(self, domain_name=None, domain_dns_value=None):
        result = {}
        if domain_name and domain_dns_value:
            self.resource_records[domain_name].add(domain_dns_value)
        for name, values in self.resource_records.items():
            log.info('[route53] adding TXT %s => %s', name, values)
        for zone_id, changes in self.by_zone_id().items():
            response = self.r53.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=self.change_batch('UPSERT', changes),
            )
            change_id = response['ChangeInfo']['Id']
            result[zone_id] = change_id
        for zone_id, change_id in result.items():
            self.wait(zone_id, change_id)
        return result

    def clear(self, challenges: Sequence[Dict[str, str]]) -> Sequence[ErrataItemType]:
        self.delete_dns_record(None, None)
        return []

    def delete_dns_record(self, domain_name=None, domain_dns_value=None):
        result = {}
        if domain_name and domain_dns_value:
            self.resource_records[domain_name].add(domain_dns_value)
        for name, values in self.resource_records.items():
            log.info('[route53] removing TXT %s => %s', name, values)
        for zone_id, changes in self.by_zone_id().items():
            response = self.r53.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=self.change_batch('DELETE', changes),
            )
            change_id = response['ChangeInfo']['Id']
            result[zone_id] = change_id
        for zone_id, change_id in result.items():
            self.wait(zone_id, change_id)
        return result


def new_cert(hostname, alt_domains, email=None, profile=None):
    """
    :param str hostname:
        the fqdn of the local host for which we are creating the cert

    :param str alt_domains:
        a comma-separated list of alternative domains to also
        requests certs for.

    :param str email:
        the email of the contact on the cert

    :param str profile:
        the name of the aws profile to use to connect boto3 to
        appropriate credentials
    """
    alt_domains = alt_domains.split(',') if alt_domains else []
    client = Client(
        hostname, domain_alt_names=alt_domains, contact_email=email,
        provider=Route53Dns(profile), ACME_AUTH_STATUS_WAIT_PERIOD=5,
        ACME_AUTH_STATUS_MAX_CHECKS=180, ACME_REQUEST_TIMEOUT=60,
        LOG_LEVEL='INFO')
    certificate = client.cert()
    account_key = client.account_key
    key = client.certificate_key
    return certificate, account_key, key


def get_certificate(ns, hostname, profile=None):
    if not ns.startswith('/'):
        ns = f'/{ns}'
    hostname = hostname.replace('*', 'star')
    try:
        session = Session(profile_name=profile)
        ssm = session.client('ssm')
        name = '/'.join([ ns, 'apps_keystore', hostname, 'account_key' ])
        account_key = get_chunked_ssm_parameter(name, profile=profile)
        log.info('account key retrieved')
        name = '/'.join([ ns, 'apps_keystore', hostname, 'key' ])
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        key = response['Parameter']['Value']
        log.info('private key retrieved')
        name = '/'.join([ ns, 'apps_keystore', hostname, 'cert' ])
        certificate = get_chunked_ssm_parameter(name, profile=profile)
        log.info('public cert retrieved')
    except:  # noqa: E722, pylint: disable=bare-except
        account_key = None
        key = None
        certificate = None
    return certificate, account_key, key


def get_file_from_s3(s3, bucket, ns, filename, decode=True):
    filename = filename.replace('*', 'star')
    key = filename
    if ns:
        key = posixpath.join(ns, key)
    log.info('retrieving s3://%s/%s', bucket, key)
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    if decode:
        data = data.decode('utf-8')
    return data


def get_certificate_from_s3(bucket, ns, hostname, profile=None):
    hostname = hostname.replace('*', 'star')
    account_key = None
    key_content = None
    certificate = None
    try:
        session = Session(profile_name=profile)
        s3 = session.client('s3')
    except Exception as ex:  # noqa: E722, pylint: disable=broad-except,
        log.info('exception connecting to s3: %s', ex)
        return certificate, account_key, key_content

    try:
        account_key = get_file_from_s3(s3, bucket, None, 'global.account_key')
        log.info('account key retrieved')
    except Exception as ex:  # noqa: E722, pylint: disable=broad-except,
        log.info('exception getting account key: %s', ex)

    try:
        key_content = get_file_from_s3(s3, bucket, ns, f'{hostname}.key')
        log.info('private key retrieved')
    except Exception as ex:  # noqa: E722, pylint: disable=broad-except,
        log.info('exception getting private key: %s', ex)

    try:
        certificate = get_file_from_s3(s3, bucket, ns, f'{hostname}.crt')
        log.info('public cert retrieved')
    except Exception as ex:  # noqa: E722, pylint: disable=broad-except,
        log.info('exception retrieving public cert: %s', ex)
    return certificate, account_key, key_content


def get_chunked_ssm_parameter(name, profile=None):
    session = Session(profile_name=profile)
    ssm = session.client('ssm')
    rg = []
    for n in range(1, 10):
        try:
            st = f'{name}{n}'
            log.info('[ssm]  getting %s', st)
            response = ssm.get_parameter(Name=st, WithDecryption=True)
            rg.append(response['Parameter']['Value'])
        except:  # noqa: E722, pylint: disable=bare-except
            break
    data = ''.join(rg)
    return data


def get_pfx(ns, hostname, bucket, profile=None):
    session = Session(profile_name=profile)
    s3 = session.client('s3')
    hostname = hostname.replace('*', 'star')
    pfx_data = get_file_from_s3(s3, bucket, ns, f'{hostname}.pfx', False)
    log.info('[pfx]  read %s bytes', len(pfx_data))
    return pfx_data


def renew_cert(
        ns, hostname, alt_domains=None,
        email=None, bucket=None, tmp_dir=None, profile=None, **kwargs):
    if alt_domains:
        if isinstance(alt_domains, str):
            alt_domains = alt_domains.split(',')
    else:
        alt_domains = []
    _, account_key, key = get_certificate_from_s3(bucket, ns, hostname, profile)
    client = Client(
        hostname, domain_alt_names=alt_domains, contact_email=email,
        provider=Route53Dns(profile), account_key=account_key,
        certificate_key=key, ACME_AUTH_STATUS_WAIT_PERIOD=5,
        ACME_AUTH_STATUS_MAX_CHECKS=360, ACME_REQUEST_TIMEOUT=3)
    if not account_key:
        client.acme_register()
        content = client.account_key
        save_account_key(bucket, ns, content, tmp_dir, profile)
    if not key:
        client.create_certificate_key()
        content = client.certificate_key
        save_key(bucket, ns, hostname, content, tmp_dir, profile)
    certificate = client.renew()
    account_key = client.account_key
    key = client.certificate_key
    return certificate, account_key, key


def save_account_key(bucket, ns, content, tmp_dir, profile):
    session = Session(profile_name=profile)
    s3 = session.client('s3')
    filename = 'global.account_key'
    save_to_temp(tmp_dir, filename, content)
    if isinstance(content, str):
        content = content.encode('utf-8')
    s3_key = filename
    s3.put_object(Bucket=bucket, Key=s3_key, Body=content, ACL='bucket-owner-full-control')


def save_key(bucket, ns, hostname, content, tmp_dir, profile):
    session = Session(profile_name=profile)
    s3 = session.client('s3')
    hostname = hostname.replace('*', 'star')
    filename = f'{hostname}.key'
    save_to_temp(tmp_dir, filename, content)
    if isinstance(content, str):
        content = content.encode('utf-8')
    s3_key = posixpath.join(ns, filename)
    s3.put_object(Bucket=bucket, Key=s3_key, Body=content, ACL='bucket-owner-full-control')


def pfx(ctx, certificate, key):
    f1, f2, f3 = '/tmp/p1.crt', '/tmp/p1.key', '/tmp/p1.pfx'
    with open(f1, 'w') as f:
        f.write(certificate)
    with open(f2, 'w') as f:
        f.write(key)
    os.chmod(f1, 0o644)
    os.chmod(f2, 0o600)
    ctx.run(
        f'/usr/bin/openssl pkcs12 -export -in {f1} -inkey {f2}'
        f' -out {f3} -passout pass:')
    with open(f3, 'rb') as f:
        data = f.read()
    os.remove(f1)
    os.remove(f2)
    os.remove(f3)
    return data


def full_pfx(ctx, certificate, key, tmp_dir='/tmp'):
    f1 = os.path.join(tmp_dir, 'p1.crt')
    f2 = os.path.join(tmp_dir, 'p1.key')
    f3 = os.path.join(tmp_dir, 'p1.pfx')
    with open(f1, 'w') as f:
        f.write(certificate)
    with open(f2, 'w') as f:
        f.write(key)
    os.chmod(f1, 0o644)
    os.chmod(f2, 0o600)
    ctx.run(
        f'/usr/bin/openssl pkcs12 -export -in {f1} -inkey {f2}'
        f' -out {f3} -passout pass:')
    with open(f3, 'rb') as f:
        data = f.read()
    os.remove(f1)
    os.remove(f2)
    os.remove(f3)
    return data


@task
def renew_all(ctx, dir_name=None, profile=None):
    """
    Requests a letsencrypt cert using route53 and sewer, also requests
    wildcard certs based on the provided hostname

    :param raft.context.Context ctx:
        the raft-provided context

    :param str dir_name:
        the config directory

    :param str profile:
        the name of the aws profile to use to connect boto3 to
        appropriate credentials

    """
    default_filename = os.path.join(dir_name, 'defaults.yml')
    defaults = {}
    if os.path.exists(default_filename):
        with open(default_filename, 'r') as f:
            defaults = yaml.load(f, Loader=yaml.SafeLoader)
    defaults = defaults or {}
    dir_name = os.path.join(dir_name, '*.yml')
    files = glob(dir_name)
    for filename in files:
        try:
            # don't let the failure of any one certificate
            # make it so that we don't try to renew the rest
            if filename.endswith('defaults.yml'):
                continue
            request_cert(ctx, filename, profile, defaults)
        except:
            pass


def request_cert(ctx, filename, profile, defaults):
    log.info('processing %s', filename)
    with open(filename, 'r') as f:
        values = yaml.load(f, Loader=yaml.SafeLoader)
    for key, value in defaults.items():
        values.setdefault(key, value)
    namespaces = values.pop('namespaces', [])
    config_profile = values.pop('profile', None)
    profile = profile or config_profile
    ns = namespaces[0]
    certificate, account_key, key = renew_cert(
        **values, ns=ns, profile=profile)
    tmp_dir = values.pop('tmp_dir', '/tmp')
    bucket = values.pop('bucket')
    for x in namespaces:
        save_to_file(
            ctx, tmp_dir, values['hostname'],
            certificate, account_key, key)
        save_to_s3(
            ctx, bucket, x, values['hostname'], certificate,
            account_key, key, tmp_dir=tmp_dir, profile=profile)


@task
def request(ctx, filename=None, profile=None):
    """
    Requests a letsencrypt cert using route53 and sewer, also requests
    wildcard certs based on the provided hostname

    :param raft.context.Context ctx:
        the raft-provided context

    :param str filename:
        the config file

    :param str profile:
        the name of the aws profile to use to connect boto3 to
        appropriate credentials

    """
    default_filename = os.path.join(os.path.dirname(filename), 'defaults.yml')
    defaults = {}
    if os.path.exists(default_filename):
        with open(default_filename, 'r') as f:
            defaults = yaml.load(f, Loader=yaml.SafeLoader)
    defaults = defaults or {}
    request_cert(ctx, filename, profile, defaults)


def save_to_temp(tmp_dir, filename, content):
    filename = os.path.join(tmp_dir, filename)
    log.info('saving %s', filename)
    filename = filename.replace('*', 'star')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, 0o755, True)
    if isinstance(content, str):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        with open(filename, 'wb') as f:
            f.write(content)


def save_to_file(ctx, tmp_dir, hostname, certificate, account_key, key):
    """
    saves the contents of the certificate, key, and account keys
    to a local directory for debugging
    """
    contents = [
        ('.crt', certificate),
        ('.account_key', account_key),
        ('.key', key),
    ]
    for extension, content in contents:
        filename = f'{hostname}{extension}'
        save_to_temp(tmp_dir, filename, content)


def save_to_s3(ctx, bucket, ns, hostname, certificate, account_key, key,
               tmp_dir='/tmp', profile=None):
    """
    saves the contents of the certificate, key, and account keys
    to a local directory for debugging
    """
    pfx_content = full_pfx(ctx, certificate, key)
    contents = [
        ('.crt', certificate),
        ('.key', key),
        ('.pfx', pfx_content),
    ]
    session = Session(profile_name=profile)
    s3 = session.client('s3')
    for extension, content in contents:
        filename = f'{hostname}{extension}'
        filename = filename.replace('*', 'star')
        filename = posixpath.join(ns, filename)
        log.info('saving s3://%s/%s', bucket, filename)
        if isinstance(content, str):
            content = content.encode('utf-8')
        s3.put_object(Bucket=bucket, Key=filename, Body=content, ACL='bucket-owner-full-control')


def save_to_ssm(ctx, ns, hostname, certificate, account_key, key, profile=None):
    session = Session(profile_name=profile)
    ssm = session.client('ssm')
    pfx_data = pfx(ctx, certificate, key)
    hostname = hostname.replace('*', 'star')
    prefix = ns
    if not prefix.startswith('/'):
        prefix = f'/{prefix}'
    prefix = os.path.join(prefix, 'apps_keystore', hostname)
    contents = [
        ('account_key', account_key),
        ('cert', certificate),
    ]
    for suffix, content in contents:
        name = os.path.join(prefix, suffix)
        log.info('saving %s', name)
        save_chunked_ssm_parameter(ns, name, content, 'String', profile)

    contents = [
        ('key', key),
    ]
    for suffix, content in contents:
        name = os.path.join(prefix, suffix)
        log.info('saving %s', name)
        try:
            ssm.put_parameter(
                Name=name,
                Description=f'sewer / certbot {suffix}',
                Value=content,
                Overwrite=True,
                Type='SecureString',
                KeyId=f'alias/{ns}')
        except Exception as ex:  # pylint: disable=broad-except
            log.info('exception saving to ssm: %s', ex)

    name = os.path.join(prefix, 'pfx')
    save_chunked_ssm_parameter(ns, name, pfx_data, 'SecureString', profile)


def save_chunked_ssm_parameter(ns, name, value, type_, profile=None):
    session = Session(profile_name=profile)
    ssm = session.client('ssm')
    pieces = []
    while value:
        pieces.append(value[:4096])
        value = value[4096:]
    for n, x in enumerate(pieces, 1):
        st = f'{name}{n}'
        log.info('saving %s', st)
        try:
            if type_ == 'SecureString':
                ssm.put_parameter(
                    Name=st,
                    Description='sewer / certbot',
                    Value=x,
                    Overwrite=True,
                    Type=type_,
                    KeyId=f'alias/{ns}')
            else:
                ssm.put_parameter(
                    Name=st,
                    Description='sewer / certbot',
                    Value=x,
                    Overwrite=True,
                    Type=type_)
        except Exception as ex:  # pylint: disable=broad-except
            log.info('exception saving to ssm: %s', ex)


@task
def install_cert(ctx, config, hostname=None):
    """
    installs a cert on the local system:

        on linux to /etc/ssl/certs
        on windows to cert:/localmachine/my
    """
    with open(config, 'r') as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)
    ns = conf['namespace']
    profile = conf.get('profile')
    owner = conf.get('owner', 'root')
    group = conf.get('group', owner)
    cert_filename = conf.get('certificate')
    key_filename = conf.get('key')
    hostname = hostname or conf.get('hostname')
    bucket = conf.get('bucket')
    if not hostname:
        hostname = get_hostname(ctx)
    if is_linux():
        install_cert_on_linux(
            ctx, ns, hostname, profile,
            cert_filename, key_filename, owner, group, bucket=bucket)
    elif is_windows():
        install_cert_on_windows(
            ctx, ns, hostname, profile)


def get_hostname(ctx):
    if is_linux():
        result = ctx.run('/bin/hostname')
        return result.stdout.strip()
    if is_windows():
        result = socket.getfqdn()
        return result
    return None


def install_cert_on_linux(
        ctx, ns, hostname, profile, cert_filename, key_filename,
        owner, group, bucket=None):
    if bucket:
        certificate, _, key = get_certificate_from_s3(bucket, ns, hostname, profile)
    else:
        certificate, _, key = get_certificate(ns, hostname, profile)
    if not cert_filename:
        st = f'{hostname}.bundled.crt'
        cert_filename = os.path.join('/etc/ssl/certs', st)
    if not key_filename:
        key_filename = os.path.join('/etc/ssl/private', f'{hostname}.key')
    with open(cert_filename, 'w') as f:
        f.write(certificate)
    ctx.run(f'chmod 0644 {cert_filename}')
    ctx.run(f'chown {owner}:{group} {cert_filename}')
    with open(key_filename, 'w', encoding='utf-8') as f:
        f.write(key)
    ctx.run(f'chmod 0600 {key_filename}')
    ctx.run(f'chown {owner}:{group} {key_filename}')


@task
def install_cert_on_windows(ctx, ns, hostname, profile):
    """
    not yet implemented -- have to find a good, cost-effective way
    to generate the pfx file and store to ssm
    """
    pfx_data = get_pfx(ns, hostname, profile)
    c = 'powershell.exe -command "[System.IO.Path]::GetTempFileName()"'
    result = ctx.run(c)
    filename = result.stdout.strip()
    with open(filename, 'wb') as f:
        f.write(pfx_data)
    c = (
        'powershell.exe -command "'
        'Import-PfxCertificate '
        r'  -CertStoreLocation cert:\localmachine\my'
        f' -filepath {filename}'
        f'"'
    )
    ctx.run(c)
    os.remove(filename)


def is_linux():
    return sys.platform == 'linux'


def is_windows():
    return sys.platform == 'win32'


@task
def create_account_key(ctx, filename):
    """
    creates an account key and saves it to filename
    """
    import OpenSSL
    key_type = OpenSSL.crypto.TYPE_RSA
    key = OpenSSL.crypto.PKey()
    key.generate_key(key_type, 2048)
    st = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
    with open(filename, 'w') as f:
        f.write(st.decode())
