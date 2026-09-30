from pathlib import Path
class S3ObjectStorage:
    def __init__(self,bucket,endpoint=None,region=None):
        import boto3
        kwargs={"region_name":region} if region else {}
        if endpoint: kwargs["endpoint_url"]=endpoint
        self.client=boto3.client("s3",**kwargs); self.bucket=bucket
    def put(self,data,filename="object.bin"):
        import hashlib
        digest=hashlib.sha256(data).hexdigest()
        suffix=Path(filename).suffix[:20]
        key=f"{digest}{suffix}"
        self.client.put_object(Bucket=self.bucket,Key=key,Body=data)
        return {"key":key,"sha256":digest,"size":len(data)}
    def get(self,key):
        return self.client.get_object(Bucket=self.bucket,Key=key)["Body"].read()
    def delete(self,key):
        self.client.delete_object(Bucket=self.bucket,Key=key)
