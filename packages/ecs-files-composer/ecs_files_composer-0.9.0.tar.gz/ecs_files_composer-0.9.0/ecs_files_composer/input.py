# generated by datamodel-codegen:
#   filename:  ecs-files-input.json
#   timestamp: 2022-07-28T09:25:01+00:00

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import AnyUrl, BaseModel, EmailStr, Extra, Field, constr


class Encoding(Enum):
    base64 = "base64"
    plain = "plain"


class Context(Enum):
    plain = "plain"
    jinja2 = "jinja2"


class UrlDef(BaseModel):
    url: Optional[AnyUrl] = Field(None, alias="Url")
    username: Optional[str] = Field(None, alias="Username")
    password: Optional[str] = Field(None, alias="Password")


class S3DefItem1(BaseModel):
    __root__: str = Field(
        ...,
        description="OneLiner with bucket ARN and path to key.",
        regex="^arn:aws(?:-[a-z]+)?:s3:::(\\S+)::(\\S+)$",
    )


class IamOverrideDef(BaseModel):
    role_arn: Optional[str] = Field(None, alias="RoleArn")
    session_name: Optional[str] = Field(
        "S3File@EcsConfigComposer",
        alias="SessionName",
        description="Name of the IAM session",
    )
    external_id: Optional[str] = Field(
        None,
        alias="ExternalId",
        description="The External ID to use when using sts:AssumeRole",
    )
    region_name: Optional[str] = Field(None, alias="RegionName")
    access_key_id: Optional[str] = Field(
        None, alias="AccessKeyId", description="AWS Access Key Id to use for session"
    )
    secret_access_key: Optional[str] = Field(
        None, alias="SecretAccessKey", description="AWS Secret Key to use for session"
    )
    session_token: Optional[str] = Field(None, alias="SessionToken")


class CommandsDef(BaseModel):
    __root__: List[str] = Field(..., description="List of commands to run")


class X509CertDef(BaseModel):
    class Config:
        extra = Extra.allow

    dir_path: Optional[str] = None
    email_address: Optional[EmailStr] = Field(
        "files-composer@compose-x.tld", alias="emailAddress"
    )
    common_name: Optional[
        constr(
            regex=r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]{0,61}[A-Za-z0-9])\Z"
        )
    ] = Field(None, alias="commonName")
    country_name: Optional[str] = Field("AW", alias="countryName", regex="^[A-Z]+$")
    locality_name: Optional[str] = Field("AWS", alias="localityName")
    state_or_province_name: Optional[str] = Field("AWS", alias="stateOrProvinceName")
    organization_name: Optional[str] = Field("AWS", alias="organizationName")
    organization_unit_name: Optional[str] = Field("AWS", alias="organizationUnitName")
    validity_end_in_seconds: Optional[float] = Field(
        8035200,
        alias="validityEndInSeconds",
        description="Validity before cert expires, in seconds. Default 3*31*24*60*60=3Months",
    )
    key_file_name: str = Field(..., alias="keyFileName")
    cert_file_name: str = Field(..., alias="certFileName")
    group: Optional[str] = Field(
        "root",
        description="UNIX group name or GID owner of the file. Default to root(0)",
    )
    owner: Optional[str] = Field(
        "root", description="UNIX user or UID owner of the file. Default to root(0)"
    )


class CertbotAwsStoreCertificate(BaseModel):
    storage_path: str = Field(
        ...,
        description="path to folder to store the certbot certificates into.",
        regex="^/[\\x00-\\x7F]+$",
    )
    table_name: Optional[str] = Field(
        "certbot-registry",
        description="dynamodb table name of the certbot-aws-store registry",
    )
    table_region_name: Optional[str] = Field(
        None,
        description="Region in which the table_name is. Defaults to profile default region, or eu-west-1",
    )


class Certificates(BaseModel):
    class Config:
        extra = Extra.forbid

    x509: Optional[Dict[str, X509CertDef]] = None


class Commands(BaseModel):
    post: Optional[CommandsDef] = Field(
        None, description="Commands to run after the file was retrieved"
    )
    pre: Optional[CommandsDef] = Field(
        None,
        description="Commands executed prior to the file being fetched, after `depends_on` completed",
    )


class SsmDef(BaseModel):
    parameter_name: Optional[str] = Field(None, alias="ParameterName")
    iam_override: Optional[IamOverrideDef] = Field(None, alias="IamOverride")


class SecretDef(BaseModel):
    secret_id: str = Field(..., alias="SecretId")
    version_id: Optional[str] = Field(None, alias="VersionId")
    version_stage: Optional[str] = Field(None, alias="VersionStage")
    json_key: Optional[str] = Field(
        None,
        alias="JsonKey",
        description="If the SecretString is a valid JSON, use the Key to map to the value stored in secret",
    )
    iam_override: Optional[IamOverrideDef] = Field(None, alias="IamOverride")


class S3DefItem(BaseModel):
    bucket_name: str = Field(
        ..., alias="BucketName", description="Name of the S3 Bucket"
    )
    bucket_region: Optional[str] = Field(
        None,
        alias="BucketRegion",
        description="S3 Region to use. Default will ignore or retrieve via s3:GetBucketLocation",
    )
    key: str = Field(..., alias="Key", description="Full path to the file to retrieve")
    iam_override: Optional[IamOverrideDef] = Field(None, alias="IamOverride")


class S3Def(BaseModel):
    __root__: Union[S3DefItem, S3DefItem1]


class SourceDef(BaseModel):
    url: Optional[UrlDef] = Field(None, alias="Url")
    ssm: Optional[SsmDef] = Field(None, alias="Ssm")
    s3: Optional[S3Def] = Field(None, alias="S3")
    secret: Optional[SecretDef] = Field(None, alias="Secret")


class FileDef(BaseModel):
    class Config:
        extra = Extra.allow

    path: Optional[str] = None
    content: Optional[str] = Field(
        None, description="The raw content of the file to use"
    )
    source: Optional[SourceDef] = None
    encoding: Optional[Encoding] = "plain"
    group: Optional[str] = Field(
        "root",
        description="UNIX group name or GID owner of the file. Default to root(0)",
    )
    owner: Optional[str] = Field(
        "root", description="UNIX user or UID owner of the file. Default to root(0)"
    )
    mode: Optional[str] = Field("0644", description="UNIX file mode")
    context: Optional[Context] = "plain"
    ignore_if_failed: Optional[bool] = Field(
        False,
        description="Whether or not the failure to retrieve the file should stop the execution",
    )
    commands: Optional[Commands] = None


class Model(BaseModel):
    files: Optional[Dict[str, FileDef]] = None
    certificates: Optional[Certificates] = None
    certbot_store: Optional[Dict[str, CertbotAwsStoreCertificate]] = None
    iam_override: Optional[IamOverrideDef] = Field(None, alias="IamOverride")
