import clusters
import yaml
import sys
from tracking_output import TrackingOutput
from expected_costs import ExpectedCosts
from group_site_manager import GroupSiteManager
from driver_creator import DriverCreator

CONFIG_FILE = "config.yml"


def find_cluster(all_clusters, tracking):
  for cluster in all_clusters:
    if cluster.group == tracking.group and cluster.trackings.intersection(
        set(tracking.order_ids)):
      return cluster
  return None


def update_clusters(all_clusters, trackings_dict):
  for group, trackings in trackings_dict.items():
    for tracking in trackings:
      cluster = find_cluster(all_clusters, tracking)
      if cluster == None:
        cluster = clusters.Cluster(tracking.group)
        all_clusters.append(cluster)

      cluster.orders.update(tracking.order_ids)
      cluster.trackings.add(tracking.tracking_number)


def fill_expected_costs(all_clusters, config):
  expected_costs = ExpectedCosts(config)
  for cluster in all_clusters:
    total_expected_cost = sum([
        expected_costs.get_expected_cost(order_id)
        for order_id in cluster.orders
    ])
    cluster.expected_cost = total_expected_cost


def get_tracked_costs_by_group(all_clusters, config, driver_creator):
  groups = set()
  for cluster in all_clusters:
    groups.add(cluster.group)

  tracked_costs_by_group = {}
  for group in groups:
    group_site_manager = GroupSiteManager(config, driver_creator)
    tracked_costs_by_group[group] = group_site_manager.get_tracked_costs(group)

  return tracked_costs_by_group


def fill_tracked_costs(all_clusters, config, driver_creator):
  tracked_costs_by_group = get_tracked_costs_by_group(all_clusters, config,
                                                      driver_creator)
  for cluster in all_clusters:
    group = cluster.group
    if group in tracked_costs_by_group:
      tracked_cost = sum([
          tracked_costs_by_group[group].get(tracking_number, 0.0)
          for tracking_number in cluster.trackings
      ])
      cluster.tracked_cost = tracked_cost


if __name__ == "__main__":
  with open(CONFIG_FILE, 'r') as config_file_stream:
    config = yaml.safe_load(config_file_stream)

  tracking_output = TrackingOutput()
  trackings_dict = tracking_output.get_existing_trackings()

  all_clusters = clusters.get_existing_clusters()
  update_clusters(all_clusters, trackings_dict)

  fill_expected_costs(all_clusters, config)
  clusters.write_clusters(all_clusters)
  tracking_output.clear()

  driver_creator = DriverCreator(sys.argv)
  fill_tracked_costs(all_clusters, config, driver_creator)
  for cluster in all_clusters:
    if cluster.expected_cost > cluster.tracked_cost:
      print(str(cluster))
