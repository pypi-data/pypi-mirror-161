from heaserver.service.runner import init_cmd_line, routes, start
from heaserver.service.db import awsservicelib
from heaserver.service.db import database
from heaserver.service.db.aws import S3Manager
from heaserver.service.wstl import builder_factory, action
from heaserver.service import response
from aiohttp import web, hdrs
import mimetypes
import logging
from typing import Union
from multidict import istr

_logger = logging.getLogger(__name__)

# Non-standard mimetypes that we may assign to files in AWS S3 buckets.
MIME_TYPES = {'application/x.fastq': ['.fq', '.fastq'],  # https://en.wikipedia.org/wiki/FASTQ_format
              'application/x.vcf': ['.vcf'],  # https://en.wikipedia.org/wiki/Variant_Call_Format
              'application/x.fasta': ['.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn'],  # https://en.wikipedia.org/wiki/FASTA_format
              'application/x.sam': ['.sam'],  # https://en.wikipedia.org/wiki/SAM_(file_format)
              'application/x.bam': ['.bam'],  # https://support.illumina.com/help/BS_App_RNASeq_Alignment_OLH_1000000006112/Content/Source/Informatics/BAM-Format.htm#:~:text=A%20BAM%20file%20(*.,file%20naming%20format%20of%20SampleName_S%23.
              'application/x.bambai': ['.bam.bai'],  # https://support.illumina.com/help/BS_App_RNASeq_Alignment_OLH_1000000006112/Content/Source/Informatics/BAM-Format.htm#:~:text=A%20BAM%20file%20(*.,file%20naming%20format%20of%20SampleName_S%23.
              'application/x.gff3': ['.gff'],  # https://en.wikipedia.org/wiki/General_feature_format and https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
              'application/x.gvf': ['.gvf']  # https://github.com/The-Sequence-Ontology/Specifications/blob/master/gvf.md
             }


@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok()


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
async def get_file_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a file resource.

    :param request: the HTTP request (required).
    :return: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '404':
        $ref: '#/components/responses/404'
    """
    resp = await awsservicelib.has_file(request)
    if resp.status == 200:
        return await response.get_options(request, ['GET', 'POST', 'DELETE', 'HEAD', 'OPTIONS'])
    else:
        headers: dict[Union[str, istr], str] = {hdrs.CONTENT_TYPE: 'text/plain; charset=utf-8'}
        return response.status_generic(status=resp.status, body=resp.text, headers=headers)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator')
@action(name='heaserver-awss3files-file-duplicate-form', path='/awss3files/{folder_id}/items/{id}')
async def get_file_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested file.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested file was not found.
    """
    return await awsservicelib.get_file(request)


@routes.put('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/content')
async def put_file_content(request: web.Request) -> web.Response:
    """
        :param request:
        :return:
        ---
        summary: File content
        tags:
            - heaserver-files-aws-s3
        parameters:
            - name: volume_id
              in: path
              required: true
              description: The id of the volume to retrieve.
              schema:
                type: string
              examples:
                example:
                  summary: A volume id
                  value: 666f6f2d6261722d71757578
            - name: bucket_id
              in: path
              required: true
              description: The id of the bucket to retrieve.
              schema:
                type: string
              examples:
                example:
                  summary: A bucket id
                  value: my-bucket
            - $ref: '#/components/parameters/id'
        requestBody:
            description: File contents.
            required: true
            content:
                application/octet-stream:
                    schema:
                        type: string
                        format: binary
        responses:
          '404':
            $ref: '#/components/responses/404'
        """
    return await awsservicelib.put_object_content(request)

@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/content')
async def get_file_content(request: web.Request) -> web.StreamResponse:
    """
    :param request:
    :return:
    ---
    summary: File content
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.get_object_content(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
@action(name='heaserver-awss3files-file-get-properties', rel='hea-properties')
@action(name='heaserver-awss3files-file-duplicate', rel='hea-duplicator', path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator')
@action('heaserver-awss3files-file-get-open-choices', rel='hea-opener-choices',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener')
async def get_file(request: web.Request) -> web.Response:
    """
    Gets the file with the specified id.

    :param request: the HTTP request.
    :return: the requested file or Not Found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.get_file(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/byname/{name}')
async def get_file_by_name(request: web.Request) -> web.Response:
    """
    Gets the file with the specified name.

    :param request: the HTTP request.
    :return: the requested file or Not Found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.get_file_by_name(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files')
@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/')
@action(name='heaserver-awss3files-file-get-properties', rel='hea-properties')
@action(name='heaserver-awss3files-file-duplicate', rel='hea-duplicator', path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/duplicator')
@action('heaserver-awss3files-file-get-open-choices', rel='hea-opener-choices',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener')
async def get_files(request: web.Request) -> web.Response:
    """
    Gets the file with the specified id.

    :param request: the HTTP request.
    :return: the requested file or Not Found.
    ---
    summary: A specific file.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.get_all_files(request)

@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3files')
@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{bucket_id}/awss3files/')
async def get_files_options(request: web.Request) -> web.Response:
    """
    Gets the allowed HTTP methods for a files resource.

    :param request: the HTTP request (required).
    :response: the HTTP response.
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await database.get_options(request, ['GET', 'DELETE', 'HEAD', 'OPTIONS'], awsservicelib.has_bucket)


@routes.delete('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}')
async def delete_file(request: web.Request) -> web.Response:
    """
    Deletes the file with the specified id.

    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: File deletion
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.delete_file(request)


@routes.get('/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/opener')
@action('heaserver-awss3files-file-open-default', rel='hea-opener hea-default',
        path='/volumes/{volume_id}/buckets/{bucket_id}/awss3files/{id}/content')
async def get_file_opener(request: web.Request) -> web.Response:
    """
    Opens the requested file.

    :param request: the HTTP request. Required.
    :return: the opened file, or Not Found if the requested file does not exist.
    ---
    summary: File opener choices
    tags:
        - heaserver-files-aws-s3
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await awsservicelib.get_file(request)


def main():
    for mime_type, extensions in MIME_TYPES.items():
        for extension in extensions if isinstance(extensions, list) else [extensions]:
            mimetypes.add_type(mime_type, extension)
    config = init_cmd_line(description='Repository of files in AWS S3 buckets', default_port=8080)
    start(db=S3Manager, wstl_builder_factory=builder_factory(__package__), config=config)
