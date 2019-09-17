import tracking
from objects_to_sheet import ObjectsToSheet


class TrackingUploader:

  def __init__(self, config) -> None:
    self.config = config
    self.objects_to_sheet = ObjectsToSheet()
    self.base_spreadsheet_id = config['reconciliation']['baseSpreadsheetId']

  def upload(self, groups_dict) -> None:
    all_trackings = []
    for trackings in groups_dict.values():
      all_trackings.extend(trackings)

    self.upload_trackings(all_trackings)

  def upload_trackings(self, trackings) -> None:
    existing_trackings = self.objects_to_sheet.download_from_sheet(
        tracking.from_row, self.base_spreadsheet_id, "Trackings")
    existing_tracking_numbers = set([
        existing_tracking.tracking_number
        for existing_tracking in existing_trackings
    ])

    new_trackings = [
        tracking for tracking in trackings
        if tracking.tracking_number not in existing_tracking_numbers
    ]

    all_trackings = existing_trackings + new_trackings
    self.upload_all_trackings(all_trackings)

  def upload_all_trackings(self, trackings) -> None:
    self.objects_to_sheet.upload_to_sheet(trackings, self.base_spreadsheet_id,
                                          "Trackings")