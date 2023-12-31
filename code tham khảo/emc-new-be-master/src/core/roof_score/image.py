import boto3
from io import BytesIO
import cv2 as cv
import tempfile
from pathlib import Path
import numpy as np
from typing import Optional

from .data import MissionImage, MissionImageUpdate, MissionScoreUpdate, DefectClass, DefectThresholdSettings, RoofMask
from .calculation import filter_defect_by_threshold
from src.config.settings import settings

defects_palette = [[0, 0, 0], [255, 50, 50], [255, 153, 50], [255, 255, 50],  [153, 50, 255], [50, 255, 255], [107, 142, 35],
                    [0, 255, 0], [119, 11, 32], [50, 50, 255], [153, 255, 50], [255, 50, 255]]

defect_colors = {
    DefectClass.Background: [0, 0, 0],
    DefectClass.BallastDisplacement: [255, 50, 50],
    DefectClass.BLockedDrain: [255, 153, 50],
    DefectClass.Corrosion: [255, 255, 50],
    DefectClass.DamagedWalkways: [153, 50, 255],
    DefectClass.Debris: [50, 255, 255],
    DefectClass.RoofMold: [107, 142, 35],
    DefectClass.OverhangingVegetation: [0, 255, 0],
    DefectClass.Patching: [119, 11, 32],
    DefectClass.Ponding: [50, 50, 255],
    DefectClass.StepsWithoutAdequateContrast: [153, 255, 50],
    DefectClass.WrinkledMembrane: [255, 50, 255],
    DefectClass.WalkwayCrack: [255, 255, 0],
    DefectClass.LowStepContrast: [153, 255, 50]
}

def redraw_mission_images(images: list[MissionImage], project_threshold_settings: Optional[DefectThresholdSettings]):
    """redraw images's updated defect and label
    then upload to s3 and copy to emc owned s3
    """
    for img in images:
        cv_img = draw_image(img, project_threshold_settings)
        upload_drawn_image(img, cv_img)


def draw_image(image: MissionImage, project_threshold_settings: Optional[DefectThresholdSettings]):
    cv_img = download_image(image)

    # use image specific threshold or project threshold
    threshold_settings = image.threshold_settings or project_threshold_settings
    # filter defect by threshold if has threshold settings
    defects = [d for d in image.defects.polygons if filter_defect_by_threshold(d, threshold_settings)] if threshold_settings else image.defects.polygons

    for defect in defects:
        pts = np.array(defect.points)

        # put defect label on image
        confidence = defect.confidence_score
        b = get_points_bbox(pts)

        label_color = (0, 0, 0)
        if defect.defect_class in defect_colors:
            label_color = defect_colors[defect.defect_class]
        # opencv use BGR color so we convert RGB -> BGR
        label_color = (label_color[2], label_color[1], label_color[0])

        cv.putText(cv_img, defect.defect_class + ' ' + str(confidence), (max(b[0] - 20, 0), b[1]), cv.FONT_HERSHEY_SIMPLEX, 1.25, label_color, 4, cv.LINE_AA)

        # draw defect contour on image
        # for some reason cv2.findContours returns each contour as a 3D NumPy array with one redundant dimension
        # https://stackoverflow.com/questions/57965493/how-to-convert-numpy-arrays-obtained-from-cv2-findcontours-to-shapely-polygons
        cnts = [np.array([[p] for p in pts])] # ex: [[[[2791, 2977]], [[2792, 2976]], [[2793, 2977]], [[2792, 2978]]]]
        cv.drawContours(cv_img, cnts, -1, label_color, 10)

    return cv_img

def upload_drawn_image(image: MissionImage, img_file):
    s3 = boto3.client('s3')
    # encode
    is_success, buffer = cv.imencode(".jpg", img_file)
    io_buf = BytesIO(buffer)

    prefix = f'{image.emc_rcif}/{image.mission_id}/structure1/hdimages_updated'
    normalized_image_name = f'{Path(image.img_name).stem}.jpg'
    key = f'{prefix}/{normalized_image_name}'

    # s3 upload_fileobj will close file after upload
    # not using upload_fileobj to avoid problem between asyncio and multi threads upload
    s3.put_object(
        Body=io_buf,
        Bucket=settings.report_s3,
        Key=key,
    )

def get_points_bbox(points: np.ndarray):
    minx, miny = np.min(points, axis=0)
    maxx, maxy = np.max(points, axis=0)

    return minx, miny, maxx, maxy

def download_image(image: MissionImage):
    prefix = f'{image.emc_rcif}/{image.mission_id}'
    prefix = f'{prefix}/structure1/hdimages'
    # all hdimages in s3 has .jpg lowercase
    normalized_image_name = f'{Path(image.img_name).stem}.jpg'
    key = f'{prefix}/{normalized_image_name}'

    s3 = boto3.client('s3')
    out_file = tempfile.SpooledTemporaryFile(max_size=25*1024*1024)
    s3.download_fileobj(settings.report_s3, key, out_file)
    # goes to the start of the file after download completed
    out_file.seek(0)

    # https://stackoverflow.com/questions/47515243/reading-image-file-file-storage-object-using-opencv
    file_bytes = np.fromfile(out_file, np.uint8)
    # convert numpy array to image
    img = cv.imdecode(file_bytes, cv.IMREAD_COLOR)

    out_file.close()

    return img

def update_image_data(img: MissionImage, update: MissionImageUpdate):
    """Mutate image data with updated data
    """
    img.defects = update.defects
    img.score = update.score
    if update.roof_contours:
        if not img.roof_mask:
            # TODO: temp workaround for image without roofmask by using bounding box of update roof contour
            points = np.array(update.roof_contours[0])
            bbox = get_points_bbox(points)
            img.roof_mask = RoofMask(shape=[bbox[2], bbox[3]], dtype='uint8', contour=update.roof_contours)
        else:
            img.roof_mask.contour = update.roof_contours
    if update.env_contours:
        img.env_contours = update.env_contours
    if update.threshold_settings:
        img.threshold_settings = update.threshold_settings

    return img

def update_image_list(images: list[MissionImage], update_list: Optional[list[MissionScoreUpdate]]):
    """update image list with data from mission score update
    """
    if not update_list:
        return images

    for img in images:
        img_name = Path(img.img_name).stem
        # loop from latest update to first to find match image update
        for update in reversed(update_list):
            image_updates = update.image_updates

            # check if image in latest update
            match_img_update = next((i for i in image_updates if Path(i.img_name).stem == img_name), None)
            if not match_img_update:
                continue

            update_image_data(img, match_img_update)
            break

    return images
