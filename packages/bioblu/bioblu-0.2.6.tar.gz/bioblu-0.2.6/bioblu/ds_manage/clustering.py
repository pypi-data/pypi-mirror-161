#!/usr/bin/env python3
import logging
import os.path

import kneed
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import OPTICS, cluster_optics_dbscan, KMeans


def record_clicked_coordinates(n_points=25, hres=640, vres=320):
    plt.figure()
    plt.xlim(0, hres)
    plt.ylim(0, vres)
    points = plt.ginput(n_points, timeout=60)
    points = np.array(points)
    return points


def plot_coordinates(lat: list, lon: list, color=None):
    fig, ax = plt.subplots()
    if color is None:
        plt.scatter(lon, lat, label="Predictions")
    else:
        plt.scatter(lon, lat, label="Predictions", c=color)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()


def cluster_preds_optics(fpath_preds_csv, min_samples=50, xi=0.05, min_cluster_size=0.05, multiply_input=1):
    data = pd.read_csv(fpath_preds_csv)
    X = np.array(data[["longitude", "latitude"]]) * multiply_input

    print(f"Running clustering on {X.shape[0]:,} points...")

    clust = OPTICS(min_samples=min_samples, xi=xi, min_cluster_size=min_cluster_size)
    clust.fit(X)
    print(clust)
    print(f"Labels: {clust.labels_}")
    print(f"No. of labels: {len(set(clust.labels_))}")
    print(f"Labels: {clust.get_params()}")
    print(f"Labels: {clust.ordering_}")

    labels_050 = cluster_optics_dbscan(
        reachability=clust.reachability_,
        core_distances=clust.core_distances_,
        ordering=clust.ordering_,
        eps=0.5,
    )
    labels_300 = cluster_optics_dbscan(
        reachability=clust.reachability_,
        core_distances=clust.core_distances_,
        ordering=clust.ordering_,
        eps=3,
    )

    space = np.arange(len(X))
    reachability = clust.reachability_[clust.ordering_]
    labels = clust.labels_[clust.ordering_]

    plt.figure(figsize=(10, 7))
    G = gridspec.GridSpec(2, 3)
    ax1 = plt.subplot(G[0, :])
    ax2 = plt.subplot(G[1, 0])
    ax3 = plt.subplot(G[1, 1])
    ax4 = plt.subplot(G[1, 2])

    # Reachability plot
    colors = ["g.", "r.", "b.", "y.", "c."]
    for klass, color in zip(range(0, 5), colors):
        Xk = space[labels == klass]
        Rk = reachability[labels == klass]
        ax1.plot(Xk, Rk, color, alpha=0.3)
    ax1.plot(space[labels == -1], reachability[labels == -1], "k.", alpha=0.3)
    ax1.plot(space, np.full_like(space, 2.0, dtype=float), "k-", alpha=0.5)
    ax1.plot(space, np.full_like(space, 0.5, dtype=float), "k-.", alpha=0.5)
    ax1.set_ylabel("Reachability (epsilon distance)")
    ax1.set_title("Reachability Plot")

    # OPTICS
    colors = ["g.", "r.", "b.", "y.", "c."]
    for klass, color in zip(range(0, 5), colors):
        Xk = X[clust.labels_ == klass]
        ax2.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3)
    ax2.plot(X[clust.labels_ == -1, 0], X[clust.labels_ == -1, 1], "k+", alpha=0.1)
    ax2.set_title("Automatic Clustering\nOPTICS")

    # DBSCAN at 0.5
    colors = ["g", "greenyellow", "olive", "r", "b", "c"]
    for klass, color in zip(range(0, 6), colors):
        Xk = X[labels_050 == klass]
        ax3.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3, marker=".")
    ax3.plot(X[labels_050 == -1, 0], X[labels_050 == -1, 1], "k+", alpha=0.1)
    ax3.set_title("Clustering at 0.5 epsilon cut\nDBSCAN")

    # DBSCAN at 3.
    colors = ["g.", "m.", "y.", "c."]
    for klass, color in zip(range(0, 4), colors):
        Xk = X[labels_300 == klass]
        ax4.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3)
    ax4.plot(X[labels_300 == -1, 0], X[labels_300 == -1, 1], "k+", alpha=0.1)
    ax4.set_title("Clustering at 3.0 epsilon cut\nDBSCAN")

    plt.tight_layout()
    plt.show()


def demo_OPTICS():
    # From: https://scikit-learn.org/stable/auto_examples/cluster/plot_optics.html#sphx-glr-auto-examples-cluster-plot-optics-py

    # Generate sample data

    np.random.seed(0)
    n_points_per_cluster = 250

    C1 = [-5, -2] + 0.8 * np.random.randn(n_points_per_cluster, 2)
    C2 = [4, -1] + 0.1 * np.random.randn(n_points_per_cluster, 2)
    C3 = [1, -2] + 0.2 * np.random.randn(n_points_per_cluster, 2)
    C4 = [-2, 3] + 0.3 * np.random.randn(n_points_per_cluster, 2)
    C5 = [3, -2] + 1.6 * np.random.randn(n_points_per_cluster, 2)
    C6 = [5, 6] + 2 * np.random.randn(n_points_per_cluster, 2)
    X = np.vstack((C1, C2, C3, C4, C5, C6))

    plt.scatter(X[:, 0], X[:, 1], alpha=0.2)
    plt.show()

    clust = OPTICS(min_samples=50, xi=0.05, min_cluster_size=0.05)

    # Run the fit
    clust.fit(X)

    labels_050 = cluster_optics_dbscan(
        reachability=clust.reachability_,
        core_distances=clust.core_distances_,
        ordering=clust.ordering_,
        eps=0.5,
    )
    labels_200 = cluster_optics_dbscan(
        reachability=clust.reachability_,
        core_distances=clust.core_distances_,
        ordering=clust.ordering_,
        eps=2,
    )

    space = np.arange(len(X))
    reachability = clust.reachability_[clust.ordering_]
    labels = clust.labels_[clust.ordering_]

    plt.figure(figsize=(10, 7))
    G = gridspec.GridSpec(2, 3)
    ax1 = plt.subplot(G[0, :])
    ax2 = plt.subplot(G[1, 0])
    ax3 = plt.subplot(G[1, 1])
    ax4 = plt.subplot(G[1, 2])

    # Reachability plot
    colors = ["g.", "r.", "b.", "y.", "c."]
    for klass, color in zip(range(0, 5), colors):
        Xk = space[labels == klass]
        Rk = reachability[labels == klass]
        ax1.plot(Xk, Rk, color, alpha=0.3)
    ax1.plot(space[labels == -1], reachability[labels == -1], "k.", alpha=0.3)
    ax1.plot(space, np.full_like(space, 2.0, dtype=float), "k-", alpha=0.5)
    ax1.plot(space, np.full_like(space, 0.5, dtype=float), "k-.", alpha=0.5)
    ax1.set_ylabel("Reachability (epsilon distance)")
    ax1.set_title("Reachability Plot")

    # OPTICS
    colors = ["g.", "r.", "b.", "y.", "c."]
    for klass, color in zip(range(0, 5), colors):
        Xk = X[clust.labels_ == klass]
        ax2.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3)
    ax2.plot(X[clust.labels_ == -1, 0], X[clust.labels_ == -1, 1], "k+", alpha=0.1)
    ax2.set_title("Automatic Clustering\nOPTICS")

    # DBSCAN at 0.5
    colors = ["g", "greenyellow", "olive", "r", "b", "c"]
    for klass, color in zip(range(0, 6), colors):
        Xk = X[labels_050 == klass]
        ax3.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3, marker=".")
    ax3.plot(X[labels_050 == -1, 0], X[labels_050 == -1, 1], "k+", alpha=0.1)
    ax3.set_title("Clustering at 0.5 epsilon cut\nDBSCAN")

    # DBSCAN at 2.
    colors = ["g.", "m.", "y.", "c."]
    for klass, color in zip(range(0, 4), colors):
        Xk = X[labels_200 == klass]
        ax4.plot(Xk[:, 0], Xk[:, 1], color, alpha=0.3)
    ax4.plot(X[labels_200 == -1, 0], X[labels_200 == -1, 1], "k+", alpha=0.1)
    ax4.set_title("Clustering at 2.0 epsilon cut\nDBSCAN")

    plt.tight_layout()
    plt.show()


def get_avg_position(coords: np.array, clusters: np.array):
    cluster_centroids = []
    for c in set(clusters):
        cluster_centroids.append(np.mean(coords[clusters == c, :], axis=0))
    return np.array(cluster_centroids)


def cluster_geolocated_points(data: pd.DataFrame = None, min_samples: int = 2, show_plot=True):
    """
    Clusters points using OPTICS clustering
    :param data: needs to have columns "latitude", "longitude", "confidence"
    :param min_samples:
    :return:
    """
    if data is None:
        data = pd.DataFrame(np.array([[1.0, 3.0, 2.0], [2.0, 2.8, 3.0], [1.5, 2.5, 1.0], [5.0, 5.0, 6.0], [6.0, 4.5, 5.0], [5.5, 5.1, 7.0]]))
        data.columns = ["longitude", "latitude", "confidence"]
    clust = OPTICS(min_samples=min_samples, xi=0.05, min_cluster_size=20)
    clust.fit(data.loc[:, ["longitude", "latitude"]])
    data["cluster"] = clust.labels_

    print(f"{data.loc[data['cluster'] == -1, :].shape[0]} points were not part of any cluster.")
    cluster_centers = data.groupby("cluster").mean()
    cluster_centers.reset_index(inplace=True)
    print(cluster_centers.head())
    cluster_centers = cluster_centers.loc[cluster_centers["cluster"] >= 0, :]

    if show_plot:
        # plt.scatter(data["longitude"], data["latitude"], c=data["cluster"])
        # Plot clustered points
        plt.scatter(data.loc[data["cluster"] != -1, "longitude"],
                    data.loc[data["cluster"] != -1, "latitude"],
                    c=data.loc[data["cluster"] != -1, "cluster"])
        # Plot points outside of clusters
        plt.scatter(data.loc[data["cluster"] == -1, "longitude"],
                    data.loc[data["cluster"] == -1, "latitude"],
                    marker=".", c="gray", alpha=0.5)
        plt.scatter(cluster_centers["longitude"], cluster_centers["latitude"], marker="+", c="red")
        plt.show()

    return cluster_centers


def cluster_points_kmeans_elbow(data: pd.DataFrame, min_clusters=1, max_clusters=50, show_plot=True, return_cluster_centers=True):
    error_values = []
    cluster_labels = []
    for n in range(min_clusters, max_clusters):
        logging.info(f"Running cluster {n} of {max_clusters}")
        kmeans = KMeans(n_clusters=n)
        kmeans.fit(data.loc[:, ["longitude", "latitude"]])
        # Add data points
        error_values.append(kmeans.inertia_)
        cluster_labels.append(kmeans.labels_)


    x = list(range(min_clusters, max_clusters))
    kneedle = kneed.KneeLocator(x=x, y=error_values, S=0, curve="convex", direction="decreasing")
    elbow_point = kneedle.elbow

    cluster_labels = np.array(cluster_labels)[x.index(elbow_point)]


    if show_plot:
        plt.plot(x, error_values)
        plt.scatter(x, error_values)
        plt.scatter(elbow_point, error_values[x.index(elbow_point)], c="red",
                    zorder=2) # Put point on top of line
        plt.xlabel("N clusters")
        plt.ylabel("Cluster inertia (i.e. SS per cluster)")
        plt.show()

    data["cluster"] = cluster_labels
    if return_cluster_centers:
        return data.groupby("cluster").mean()

    return data


if __name__ == "__main__":
    loglevel = logging.INFO
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)

    csv_fpath = "/home/findux/Desktop/Next/Catania_workshop/drone_tests/predictions_2022-07-20_2321_best_DJI_0502_W/geolocated_predictions.csv"
    points_df = pd.read_csv(csv_fpath)
    plot_coordinates(lat=points_df["latitude"], lon=points_df["longitude"])

    data = cluster_points_kmeans_elbow(points_df, return_cluster_centers=False)
    cluster_centers = data.groupby("cluster").mean()

    plt.scatter(data["longitude"], data["latitude"], c=data["cluster"])
    plt.scatter(cluster_centers["longitude"], cluster_centers["latitude"], marker="+", c="red")
    plt.show()

    cluster_geolocated_points(points_df, 50)

    # clustered_points = cluster_geolocated_points(points_df, 50)
    # clustered_points.to_csv(f"{os.path.splitext(csv_fpath)[0]}_clustered.csv")

    # preds = "/home/findux/Desktop/drone_tests/predictions_6674_best_DJI_0495_W_2022-07-06_1748/geolocated_predictions.csv"
    # preds = "/home/findux/Desktop/Next/Catania_workshop/drone_tests/predictions_2022-07-07_1626_6674_best_DJI_0495_W/geolocated_predictions.csv"
    # # cluster_preds_optics(preds, min_samples=200, xi=0.00001, multiply_input=200_000)
    #
    # X = np.array(pd.read_csv(preds)[["longitude", "latitude"]])
    # print(f"X: {X.shape}")
    # km = KMeans()
    # clusters = km.fit(X)
    #
    # centroids = km.cluster_centers_
    # centroid_count = centroids.shape[0]
    # print(f"{centroid_count} centroids.")
    #
    # clust = OPTICS(min_samples=50, xi=0.05, min_cluster_size=0.05)
    # clust.fit(X)
    # print(f"OPTICS coredist: {len(clust.core_distances_)}: {clust.core_distances_}")
    #
    # plt.scatter(X[:, 0], X[:, 1], alpha=0.2)
    # plt.scatter(centroids[:, 0], centroids[:, 1], color="red")
    # # plt.show()
    # # pd.DataFrame(centroids).to_csv("/home/findux/Desktop/drone_tests/centroids.csv")

    # points = record_clicked_coordinates()
    # cluster_test()

    # cluster_geolocated_points()