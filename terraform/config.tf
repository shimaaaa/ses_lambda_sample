provider "aws" {
  version = "~> 3.0"
  region  = "ap-northeast-1"
}
 
terraform {
  required_version = ">= 0.12"
  backend "s3" {
    bucket = "terraform-tfstate-shima"
    key    = "sestest/terraform.tfstate"
    region = "ap-northeast-1"
  }
}