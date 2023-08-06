"""Compute node embeddings for the dataset"""

import json
import warnings
from functools import partial
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import torch
from transformers import (
    AutoFeatureExtractor,
    AutoModel,
    AutoModelForImageClassification,
    AutoTokenizer,
)
from transformers import logging as tf_logging

tf_logging.set_verbosity_error()


class Embedder:
    """Compute node embeddings for the dataset"""

    def __init__(
        self,
        include_articles: bool,
        include_tweet_images: bool,
        include_extra_images: bool,
        text_embedding_model_id: str,
        image_embedding_model_id: str,
    ):
        self.include_articles = include_articles
        self.include_tweet_images = include_tweet_images
        self.include_extra_images = include_extra_images
        self.text_embedding_model_id = text_embedding_model_id
        self.image_embedding_model_id = image_embedding_model_id

    def embed_all(
        self, nodes: Dict[str, pd.DataFrame], nodes_to_embed: List[str]
    ) -> Tuple[Dict[str, pd.DataFrame], bool]:
        """Computes embeddings of node features.

        Args:
            nodes (Dict[str, pd.DataFrame]):
                A dictionary of node dataframes.
            nodes_to_embed (list of str):
                The node types which needs to be embedded. If a node type does not
                exist in the graph it will be ignored.

        Returns:
            pair of Dict[str, pd.DataFrame] and bool:
                A dictionary of node dataframes with embeddings, and a boolean
                indicating whether any embeddings were added.
        """
        # Create variable keeping track of whether any embeddings have been
        # added
        embeddings_added = False

        # Embed tweets
        if (
            "tweet" in nodes_to_embed
            and "tweet" in nodes
            and len(nodes["tweet"]) > 0
            and "text_emb" not in nodes["tweet"].columns
        ):
            nodes["tweet"] = self._embed_tweets(tweet_df=nodes["tweet"])
            embeddings_added = True

        # Embed replies
        if (
            "reply" in nodes_to_embed
            and "reply" in nodes
            and len(nodes["reply"]) > 0
            and "text_emb" not in nodes["reply"].columns
        ):
            nodes["reply"] = self._embed_replies(reply_df=nodes["reply"])
            embeddings_added = True

        # Embed users
        if (
            "user" in nodes_to_embed
            and "user" in nodes
            and len(nodes["user"]) > 0
            and "description_emb" not in nodes["user"].columns
        ):
            nodes["user"] = self._embed_users(user_df=nodes["user"])
            embeddings_added = True

        # Embed articles
        if (
            "article" in nodes_to_embed
            and "article" in nodes
            and len(nodes["article"]) > 0
            and "content_emb" not in nodes["article"].columns
        ):
            nodes["article"] = self._embed_articles(article_df=nodes["article"])
            embeddings_added = True

        # Embed images
        if (
            "image" in nodes_to_embed
            and "image" in nodes
            and len(nodes["image"]) > 0
            and "pixels_emb" not in nodes["image"].columns
        ):
            nodes["image"] = self._embed_images(image_df=nodes["image"])
            embeddings_added = True

        # Embed claims
        if (
            "claim" in nodes_to_embed
            and "claim" in nodes
            and len(nodes["claim"]) > 0
            and "reviewer_emb" not in nodes["claim"].columns
        ):
            nodes["claim"] = self._embed_claims(claim_df=nodes["claim"])
            embeddings_added = True

        return nodes, embeddings_added

    @staticmethod
    def _embed_text(text: str, tokenizer, model) -> np.ndarray:
        """Extract a text embedding.

        Args:
            text (str):
                The text to embed.
            tokenizer (transformers.PreTrainedTokenizer):
                The tokenizer to use.
            model (transformers.PreTrainedModel):
                The model to use.

        Returns:
            np.ndarray:
                The embedding of the text.
        """
        with torch.no_grad():
            inputs = tokenizer(text, truncation=True, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            result = model(**inputs)
            return result.pooler_output[0].cpu().numpy()

    def _embed_tweets(self, tweet_df: pd.DataFrame) -> pd.DataFrame:
        """Embeds all the tweets in the dataset.

        Args:
            tweet_df (pd.DataFrame):
                The tweet dataframe.

        Returns:
            pd.DataFrame:
                The tweet dataframe with embeddings.
        """
        # Load text embedding model
        model_id = self.text_embedding_model_id
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)

        # Move model to GPU if available
        if torch.cuda.is_available():
            model.cuda()

        # Define embedding function
        embed = partial(self._embed_text, tokenizer=tokenizer, model=model)

        # Embed tweet text using the pretrained transformer
        text_embs = tweet_df.text.progress_apply(embed)
        tweet_df["text_emb"] = text_embs

        # Embed tweet language using a one-hot encoding
        languages = tweet_df.lang.tolist()
        one_hotted = [
            np.asarray(lst) for lst in pd.get_dummies(languages).to_numpy().tolist()
        ]
        tweet_df["lang_emb"] = one_hotted

        return tweet_df

    def _embed_replies(self, reply_df: pd.DataFrame) -> pd.DataFrame:
        """Embeds all the replies in the dataset.

        Args:
            reply_df (pd.DataFrame): The reply dataframe.

        Returns:
            pd.DataFrame: The reply dataframe with embeddings.
        """
        # Load text embedding model
        model_id = self.text_embedding_model_id
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)

        # Move model to GPU if available
        if torch.cuda.is_available():
            model.cuda()

        # Define embedding function
        embed = partial(self._embed_text, tokenizer=tokenizer, model=model)

        # Embed tweet text using the pretrained transformer
        text_embs = reply_df.text.progress_apply(embed)
        reply_df["text_emb"] = text_embs

        # Embed tweet language using a one-hot encoding
        languages = reply_df.lang.tolist()
        one_hotted = [
            np.asarray(lst) for lst in pd.get_dummies(languages).to_numpy().tolist()
        ]
        reply_df["lang_emb"] = one_hotted

        return reply_df

    def _embed_users(self, user_df: pd.DataFrame) -> pd.DataFrame:
        """Embeds all the users in the dataset.

        Args:
            user_df (pd.DataFrame):
                The user dataframe.

        Returns:
            pd.DataFrame:
                The user dataframe with embeddings.
        """
        # Load text embedding model
        model_id = self.text_embedding_model_id
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)

        # Move model to GPU if available
        if torch.cuda.is_available():
            model.cuda()

        # Define embedding function
        def embed(text: str):
            """Extract a text embedding"""
            if text != text:
                return np.zeros(model.config.hidden_size)
            else:
                return self._embed_text(text, tokenizer=tokenizer, model=model)

        # Embed user description using the pretrained transformer
        desc_embs = user_df.description.progress_apply(embed)
        user_df["description_emb"] = desc_embs

        return user_df

    def _embed_articles(self, article_df: pd.DataFrame) -> pd.DataFrame:
        """Embeds all the tweets in the dataset.

        Args:
            article_df (pd.DataFrame):
                The article dataframe.

        Returns:
            pd.DataFrame:
                The article dataframe with embeddings.
        """
        if self.include_articles:
            # Load text embedding model
            model_id = self.text_embedding_model_id
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModel.from_pretrained(model_id)

            # Move model to GPU if available
            if torch.cuda.is_available():
                model.cuda()

            # Define embedding function
            def embed(text: Union[str, List[str]]):
                """Extract a text embedding"""
                params = dict(tokenizer=tokenizer, model=model)
                if isinstance(text, str):
                    return self._embed_text(text, **params)
                else:
                    return np.mean(
                        [self._embed_text(doc, **params) for doc in text], axis=0
                    )

            def split_content(doc: str) -> List[str]:
                """Split up a string into smaller chunks"""
                if "." in doc:
                    return doc.split(".")
                else:
                    end = min(len(doc) - 1000, 0)
                    return [doc[i : i + 1000] for i in range(0, end, 1000)] + [
                        doc[end:-1]
                    ]

            # Embed titles using the pretrained transformer
            title_embs = article_df.title.progress_apply(embed)
            article_df["title_emb"] = title_embs

            # Embed contents using the pretrained transformer
            contents = article_df.content
            content_embs = contents.map(split_content).progress_apply(embed)
            article_df["content_emb"] = content_embs

        return article_df

    def _embed_images(self, image_df: pd.DataFrame) -> pd.DataFrame:
        """Embeds all the images in the dataset.

        Args:
            image_df (pd.DataFrame):
                The image dataframe.

        Returns:
            pd.DataFrame:
                The image dataframe with embeddings.
        """
        if self.include_tweet_images or self.include_extra_images:
            # Load image embedding model
            model_id = self.image_embedding_model_id
            feature_extractor = AutoFeatureExtractor.from_pretrained(model_id)
            model = AutoModelForImageClassification.from_pretrained(model_id)

            # Move model to GPU if available
            if torch.cuda.is_available():
                model.cuda()

            # Define embedding function
            def embed(image):
                """Extract the last hiden state of image model"""
                with torch.no_grad():

                    # Ensure that the input has shape (C, H, W)
                    image = np.transpose(image, (2, 0, 1))

                    # Extract the features to be used in the model
                    inputs = feature_extractor(images=image, return_tensors="pt")

                    if torch.cuda.is_available():
                        inputs = {k: v.cuda() for k, v in inputs.items()}

                    # Get the embedding
                    outputs = model(**inputs, output_hidden_states=True)
                    penultimate_embedding = outputs.hidden_states[-1]
                    cls_embedding = penultimate_embedding[0, 0, :]

                    # Convert to NumPy and return
                    return cls_embedding.cpu().numpy()

            # Embed pixels using the pretrained transformer
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                image_df["pixels_emb"] = image_df.pixels.progress_apply(embed).tolist()

        return image_df

    def _embed_claims(self, claim_df: pd.DataFrame) -> pd.DataFrame:
        """Embeds all the claims in the dataset.

        Args:
            claim_df (pd.DataFrame):
                The claim dataframe.

        Returns:
            pd.DataFrame:
                The claim dataframe with embeddings.
        """
        # Ensure that `reviewers` is a list
        if isinstance(claim_df.reviewers.iloc[0], str):

            def string_to_list(string: str) -> list:
                """Convert a string to a list.

                Args:
                    string: A string to be converted to a list.

                Returns:
                    list: A list of strings.
                """
                string = string.replace("'", '"')
                return json.loads(string)

            claim_df["reviewers"] = claim_df.reviewers.map(string_to_list)

        # Set up one-hot encoding of claim reviewers
        reviewers = claim_df.reviewers.explode().unique().tolist()
        one_hotted = [
            np.asarray(lst) for lst in pd.get_dummies(reviewers).to_numpy().tolist()
        ]
        one_hot_dict = {
            reviewer: array for reviewer, array in zip(reviewers, one_hotted)
        }

        def embed_reviewers(revs: List[str]) -> np.ndarray:
            """One-hot encoding of multiple reviewers.

            Args:
                revs: A list of reviewers.

            Returns:
                np.ndarray: A one-hot encoded array.
            """
            arrays = [one_hot_dict[rev] for rev in revs]
            return np.stack(arrays, axis=0).sum(axis=0)

        # Embed claim reviewer using a one-hot encoding
        reviewer_emb = claim_df.reviewers.map(embed_reviewers)
        claim_df["reviewer_emb"] = reviewer_emb

        return claim_df
