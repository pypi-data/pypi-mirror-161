"""
Runs integration tests for the HEA folder service.

Note that each test opens an aiohttp server listening on port 8080.
"""

from heaserver.service.testcase import microservicetestcase, expectedvalues
from heaserver.service.testcase.mockaws import MockS3Manager
from heaserver.fileawss3 import service
from heaobject import user
from heaobject.data import AWSS3FileObject
import importlib.resources as pkg_resources
from heaserver.service.testcase.dockermongo import RealRegistryContainerConfig
from heaserver.service.testcase.dockermongo import DockerMongoManager
from heaserver.service.testcase.testenv import DockerContainerConfig
from heaobject.registry import Resource
from heaobject.volume import DEFAULT_FILE_SYSTEM
from . import files

db_values = {'components': [
    {
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'invited': [],
        'modified': None,
        'name': 'reximus',
        'owner': user.NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.registry.Component',
        'version': None,
        'base_url': 'http://localhost:8080',
        'resources': [{'type': 'heaobject.registry.Resource', 'resource_type_name': AWSS3FileObject.get_type_name(),
                       'base_path': '/volumes'}]
    }
],
    'filesystems': [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'amazon_web_services',
        'owner': user.NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.AWSFileSystem',
        'version': None
    }],
    'volumes': [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'My Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'amazon_web_services',
        'owner': user.NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.Volume',
        'version': None,
        'file_system_name': 'amazon_web_services',
        'file_system_type': 'heaobject.volume.AWSFileSystem',
        'credential_id': None  # Let boto3 try to find the user's credentials.
    }],
    'buckets': [{
        "arn": None,
        "created": '2022-05-17T00:00:00+00:00',
        "derived_by": None,
        "derived_from": [],
        "description": None,
        "display_name": "arp-scale-2-cloud-bucket-with-tags11",
        "encrypted": True,
        "id": "arp-scale-2-cloud-bucket-with-tags11",
        "invites": [],
        "locked": False,
        "mime_type": "application/x.awsbucket",
        "modified": '2022-05-17T00:00:00+00:00',
        "name": "arp-scale-2-cloud-bucket-with-tags11",
        "object_count": None,
        "owner": "system|none",
        "permission_policy": None,
        "region": "us-west-2",
        "s3_uri": "s3://arp-scale-2-cloud-bucket-with-tags11/",
        "shares": [],
        "size": None,
        "source": None,
        "tags": [],
        "type": "heaobject.bucket.AWSBucket",
        "version": None,
        "versioned": False
    }],
    'awss3files': [{
        'created': '2022-05-17T00:00:00+00:00',
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'TextFileUTF8.txt',
        'id': 'VGV4dEZpbGVVVEY4LnR4dA==',
        'invites': [],
        'modified': '2022-05-17T00:00:00+00:00',
        'name': 'VGV4dEZpbGVVVEY4LnR4dA==',
        'owner': user.NONE_USER,
        'shares': [],
        'source': 'AWS Simple Cloud Storage (S3)',
        'storage_class': 'STANDARD',
        'type': AWSS3FileObject.get_type_name(),
        's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/TextFileUTF8.txt',
        'version': None,
        'mime_type': 'text/plain',
        'size': 1253952,
        'human_readable_size': '1.3 MB'
    },
        {
            'created': '2022-05-17T00:00:00+00:00',
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'BinaryFile',
            'id': 'QmluYXJ5RmlsZQ==',
            'invites': [],
            'modified': '2022-05-17T00:00:00+00:00',
            'name': 'QmluYXJ5RmlsZQ==',
            'owner': user.NONE_USER,
            'shares': [],
            'source': 'AWS Simple Cloud Storage (S3)',
            'storage_class': 'STANDARD',
            'type': AWSS3FileObject.get_type_name(),
            's3_uri': 's3://arp-scale-2-cloud-bucket-with-tags11/BinaryFile',
            'version': None,
            'mime_type': 'application/octet-stream',
            'size': 8673160,
            'human_readable_size': '8.7 MB'
        }
    ]
}

content = {
    'awss3files': {
        'VGV4dEZpbGVVVEY4LnR4dA==': b'arp-scale-2-cloud-bucket-with-tags11|' + pkg_resources.read_text(files,
                                                                                                       'TextFileUTF8.txt').encode(
            'utf-8'),
        'QmluYXJ5RmlsZQ==': b'arp-scale-2-cloud-bucket-with-tags11|' + pkg_resources.read_binary(files,
                                                                                                         'BinaryFile')
    }
}

HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0a24'
HEASERVER_VOLUMES_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-volumes:1.0.0a10'
HEASERVER_KEYCHAIN_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-keychain:1.0.0a4'
volume_microservice = DockerContainerConfig(image=HEASERVER_VOLUMES_IMAGE, port=8080, check_path='/volumes',
                                            resources=[Resource(resource_type_name='heaobject.volume.Volume',
                                                                base_path='/volumes',
                                                                file_system_name=DEFAULT_FILE_SYSTEM),
                                                       Resource(resource_type_name='heaobject.volume.FileSystem',
                                                                base_path='/filesystems',
                                                                file_system_name=DEFAULT_FILE_SYSTEM)],
                                            db_manager_cls=DockerMongoManager)
keychain_microservice = DockerContainerConfig(image=HEASERVER_KEYCHAIN_IMAGE, port=8080, check_path='/credentials',
                                              resources=[
                                                  Resource(resource_type_name='heaobject.keychain.Credentials',
                                                           base_path='/credentials',
                                                           file_system_name=DEFAULT_FILE_SYSTEM)],
                                              db_manager_cls=DockerMongoManager)

AWSS3FileTestCase = \
    microservicetestcase.get_test_case_cls_default(
        href='http://localhost:8080/volumes/666f6f2d6261722d71757578/buckets/arp-scale-2-cloud-bucket-with-tags11/awss3files/',
        wstl_package=service.__package__,
        coll='awss3files',
        fixtures=db_values,
        content=content,
        db_manager_cls=MockS3Manager,
        get_all_actions=[
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-properties',
                rel=['hea-properties']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-open-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener',
                rel=['hea-opener-choices']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-duplicate',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator',
                rel=['hea-duplicator'])],
        get_actions=[
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-properties',
                rel=['hea-properties']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-get-open-choices',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener',
                rel=['hea-opener-choices']),
            expectedvalues.Action(
                name='heaserver-awss3files-file-duplicate',
                url='http://localhost:8080/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator',
                rel=['hea-duplicator'])],
        duplicate_action_name='heaserver-awss3files-file-duplicate-form',
        put_content_status=204,
        exclude=['body_post', 'body_put'],
        registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
        other_docker_images=[volume_microservice, keychain_microservice])
