provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "shopify_lambda" {
  function_name = var.lambda_function_name
  filename      = "${path.module}/lambda.zip"
  handler       = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/lambda.zip")
  runtime       = "python3.11"
  role          = aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      IG_ACCESS_TOKEN = var.IG_ACCESS_TOKEN
      VERIFY_TOKEN    = var.VERIFY_TOKEN
      IG_ACCOUNT_ID   = var.IG_ACCOUNT_ID
    }
  }
}

resource "aws_apigatewayv2_api" "shopify_api" {
  name          = "ShopifySocialPosterAPI"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.shopify_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.shopify_lambda.invoke_arn
  integration_method = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "post_route" {
  api_id    = aws_apigatewayv2_api.shopify_api.id
  route_key = "POST /post"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.shopify_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "allow_apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.shopify_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.shopify_api.execution_arn}/*/*"
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.shopify_api.api_endpoint
  description = "Invoke URL for your Lambda function via HTTP API"
}

