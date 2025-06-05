# main.tf

# Terraform 구성 파일

# AWS 프로바이더 설정
# 이 블록은 Terraform이 AWS와 통신하는 데 필요한 정보를 정의합니다.
# "region"은 S3 버킷이 생성될 AWS 리전을 지정합니다.
provider "aws" {
  region = "ap-northeast-2" # 서울 리전 (원하는 리전으로 변경 가능)
  # access_key = "YOUR_ACCESS_KEY"  # 보안상 AWS_ACCESS_KEY_ID 환경 변수 사용 권장
  # secret_key = "YOUR_SECRET_KEY"  # 보안상 AWS_SECRET_ACCESS_KEY 환경 변수 사용 권장
  # 또는 AWS CLI가 구성되어 있다면 자동으로 자격 증명을 찾습니다.
}

# AWS S3 버킷 리소스 정의
# 이 리소스는 AWS S3에 새로운 버킷을 생성합니다.
# "bucket" 속성은 버킷의 고유한 이름을 지정합니다. S3 버킷 이름은 전역적으로 고유해야 합니다.
# "tags" 블록은 버킷에 메타데이터 태그를 할당하여 리소스 관리를 용이하게 합니다.
resource "aws_s3_bucket" "my_terraform_bucket" {
  bucket = "my-unique-terraform-example-bucket-2025-06-01" # 고유한 버킷 이름으로 변경하세요!
  # 버킷 이름 규칙: 소문자, 숫자, 마침표(.), 하이픈(-)만 포함
  # 3에서 63자 사이여야 함
  # 마침표는 IP 주소처럼 보이지 않아야 함

  # 선택 사항: 버킷의 접근 제어 설정
  # ACL (Access Control List) 설정. "private"은 버킷 소유자만 접근 가능합니다.
  acl    = "private"

  # 선택 사항: 버킷에 대한 버전 관리 활성화 (파일 변경 이력을 추적)
  versioning {
    enabled = true
  }

  # 선택 사항: 버킷에 대한 웹 호스팅 활성화 (정적 웹사이트 호스팅)
  # website {
  #   index_document = "index.html"
  #   error_document = "error.html"
  # }

  # 태그: 리소스를 분류하고 관리하는 데 사용
  tags = {
    Name        = "MyTerraformBucket"
    Environment = "Development"
    Project     = "LearningTerraform"
    Owner       = "YourName"
  }

  # 라이프사이클 관리: 리소스 변경 시 동작 정의
  # prevent_destroy = true: 이 버킷이 실수로 파괴되는 것을 방지합니다.
  #              프로덕션 환경에서 매우 유용합니다.
  #              삭제하려면 이 줄을 주석 처리하거나 false로 변경해야 합니다.
  lifecycle {
    prevent_destroy = false # 학습 목적상 일단 false로 설정
  }
}

# S3 버킷의 퍼블릭 접근 차단 설정
# 기본적으로 S3는 퍼블릭 접근을 허용하지 않지만, 명시적으로 차단하는 것이 좋습니다.
resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.my_terraform_bucket.id

  block_public_acls       = true  # 새 ACL이 퍼블릭 접근을 허용하지 않도록 차단
  ignore_public_acls      = true  # 기존 퍼블릭 ACL을 무시
  block_public_policy     = true  # 새 버킷 정책이 퍼블릭 접근을 허용하지 않도록 차단
  restrict_public_buckets = true  # 퍼블릭 버킷에 대한 접근을 제한
}

# Terraform 출력 값 (버킷 이름과 ARN을 콘솔에 표시)
# `output` 블록은 Terraform apply 후 콘솔에 표시될 값을 정의합니다.
output "bucket_name" {
  description = "생성된 S3 버킷의 이름"
  value       = aws_s3_bucket.my_terraform_bucket.bucket
}

output "bucket_arn" {
  description = "생성된 S3 버킷의 ARN (Amazon Resource Name)"
  value       = aws_s3_bucket.my_terraform_bucket.arn
}

output "bucket_id" {
  description = "생성된 S3 버킷의 ID (버킷 이름과 동일)"
  value       = aws_s3_bucket.my_terraform_bucket.id
}

# 이 Terraform 스크립트를 실행하는 방법:
# 1. AWS CLI가 구성되어 있고 자격 증명이 유효한지 확인합니다.
# 2. `terraform init` (Terraform 초기화)
# 3. `terraform plan` (계획 확인)
# 4. `terraform apply` (리소스를 AWS에 생성)
# 5. `terraform destroy` (생성된 리소스 삭제)
