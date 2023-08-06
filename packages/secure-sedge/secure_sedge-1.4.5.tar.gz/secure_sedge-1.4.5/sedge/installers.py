import os
from raft import task
from raft.collection import Collection
import posixpath


@task
def pan(ctx, host, bucket, namespace, cert,
        profile=None, region=None, passphrase=None):
    """
    uploads the specified cert and key files to a panos device.  the username
    and password used to access the api must be specified by the
    PALO_ALTO_USERNAME and PALO_ALTO_PASSWORD environment variables
    """
    import requests
    from boto3 import Session
    from xml.etree import ElementTree as ET
    from OpenSSL.crypto import dump_privatekey
    from OpenSSL.crypto import load_privatekey
    from OpenSSL.crypto import FILETYPE_PEM
    session = requests.Session()
    session.verify = False
    aws_session = Session(profile_name=profile, region_name=region)
    s3 = aws_session.client('s3')
    s3_key = posixpath.join(namespace, cert)
    username = os.environ['PALO_ALTO_USERNAME']
    password = os.environ['PALO_ALTO_PASSWORD']
    base_url = f'https://{host}/api/'

    print('generating api key')
    data = dict(user=username, password=password)
    data['type'] = 'keygen'
    doc = session.post(base_url, data=data)
    root = ET.fromstring(doc.text)
    api_key = root.find('result/key').text
    session.headers = {
        'X-PAN-KEY': api_key,
    }

    print(f'reading cert from s3://{bucket}/{s3_key}')
    response = s3.get_object(Bucket=bucket, Key=f'{s3_key}.crt')

    print(f'importing certificate as {cert}')
    params = {
        'type': 'import',
        'category': 'certificate',
    }
    data = {
        'type': 'import',
        'category': 'certificate',
        'certificate-name': cert,
        'format': 'pem',
        'key': api_key,
    }
    files = dict(file=response['Body'].read())
    response = session.post(base_url, params=params, data=data, files=files)
    print(f'{response.text}')

    print(f'reading key from s3://{bucket}/{s3_key}.key')
    response = s3.get_object(Bucket=bucket, Key=f'{s3_key}.key')
    print(f'importing key to {cert}')
    params['category'] = data['category'] = 'private-key'
    # all private keys uploaded to the palo alto require a passphrase.
    # when the cert has no passphrase, add a passphrase of `stupid_palo_alto`
    # because, well, that's stupid.
    stupid_palo_alto = 'stupid_palo_alto'
    data['passphrase'] = passphrase or stupid_palo_alto
    x509_key = response['Body'].read()
    if not passphrase:
        x509_key = load_privatekey(FILETYPE_PEM, x509_key)
        x509_key = dump_privatekey(
            FILETYPE_PEM,
            x509_key,
            passphrase=stupid_palo_alto.encode())
    files = dict(file=x509_key)
    response = session.post(base_url, params=params, data=data, files=files)
    print(f'{response.text}')

    print(f'committing')
    xml = f'<commit><description>imported certificate from secure_sedge</description></commit>'
    data = {
        'type': 'commit',
        'cmd': xml,
        'key': api_key,
    }
    response = session.post(base_url, data=data)
    print(f'{response.text}')


installers_collection = Collection(
    pan,
)
