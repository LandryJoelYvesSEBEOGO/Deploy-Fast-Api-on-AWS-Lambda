import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";

export class DeployFastApiOnAwsLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Création de la fonction Lambda basée sur l'image Docker
    const dockerFunc = new lambda.DockerImageFunction(this, "DockerFunc", {
      code: lambda.DockerImageCode.fromImageAsset("./image"),
      // Augmenter la mémoire pour fournir plus de CPU (et éviter d'atteindre 100% d'utilisation mémoire)
      memorySize: 3008 , // Passage de 3008 MB à 4096 MB (à ajuster selon les tests)
      // Augmenter le timeout pour permettre un traitement complet si nécessaire
      timeout: cdk.Duration.seconds(180),
      architecture: lambda.Architecture.X86_64,
      ephemeralStorageSize: cdk.Size.gibibytes(10),
      environment: {
        // Exemple : passage du chemin du modèle via une variable d'environnement
        "MODEL_PATH": "/var/task/aes_model.h5"
      },
    });

    // Ajout d'une URL publique pour accéder à la fonction Lambda
    const functionUrl = dockerFunc.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
        allowedOrigins: ["*"],
      },
    });

    // Export de l'URL de la fonction pour consultation post-déploiement
    new cdk.CfnOutput(this, "FunctionUrlValue", {
      value: functionUrl.url,
    });
  }
}
