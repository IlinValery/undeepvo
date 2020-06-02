import torch.nn as nn

from undeepvo.data.cameras_calibration import CamerasCalibration
from undeepvo.utils import ResultDataPoint
from .losses import SpatialLosses, TemporalImageLosses


class UnsupervisedCriterion(nn.Module):
    def __init__(self, cameras_calibration: CamerasCalibration, lambda_position, lambda_angle, lambda_s,
                 lambda_disparity=1.0):
        super(UnsupervisedCriterion, self).__init__()
        self.spatial_losses = SpatialLosses(cameras_calibration.camera_baseline,
                                            cameras_calibration.focal_length,
                                            cameras_calibration.left_camera_matrix,
                                            cameras_calibration.right_camera_matrix,
                                            cameras_calibration.transform_from_left_to_right,
                                            lambda_position, lambda_angle, lambda_s, lambda_disparity)

        self.temporal_losses = TemporalImageLosses(cameras_calibration.left_camera_matrix,
                                                   cameras_calibration.right_camera_matrix,
                                                   lambda_s)

    def forward(self, left_current_output: ResultDataPoint, right_current_output: ResultDataPoint,
                left_next_output: ResultDataPoint, right_next_output: ResultDataPoint):
        current_spatial_loss, current_photometric_loss, current_disparity_loss, current_pose_loss = \
            self.spatial_losses(left_current_output.input_image, right_current_output.input_image,
                                left_current_output.depth, right_current_output.depth,
                                left_current_output.translation, right_current_output.translation,
                                left_current_output.rotation, right_current_output.rotation)
        next_spatial_loss, next_photometric_loss, next_disparity_loss, next_pose_loss = \
            self.spatial_losses(left_next_output.input_image, right_next_output.input_image,
                                left_next_output.depth, right_next_output.depth,
                                left_next_output.translation, right_next_output.translation,
                                left_next_output.rotation, right_next_output.rotation)
        temporal_loss = self.temporal_losses(left_current_output.input_image,
                                             left_next_output.input_image,
                                             left_current_output.depth,
                                             left_next_output.depth,
                                             right_current_output.input_image,
                                             right_next_output.input_image,
                                             right_current_output.depth,
                                             right_next_output.depth,
                                             left_current_output.translation,
                                             right_current_output.translation,
                                             left_current_output.rotation,
                                             right_current_output.rotation,
                                             left_next_output.translation,
                                             right_next_output.translation,
                                             left_next_output.rotation,
                                             right_next_output.rotation)
        return (current_spatial_loss + next_spatial_loss + temporal_loss,
                current_photometric_loss + next_photometric_loss,
                current_disparity_loss + next_disparity_loss,
                current_pose_loss + next_pose_loss,
                temporal_loss)

