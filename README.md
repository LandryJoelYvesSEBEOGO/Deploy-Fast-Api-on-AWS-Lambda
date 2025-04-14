# 🚀 Déployer un Modèle de Machine Learning en tant que Fonction AWS Lambda

Ce dépôt contient le code et l'infrastructure pour déployer un modèle de machine learning (modèle de notation d'essai basé sur BERT) en tant que fonction AWS Lambda serverless, en utilisant AWS CDK (Cloud Development Kit) avec TypeScript.

---

## 📌 Vue d'ensemble de l'Architecture

Le workflow de déploiement se compose de deux parties principales :

- **Pipeline de Build Docker** : Prépare le modèle ML et ses dépendances pour le déploiement  
- **Déploiement avec AWS CDK** : Provisionne et configure les ressources AWS  

![Architecture](./docs/deployment_workflow.png)

---

## ✅ Prérequis

- Node.js (v18.x ou supérieur)  
- AWS CLI configuré avec les identifiants appropriés  
- AWS CDK installé (`npm install -g aws-cdk`)  
- Docker installé et en cours d'exécution  
- Python 3.11 installé (pour les tests locaux)  

---

## 🗂️ Structure du Projet

```bash
├── bin/                   # Point d'entrée de l'application CDK
├── lib/                   # Définition de la stack CDK
├── image/                 # Fichiers de l'image Docker
│   ├── Dockerfile         # Dockerfile multi-étapes pour le déploiement Lambda
│   ├── requirements.txt   # Dépendances Python
│   └── src/               # Code source Python
│       └── main.py        # Fonction handler Lambda
├── test/                  # Fichiers de test pour la stack CDK
├── cdk.json               # Configuration CDK
├── tsconfig.json          # Configuration TypeScript
├── package.json           # Dépendances Node.js
└── README.md              # Ce fichier
```

---

## 🐳 Pipeline de Build Docker du Modèle ML

La pipeline de build Docker prépare votre modèle ML pour le déploiement :

1. **Jeu de données** : Données brutes utilisées pour l'entraînement du modèle  
2. **Traitement des données** : Nettoie et prépare les données  
3. **Entraînement du modèle** : Entraîne le modèle de notation d'essai basé sur BERT  
4. **Export final du modèle** : Exporte le modèle au format `.h5`  
5. **Image Docker** : Emballe le modèle avec ses dépendances  

Le Dockerfile utilise un **processus de build multi-étapes** afin d'optimiser la taille de l'image :

- **Étape 1** : Compile les dépendances et télécharge les données NLTK  
- **Étape 2** : Crée une image d'exécution minimale ne contenant que les composants nécessaires  

---

## ☁️ Processus de Déploiement avec AWS CDK

### 🔧 Initialisation CDK  
Crée les ressources AWS nécessaires pour le déploiement via CDK :

- Bucket S3 pour les assets  
- Rôles IAM pour le déploiement  

### 📦 Définition des Ressources  
Configure la fonction Lambda :

- **Allocation mémoire** : 3008 MB  
- **Timeout** : 180 secondes  
- **Architecture** : `x86_64`  
- **Stockage éphémère** : 10 GB  

### 🚀 Déploiement CDK  

- Télécharge l'image Docker sur **AWS ECR**  
- Crée la fonction Lambda  
- Configure l'URL de la fonction avec les réglages **CORS**  

---

## ⚙️ Installation et Déploiement

### 1. Installer les dépendances

```bash
npm install
```

### 2. Préparer votre modèle ML

Assurez-vous que vos modèles sont placés dans les répertoires appropriés :

```
image/models/bert-tokenizer/
image/models/bert-model/
```

Le modèle TensorFlow doit être placé à :

```bash
/var/task/aes_model.h5
```

### 3. Initialiser CDK (première utilisation)

```bash
npx cdk bootstrap
```

### 4. Déployer la stack

```bash
npx cdk deploy
```

Après le déploiement, l'URL de la fonction Lambda s'affichera dans la sortie.

---

## 🧪 Tester la Fonction Déployée

```bash
curl -X POST   -H "Content-Type: application/json"   -d '{"text": "Ceci est un essai pour être noté."}'   <FUNCTION_URL>
```

### ✅ Réponse Exemple

```json
{
  "statusCode": 200,
  "body": {
    "essay score": 4
  }
}
```

---

## 🔍 Détails de la Fonction Lambda

La fonction Lambda exécute les étapes suivantes :

- Initialise le tokenizer BERT, le modèle BERT et le modèle de notation  
- Nettoie et prétraite le texte de l'essai  
- Génère des embeddings BERT pour l'essai  
- Redimensionne les embeddings pour correspondre à la taille d'entrée attendue  
- Effectue une prédiction avec le modèle de notation  
- Retourne le score prédit  

---

## 🧠 Considérations de Performance

- **Mémoire** : 3008 MB  
- **Timeout** : 180 secondes  
- **Remarque** : Les démarrages à froid peuvent être plus lents  
- **Containers chauds** : Les invocations suivantes sont plus rapides

---

## 🔧 Personnalisation

### Modification de la Mémoire et du Timeout  
Dans `lib/DeployFastApiOnAwsLambdaStack.ts` :

```ts
const dockerFunc = new lambda.DockerImageFunction(this, "DockerFunc", {
  memorySize: 4096,  // en MB
  timeout: cdk.Duration.seconds(240),
  // ...
});
```

### Ajout d'une API Gateway

```ts
import * as apigw from 'aws-cdk-lib/aws-apigateway';

const api = new apigw.LambdaRestApi(this, 'ModelApi', {
  handler: dockerFunc,
  proxy: false
});

const modelResource = api.root.addResource('model');
const predictResource = modelResource.addResource('predict');
predictResource.addMethod('POST');
```

---

## 🧹 Nettoyage

```bash
npx cdk destroy
```

---

## 💰 Optimisation des Coûts

- Facturation basée sur la mémoire et le temps d'exécution  
- Les images des conteneurs Lambda sont stockées dans **Amazon ECR**  
- Utilisez la **concurrence provisionnée** pour les charges de travail critiques en termes de performance

---

## 📚 Ressources Complémentaires

- [Bonnes Pratiques AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)  
- [Documentation AWS CDK](https://docs.aws.amazon.com/cdk/)  
- [Machine Learning sur AWS Lambda](https://aws.amazon.com/blogs/machine-learning/)  
- [Tutoriel](https://youtu.be/RGIM4JfsSk0/)

---
