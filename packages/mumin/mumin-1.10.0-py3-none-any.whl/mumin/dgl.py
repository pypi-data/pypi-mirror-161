"""Functions related to exporting the dataset to the Deep Graph Library"""

import json
from pathlib import Path
from typing import Dict, Tuple, Union

import numpy as np
import pandas as pd
from torch import Tensor


def build_dgl_dataset(
    nodes: Dict[str, pd.DataFrame], relations: Dict[Tuple[str, str, str], pd.DataFrame]
):
    """Convert the dataset to a DGL graph.

    This assumes that the dataset has been compiled and thus also dumped to a local
    file.

    Args:
        nodes (dict):
            The nodes of the dataset, with keys the node types and NumPy arrays as the
            values.
        relations (dict):
            The relations of the dataset, with keys being triples of strings
            (source_node_type, relation_type, target_node_type) and NumPy arrays as the
            values.

    Returns:
        DGLHeteroGraph:
            The graph in DGL format.

    Raises:
        ModuleNotFoundError:
            If `dgl` has not been installed.
    """
    # Import the needed libraries, and raise an error if they have not yet been
    # installed
    try:
        import dgl
        import torch
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Could not find the `dgl` library. Please install it and try again."
        )

    # Remove the claims that are only connected to deleted tweets
    tweet_df = nodes["tweet"].dropna()
    claim_df = nodes["claim"]
    discusses_df = relations[("tweet", "discusses", "claim")]
    discusses_df = discusses_df[discusses_df.src.isin(tweet_df.index.tolist())]
    claim_df = claim_df[claim_df.index.isin(discusses_df.tgt.tolist())]
    nodes["claim"] = claim_df

    # Set up the graph as a DGL graph
    graph_data = dict()
    for canonical_etype, rel_arr in relations.items():

        # Drop the NaN nodes, corresponding to the deleted tweets. We also reset the
        # indices to start from 0, as DGL requires there to be no gaps in the indexing
        src, rel, tgt = canonical_etype
        allowed_src = (
            nodes[src]
            .dropna()
            .reset_index()
            .rename(columns=dict(index="old_idx"))
            .old_idx
        )
        allowed_src = {old: new for new, old in allowed_src.iteritems()}
        allowed_tgt = (
            nodes[tgt]
            .dropna()
            .reset_index()
            .rename(columns=dict(index="old_idx"))
            .old_idx
        )
        allowed_tgt = {old: new for new, old in allowed_tgt.iteritems()}

        # Get a dataframe containing the edges between allowed source and target nodes
        # (i.e., non-deleted)
        rel_arr = (
            relations[canonical_etype][["src", "tgt"]]
            .query("src in @allowed_src.keys() and " "tgt in @allowed_tgt.keys()")
            .drop_duplicates()
        )

        # Convert the node indices in the edge dataframe to the new indices without
        # gaps
        rel_arr.src = [allowed_src[old_idx] for old_idx in rel_arr.src.tolist()]
        rel_arr.tgt = [allowed_tgt[old_idx] for old_idx in rel_arr.tgt.tolist()]

        # Convert the edge dataframe to a NumPy array
        rel_arr = rel_arr.to_numpy()

        # If there are edges left in the edge array, then convert these to PyTorch
        # tensors and add them to the graph data
        if rel_arr.size:
            src_tensor = torch.from_numpy(rel_arr[:, 0]).long()
            tgt_tensor = torch.from_numpy(rel_arr[:, 1]).long()
            graph_data[canonical_etype] = (src_tensor, tgt_tensor)

            # Adding inverse relations as well, to ensure that graph is bidirected
            graph_data[(tgt, f"{rel}_inv", src)] = (tgt_tensor, src_tensor)

    # Initialise a DGL heterogeneous graph from the graph data
    dgl_graph = dgl.heterograph(graph_data)

    def emb_to_tensor(df: pd.DataFrame, col_name: str) -> torch.Tensor:
        """Convenience function converting embeddings to tensors.

        Args:
            df (pd.DataFrame):
                The dataframe containing the embeddings.
            col_name (str):
                The name of the column containing the embeddings.

        Returns:
            torch.Tensor:
                The embeddings as a PyTorch tensor.
        """
        if type(df[col_name].iloc[0]) == str:
            df[col_name] = df[col_name].map(lambda x: json.loads(x))
        np_array = np.stack(df[col_name].tolist())
        if len(np_array.shape) == 1:
            np_array = np.expand_dims(np_array, axis=1)
        return torch.from_numpy(np_array)

    # Initialise `tensors` variable
    tensors: Union[Tuple[Tensor], Tuple[Tensor, Tensor], Tuple[Tensor, Tensor, Tensor]]

    # Add node features to the Tweet nodes
    allowed_tweet_df = nodes["tweet"].dropna().reset_index(drop=True)
    cols = ["num_retweets", "num_replies", "num_quote_tweets"]
    tweet_feats = torch.from_numpy(allowed_tweet_df[cols].astype(float).to_numpy())
    if (
        "text_emb" in allowed_tweet_df.columns
        and "lang_emb" in allowed_tweet_df.columns
    ):
        tweet_embs = emb_to_tensor(allowed_tweet_df, "text_emb")
        lang_embs = emb_to_tensor(allowed_tweet_df, "lang_emb")
        tensors = (tweet_embs, lang_embs, tweet_feats)
    else:
        tensors = (tweet_feats,)
    dgl_graph.nodes["tweet"].data["feat"] = torch.cat(tensors, dim=1)

    # Add node features to the Reply nodes
    if "reply" in nodes.keys() and "reply" in dgl_graph.ntypes:
        allowed_reply_df = nodes["reply"].dropna().reset_index(drop=True)
        cols = ["num_retweets", "num_replies", "num_quote_tweets"]
        reply_feats = torch.from_numpy(allowed_reply_df[cols].astype(float).to_numpy())
        if (
            "text_emb" in allowed_reply_df.columns
            and "lang_emb" in allowed_reply_df.columns
        ):
            reply_embs = emb_to_tensor(allowed_reply_df, "text_emb")
            lang_embs = emb_to_tensor(allowed_reply_df, "lang_emb")
            tensors = (reply_embs, lang_embs, reply_feats)
        else:
            tensors = (reply_feats,)
        dgl_graph.nodes["reply"].data["feat"] = torch.cat(tensors, dim=1)

    # Add node features to the User nodes
    nodes["user"]["verified"] = nodes["user"].verified.astype(np.uint64)
    nodes["user"]["protected"] = nodes["user"].verified.astype(np.uint64)
    cols = [
        "verified",
        "protected",
        "num_followers",
        "num_followees",
        "num_tweets",
        "num_listed",
    ]
    user_feats = torch.from_numpy(nodes["user"][cols].astype(float).to_numpy())
    if "description_emb" in nodes["user"].columns:
        user_embs = emb_to_tensor(nodes["user"], "description_emb")
        tensors = (user_embs, user_feats)
    else:
        tensors = (user_feats,)
    dgl_graph.nodes["user"].data["feat"] = torch.cat(tensors, dim=1)

    # Add node features to the Article nodes
    if "article" in nodes.keys() and "article" in dgl_graph.ntypes:
        if (
            "title_emb" in nodes["article"].columns
            and "content_emb" in nodes["article"].columns
        ):
            title_embs = emb_to_tensor(nodes["article"], "title_emb")
            content_embs = emb_to_tensor(nodes["article"], "content_emb")
            tensors = (title_embs, content_embs)
            dgl_graph.nodes["article"].data["feat"] = torch.cat(tensors, dim=1)
        else:
            num_articles = dgl_graph.num_nodes("article")
            ones = torch.ones(num_articles, 1)
            dgl_graph.nodes["article"].data["feat"] = ones

    # Add node features to the Image nodes
    if "image" in nodes.keys() and "image" in dgl_graph.ntypes:
        if "pixels_emb" in nodes["image"].columns:
            image_embs = emb_to_tensor(nodes["image"], "pixels_emb")
            dgl_graph.nodes["image"].data["feat"] = image_embs
        else:
            num_images = dgl_graph.num_nodes("image")
            dgl_graph.nodes["image"].data["feat"] = torch.ones(num_images, 1)

    # Add node features to the Hashtag nodes
    if "hashtag" in nodes.keys() and "hashtag" in dgl_graph.ntypes:
        num_hashtags = dgl_graph.num_nodes("hashtag")
        dgl_graph.nodes["hashtag"].data["feat"] = torch.ones(num_hashtags, 1)

    # Add node features to the Claim nodes
    if "claim" in nodes.keys() and "claim" in dgl_graph.ntypes:
        claim_embs = emb_to_tensor(nodes["claim"], "embedding")
        if "reviewer_emb" in nodes["claim"].columns:
            rev_embs = emb_to_tensor(nodes["claim"], "reviewer_emb")
            tensors = (claim_embs, rev_embs)
            dgl_graph.nodes["claim"].data["feat"] = torch.cat(tensors, dim=1)
        else:
            dgl_graph.nodes["claim"].data["feat"] = claim_embs

    # Add labels
    def numericalise_labels(label: str) -> int:
        numericalise = dict(misinformation=0, factual=1)
        return numericalise[label]

    claim_labels = nodes["claim"][["label"]].applymap(numericalise_labels)
    discusses = relations[("tweet", "discusses", "claim")]
    tweet_labels = allowed_tweet_df.merge(
        discusses.merge(claim_labels, left_on="tgt", right_index=True).drop_duplicates(
            "src"
        ),
        left_index=True,
        right_on="src",
        how="left",
    )
    claim_label_tensor = torch.from_numpy(claim_labels.label.to_numpy())
    claim_label_tensor = torch.nan_to_num(claim_label_tensor).long()
    tweet_label_tensor = torch.from_numpy(tweet_labels.label.to_numpy())
    tweet_label_tensor = torch.nan_to_num(tweet_label_tensor).long()
    dgl_graph.nodes["claim"].data["label"] = claim_label_tensor
    dgl_graph.nodes["tweet"].data["label"] = tweet_label_tensor

    # Add masks
    mask_names = ["train_mask", "val_mask", "test_mask"]
    claim_masks = nodes["claim"][mask_names].copy()
    merged = allowed_tweet_df.merge(
        discusses.merge(claim_masks, left_on="tgt", right_index=True).drop_duplicates(
            "src"
        ),
        left_index=True,
        right_on="src",
        how="left",
    )
    for col_name in mask_names:
        claim_tensor = torch.from_numpy(
            nodes["claim"][col_name].astype(float).to_numpy()
        )
        claim_tensor = torch.nan_to_num(claim_tensor).bool()
        tweet_tensor = torch.from_numpy(merged[col_name].astype(float).to_numpy())
        tweet_tensor = torch.nan_to_num(tweet_tensor).bool()
        dgl_graph.nodes["claim"].data[col_name] = claim_tensor
        dgl_graph.nodes["tweet"].data[col_name] = tweet_tensor

    # Return DGL graph
    return dgl_graph


def save_dgl_graph(dgl_graph, path: Union[str, Path] = "mumin.dgl"):
    """Save a MuMiN DGL graph.

    Args:
        dgl_graph (DGL heterogeneous graph):
            The graph to store.
        path (str, optional):
            Where to store the graph. Defaults to 'mumin.dgl'.
    """
    # Import the needed libraries, and raise an error if they have not yet been
    # installed
    try:
        import torch
        from dgl.data.utils import save_graphs
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Could not find the `dgl` library. Please install it and try again."
        )

    # Convert masks to unsigned 8-bit integers
    for mask_name in ["train_mask", "val_mask", "test_mask"]:
        for node_type in ["claim", "tweet"]:
            t = dgl_graph.nodes[node_type].data[mask_name]
            dgl_graph.nodes[node_type].data[mask_name] = t.type(torch.uint8)

    # Save the graph
    save_graphs(str(path), [dgl_graph])


def load_dgl_graph(path: Union[str, Path] = "mumin.dgl"):
    """Load a MuMiN DGL graph.

    Args:
        path (str or Path, optional):
            Where to load the graph from. Defaults to 'mumin.dgl'.

    Returns:
        DGLHeteroGraph:
            The MuMiN graph.
    """
    # Import the needed libraries, and raise an error if they have not yet been
    # installed
    try:
        from dgl.data.utils import load_graphs
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Could not find the `dgl` library. Please install it and try again."
        )

    # Load the graph
    dgl_graph = load_graphs(str(path))[0][0]

    # Convert masks back to booleans
    for mask_name in ["train_mask", "val_mask", "test_mask"]:
        for node_type in ["claim", "tweet"]:
            mask_tensor = dgl_graph.nodes[node_type].data[mask_name]
            dgl_graph.nodes[node_type].data[mask_name] = mask_tensor.bool()

    # Return the graph
    return dgl_graph
