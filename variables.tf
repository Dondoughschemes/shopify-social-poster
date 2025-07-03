variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "ShopifySocialPoster"
}

variable "IG_ACCESS_TOKEN" {
  description = "Instagram Graph API access token for posting."
  type        = string
}

variable "VERIFY_TOKEN" {
  description = "Token used to verify Facebook/Instagram webhook requests."
  type        = string
}

variable "IG_ACCOUNT_ID" {
  description = "Instagram Business Account ID for posting."
  type        = string
}
