#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################
    logger.info("Downloading input artifact")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Reading dataset")
    df = pd.read_csv(artifact_local_path)

    logger.info("Filtering price outliers")
    idx = df["price"].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logger.info("Converting last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

    logger.info("Drop the rows in the dataset that are not a proper geolocation")
    idx = df['longitude'].between( -74.25,  -73.5) & df['latitude'].between( 40.5, 41.2)
    df = df[idx].copy()

    logger.info("Saving cleaned data to clean_sample.csv")
    df.to_csv("clean_sample.csv", index=False)

    logger.info("Uploading cleaned dataset as artifact")
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help='The name of the artifact (dataset) to clean',
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help='The name of the output artifact (cleaned dataset)',
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help='The type of the output artifact (cleaned dataset)',
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help='The description of the output artifact (cleaned dataset)',
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help='The minimum price we want to set for the dataset',
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help='The maximum price we want to set for the dataset',
        required=True
    )


    args = parser.parse_args()

    go(args)
