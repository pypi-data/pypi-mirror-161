from dataclasses import dataclass

@dataclass
class CreateAccessKeyResult:
	tenant_id: str
	access_key_id: str
	private_key: str


@dataclass
class CreateBucketResult:
	tenant_id: str
	domain_id: str
	bucket_id: str
	alias: str


@dataclass
class CreateDomainResult:
	tenant_id: str
	domain_id: str
	alias: str


@dataclass
class PutObjectResult:
	tenant_id: str
	domain_id: str
	bucket_id: str
	object_id: str
	

@dataclass
class ObjectMetadata:
	md5:str
	content_type:str
	content_length:str
	etag:str
	last_modified:str


@dataclass
class GetObjectResult:
	content: str
	metadata: ObjectMetadata


@dataclass
class CreatePolicyResult:
	tenant_id: str
	policy_id: str


@dataclass
class CreateRuleResult:
	tenant_id: str
	domain_id: str
	rule_id: str
	alias: str
	
	
@dataclass
class CreateTenantResult:
	tenant_id: str


@dataclass
class CreateWatermarkResult:
	tenant_id: str
	domain_id: str
	watermark_id: str
	alias: str


@dataclass
class GetWatermarkResult:
	content: str