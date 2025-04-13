import torch
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from transformers import BertTokenizer, BertModel
import tensorflow as tf
import os

# Configuration des chemins pour AWS Lambda (fichiers dans LAMBDA_TASK_ROOT)
# Remplacez par ceci:
nltk_data_path = f"{os.environ['LAMBDA_TASK_ROOT']}/nltk_data"
os.environ["NLTK_DATA"] = nltk_data_path

# Variables globales pour les modèles (chargés au premier appel)
tokenizer = None
bert_model = None
grading_model = None
lemmatizer = None
embedding_size = 300  # Taille d'embedding attendue par le modèle

def initialize_models():
    global tokenizer, bert_model, grading_model, lemmatizer
    
    if tokenizer is None:
        tokenizer = BertTokenizer.from_pretrained(f"{os.environ['LAMBDA_TASK_ROOT']}/models/bert-tokenizer", local_files_only=True)
    
    if bert_model is None:
        bert_model = BertModel.from_pretrained(f"{os.environ['LAMBDA_TASK_ROOT']}/models/bert-model", local_files_only=True)
    
    if lemmatizer is None:
        lemmatizer = WordNetLemmatizer()
    
    if grading_model is None:
        model_path = '/var/task/aes_model.h5'
        grading_model = tf.keras.models.load_model(model_path)
def clean_essays(essay_v, remove_stopwords):
    # Supprimer les caractères non alphabétiques
    essay_v = re.sub("[^a-zA-Z]", " ", essay_v)
    
    # Convertir en minuscules
    words = essay_v.lower()
    
    # Supprimer les espaces supplémentaires
    words = re.sub(r'\s+', ' ', words).strip()
    
    # Tokeniser les mots
    words = words.split()
    
    # Supprimer les stopwords
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if w not in stops]
        words = [lemmatizer.lemmatize(w) for w in words]
    return " ".join(words)

def get_bert_embeddings(text):
    # Tokeniser le texte
    input_ids = tokenizer.encode(text, max_length=512, truncation=True, return_tensors='pt')
    attention_mask = (input_ids != 0).float()

    # Obtenir la sortie du modèle BERT
    with torch.no_grad():
        output = bert_model(input_ids, attention_mask=attention_mask)[0]

    # Moyenner les représentations de tokens
    return output.mean(dim=1).squeeze().detach().numpy()

def resize_embedding(embedding, target_size):
    orig_size = embedding.shape[0]
    
    if orig_size == target_size:
        return embedding
    
    # Si l'original est plus grand, tronquer
    if orig_size > target_size:
        return embedding[:target_size]
    
    # Si l'original est plus petit, remplir de zéros
    resized = np.zeros(target_size, dtype=np.float32)
    resized[:orig_size] = embedding
    return resized

def handler(event, context):
    """Handler de AWS Lambda pour évaluer un essai et retourner un score"""
    try:
        # Extraire le texte de l'essai depuis l'événement
        essay_text = event['text']
        
        # S'assurer que les modèles sont chargés
        initialize_models()
        
        # Nettoyer et prétraiter l'essai
        cleaned_essay = clean_essays(essay_text, remove_stopwords=True)
        
        # Obtenir les embeddings BERT
        embeddings = get_bert_embeddings(cleaned_essay)
        
        # Redimensionner les embeddings
        resized_embeddings = resize_embedding(embeddings, embedding_size)
        
        # Préparer pour la prédiction
        features = np.array([resized_embeddings])
        features = np.zeros((1, embedding_size), dtype="float32")
        features[0] = resized_embeddings
        features = np.expand_dims(features, axis=1)
        
        # Faire la prédiction
        prediction = grading_model.predict(features, verbose=0)
        score = int(np.around(prediction[0][0]))
        
        # Retourner la réponse
        return {
            "statusCode": 200,
            "body": {
                "essay score": score
            }
        }
    
    except Exception as e:
        # Gérer les erreurs
        return {
            "statusCode": 500,
            "body": {
                "error": f"Erreur lors de l'évaluation de l'essai: {str(e)}"
            }
        }
