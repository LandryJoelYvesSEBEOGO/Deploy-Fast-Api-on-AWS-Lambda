# Deploy Machine Learning Model as AWS Lambda Function

This repository contains code and infrastructure to deploy a machine learning model (BERT-based essay grading model) as a serverless AWS Lambda function using AWS CDK (Cloud Development Kit) with TypeScript.

---

## 📌 Architecture Overview

The deployment workflow consists of two main parts:

- **Docker Build Pipeline**: Prepares the ML model and dependencies for deployment  
- **AWS CDK Deployment**: Provisions and configures AWS resources  

![Architecture](./docs/deployment_workflow.png)

---

## ✅ Prerequisites

- Node.js (v18.x or higher)  
- AWS CLI configured with appropriate credentials  
- AWS CDK installed (`npm install -g aws-cdk`)  
- Docker installed and running  
- Python 3.11 installed (for local testing)  

---

## 🗂️ Project Structure

<pre> ```bash 
├── bin/ # CDK application entry point 
├── lib/ # CDK stack definition ├── image/ # Docker image files │ ├── Dockerfile # Multi-stage Dockerfile for Lambda deployment │ ├── requirements.txt # Python dependencies │ └── src/ # Python source code │ └── main.py # Lambda handler function ├── test/ # Test files for CDK stack ├── cdk.json # CDK configuration ├── tsconfig.json # TypeScript configuration ├── package.json # Node.js dependencies └── README.md # This file ``` </pre>

yaml
Copier
Modifier

---

## 🐳 ML Model Docker Build Pipeline

The Docker build pipeline prepares your ML model for deployment:

1. **Dataset**: Raw data used for model training  
2. **Data Processing**: Cleans and prepares the data  
3. **Model Training**: Trains the BERT-based essay grading model  
4. **Final Model Export**: Exports the model in `.h5` format  
5. **Docker Image**: Packages the model with its dependencies  

The Dockerfile uses a **multi-stage build process** to optimize image size:

- **Stage 1**: Builds dependencies and downloads NLTK data  
- **Stage 2**: Creates a minimal runtime image with only necessary components  

---

## ☁️ AWS CDK Deployment Process

### CDK Bootstrap  
Creates necessary AWS resources for CDK deployment:
- S3 bucket for assets  
- IAM roles for deployment  

### Define Resources  
Configures the Lambda function:
- Memory allocation: **3008 MB**  
- Timeout: **180 seconds**  
- Architecture: `x86_64`  
- Ephemeral storage: **10 GB**  

### CDK Deploy  
- Uploads Docker image to **AWS ECR**  
- Creates the Lambda function  
- Configures function URL with **CORS** settings  

---

## 🚀 Setup and Deployment

### 1. Install dependencies
```bash
npm install
2. Prepare your ML model
Ensure your models are placed in the correct directories:

arduino
Copier
Modifier
image/models/bert-tokenizer/
image/models/bert-model/
TensorFlow model should be placed at:

bash
Copier
Modifier
/var/task/aes_model.h5
3. Bootstrap CDK (first-time only)
bash
Copier
Modifier
npx cdk bootstrap
4. Deploy the stack
bash
Copier
Modifier
npx cdk deploy
After deployment, the Lambda function URL will be displayed in the output.

🧪 Testing the Deployed Function
bash
Copier
Modifier
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a sample essay to grade."}' \
  <FUNCTION_URL>
Example Response
json
Copier
Modifier
{
  "statusCode": 200,
  "body": {
    "essay score": 4
  }
}
🔍 Lambda Function Details
The Lambda function performs the following steps:

Initializes the BERT tokenizer, BERT model, and grading model

Cleans and preprocesses the input essay text

Generates BERT embeddings for the essay

Resizes embeddings to match input size

Makes a prediction using the grading model

Returns the predicted score

⚙️ Performance Considerations
Memory: 3008 MB

Timeout: 180 seconds

Cold starts may take longer

Subsequent invocations are faster if container stays warm

🛠️ Customization
Modifying Memory and Timeout
In lib/DeployFastApiOnAwsLambdaStack.ts:

ts
Copier
Modifier
const dockerFunc = new lambda.DockerImageFunction(this, "DockerFunc", {
  memorySize: 4096,  // in MB
  timeout: cdk.Duration.seconds(240),
  // ...
});
Adding API Gateway
ts
Copier
Modifier
import * as apigw from 'aws-cdk-lib/aws-apigateway';

const api = new apigw.LambdaRestApi(this, 'ModelApi', {
  handler: dockerFunc,
  proxy: false
});

const modelResource = api.root.addResource('model');
const predictResource = modelResource.addResource('predict');
predictResource.addMethod('POST');
🧹 Cleanup
bash
Copier
Modifier
npx cdk destroy
💰 Cost Optimization
Charged based on memory and execution time

Lambda container images stored in Amazon ECR

Use provisioned concurrency for performance-critical workloads

📚 Additional Resources
AWS Lambda Best Practices

AWS CDK Documentation

Machine Learning on AWS Lambda

📜 License
MIT

🤝 Contributing
Contributions are welcome! Feel free to submit a Pull Request.

vbnet
Copier
Modifier

Let me know if you'd like a `.md` file version ready to download or any section translated to French for Gi
