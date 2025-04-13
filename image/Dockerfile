# Étape 1 : Construction des dépendances et préchargement des données NLTK
FROM public.ecr.aws/lambda/python:3.11 AS builder

# Installer les dépendances
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt


# Télécharger les ressources NLTK dans un emplacement permanent
RUN mkdir -p ${LAMBDA_TASK_ROOT}/nltk_data && \
    python -c "import nltk; \
        nltk.download('stopwords', download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
        nltk.download('punkt', download_dir='${LAMBDA_TASK_ROOT}/nltk_data'); \
        nltk.download('wordnet', download_dir='${LAMBDA_TASK_ROOT}/nltk_data')"

# Maintenant installer les dépendances dans le répertoire spécifique pour Lambda
RUN pip install --no-cache-dir -r requirements.txt -t ${LAMBDA_TASK_ROOT}/python

# Étape 2 : Création de l'image finale minimale avec uniquement ce qui est nécessaire
FROM public.ecr.aws/lambda/python:3.11

# Copier les dépendances installées depuis l'étape 1
COPY --from=builder ${LAMBDA_TASK_ROOT}/python ${LAMBDA_TASK_ROOT}/python
# Copier les données NLTK depuis l'étape 1
COPY --from=builder ${LAMBDA_TASK_ROOT}/nltk_data ${LAMBDA_TASK_ROOT}/nltk_data

# Copier le code source et les modèles préchargés
COPY src/* ${LAMBDA_TASK_ROOT}
COPY models/bert-tokenizer ${LAMBDA_TASK_ROOT}/models/bert-tokenizer
COPY models/bert-model ${LAMBDA_TASK_ROOT}/models/bert-model

# Configurer l'environnement pour que NLTK trouve ses données
ENV NLTK_DATA=${LAMBDA_TASK_ROOT}/nltk_data
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}/python:${PYTHONPATH:-}

# Commande de lancement
CMD ["main.handler"]