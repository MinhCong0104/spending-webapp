from typing import Optional, Tuple, Union
import cv2 as cv
import numpy as np
import boto3
import tempfile
from pathlib import Path

from .data import DefectPolyGon, DefectThresholdSettings, MissionImage, MissionImageScoreUpdate, MissionImageUpdate, MissionScoreUpdate, MissionScoreUpdatePayload
from src.infra.database import get_mission_images_collection
from src.config.settings import settings

roof_defects_for_score = ['ballast_displacement', 'blocked_drain', 'corrosion', 'debris', 'mold_growing_on_roof',
                            'overhanging_vegetation', 'patching', 'ponding', 'wrinkled_membrane']

defects_allowed_on_roof = ['ponding', 'ballast_displacement','roof_mold','corrosion',
                               'wrinkled_membrane', 'patching', 'debris',]


def get_update_image_index(update: MissionImageUpdate, images: list[MissionImage]) -> Optional[int]:
    for index, img in enumerate(images):
        # match image and update by name
        if Path(img.img_name).stem == Path(update.img_name).stem:
            return index

    return None

def get_roof_mask(image: MissionImage, roof_contours: Optional[list] = None) -> np.ndarray:
    roof_mask = np.zeros(image.roof_mask.shape, image.roof_mask.dtype)
    # for some reason cv2.findContours returns each contour as a 3D NumPy array with one redundant dimension
    # https://stackoverflow.com/questions/57965493/how-to-convert-numpy-arrays-obtained-from-cv2-findcontours-to-shapely-polygons
    cnts = []
    # use update's roof_contours list if present other wise use original image's
    image_contours = roof_contours or image.roof_mask.contour
    # check if roof_mask contour already in opencv format
    if len(image_contours) > 0:
        # ex: [[[[2791, 2977]], [[2792, 2976]], [[2793, 2977]], [[2792, 2978]]]]
        for c in image_contours:
            if len(c[0]) == 1:
                cnts.append(np.array(c))
            else:
                cnts.append(np.array([[point] for point in c]))
    cv.drawContours(roof_mask, cnts, -1, (255), -1)

    return roof_mask

def split_img(image: np.ndarray, scale_w: int, scale_h: int) -> np.ndarray:
    h, w = image.shape[:2]
    
    # Tile parameters
    # integer division 
    wTile = 5456//scale_w
    hTile = 3632//scale_h

    # Number of tiles
    nTilesX = np.uint16(np.ceil(w / wTile))
    nTilesY = np.uint16(np.ceil(h / hTile))

    # Total remainders
    remainderX = nTilesX * wTile - w
    remainderY = nTilesY * hTile - h

    # Set up remainders per tile
    remaindersX = np.ones((nTilesX-1, 1)) * np.uint16(np.floor(remainderX / (nTilesX-1)))
    remaindersY = np.ones((nTilesY-1, 1)) * np.uint16(np.floor(remainderY / (nTilesY-1)))
    remaindersX[0:np.remainder(remainderX, np.uint16(nTilesX-1))] += 1
    remaindersY[0:np.remainder(remainderY, np.uint16(nTilesY-1))] += 1

    # Initialize array of tile boxes
    tiles = np.zeros((nTilesX * nTilesY, 4), np.uint32)

    # Determine proper tile boxes
    k = 0
    x = 0
    for i in range(nTilesX):
        y = 0
        for j in range(nTilesY):
            # print('>>> tilesss', tiles.shape, k, type(k), x, type(x), y, type(y), hTile, type(hTile), wTile, type(wTile))
            try:
                tiles[k, :] = (x, y, hTile, wTile)
            except:
                # print('>>> except')
                # incase error: 
                # ValueError: setting an array element with a sequence. The requested array would exceed the maximum number of dimension of 1
                tiles[k, 0] = x
                tiles[k, 1] = y
                tiles[k, 2] = hTile
                tiles[k, 3] = wTile
            k += 1
            if (j < (nTilesY-1)):
                y = y + hTile - remaindersY[j]
        if (i < (nTilesX-1)):
            x = x + wTile - remaindersX[i]
    return tiles

def filter_defect_by_threshold(defect: DefectPolyGon, threshold_settings: DefectThresholdSettings) -> bool:
    threshold = threshold_settings.general_threshold
    # use general or specific defect class threshold
    if threshold_settings.defect_type_threshold and defect.defect_class in threshold_settings.defect_type_threshold:
        threshold = threshold_settings.defect_type_threshold.get(defect.defect_class)

    # no filter if no threshold
    if threshold is None:
        return True

    # only keep defect with confidence score larger than threshold
    return defect.confidence_score >= threshold

def get_roof_score(roof_mask: np.ndarray, img_data: Union[MissionImageScoreUpdate, MissionImage], project_threshold_settings: Optional[DefectThresholdSettings]) -> float:
    # TODO: should process previous / original defect list if only update threshold
    # use image specific threshold or project threshold
    threshold_settings = img_data.threshold_settings or project_threshold_settings

    # filter defect by threshold if has threshold settings
    defects = [d for d in img_data.defects.polygons if filter_defect_by_threshold(d, threshold_settings)] if threshold_settings else img_data.defects.polygons

    defects_mask = roof_mask * 0
    for defect in defects:
        if defect.defect_class in roof_defects_for_score:
            # draw defect contour on defect mask
            pts = np.array(defect.points)
            # for some reason cv2.findContours returns each contour as a 3D NumPy array with one redundant dimension
            # https://stackoverflow.com/questions/57965493/how-to-convert-numpy-arrays-obtained-from-cv2-findcontours-to-shapely-polygons
            cnts = [np.array([[p] for p in pts])] # ex: [[[[2791, 2977]], [[2792, 2976]], [[2793, 2977]], [[2792, 2978]]]]
            cv.drawContours(defects_mask, cnts, -1, (255,255,255), -1)
    roof_defects_mask = np.logical_and(roof_mask, defects_mask).astype('uint8') * 255

    tiles = split_img(roof_mask, 22, 16)

    roof_block_count, defects_block_count = 0, 0
    for i, tile in enumerate(tiles):
        x1, y1, h, w = tile
        x2, y2 = x1+w, y1+h
        roof_crop = roof_mask[y1:y2, x1:x2]
        defects_crop = roof_defects_mask[y1:y2, x1:x2]
        if 255 in np.unique(roof_crop):
            roof_block_count += 1
        if 255 in np.unique(defects_crop):
            defects_block_count += 1
    
    if roof_block_count == 0 and defects_block_count == 0:
        # max score when there are no defects
        score = 0
    else:
        score = (roof_block_count - defects_block_count) / roof_block_count

    return score

def get_image_data_from_s3(emc_rcif: str, mission_id: str, image_name: str):
    prefix = f'{emc_rcif}/{mission_id}'
    prefix = f'{prefix}/structure1/hdimages'
    # all hdimages in s3 has .jpg lowercase
    normalized_image_name = f'{Path(image_name).stem}.jpg'
    key = f'{prefix}/{normalized_image_name}'

    s3 = boto3.client('s3')
    out_file = tempfile.SpooledTemporaryFile(max_size=25*1024*1024)
    s3.download_fileobj(settings.report_s3, key, out_file)
    # goes to the start of the file after download completed
    out_file.seek(0)
    # https://stackoverflow.com/questions/47515243/reading-image-file-file-storage-object-using-opencv
    file_bytes = np.fromfile(out_file, np.uint8)
    img = cv.imdecode(file_bytes, cv.IMREAD_GRAYSCALE)
    img_mask = img * 0

    # remove file after completed
    out_file.close()

    return img_mask


async def save_unprocessed_image_data(img_mask, emc_rcif: str, mission_id: str, img_name: str):
    mission_image_collection = get_mission_images_collection()

    normalized_image_name = f'{Path(img_name).stem}.jpg'

    data = {
        'img_name': normalized_image_name,
        'roof_mask': {
            'shape': img_mask.shape,
            'dtype': str(img_mask.dtype),
            'contour': [],
        },
        'score': 1, # initial score for ML unprocessed image
        'mission_id': mission_id,
        'emc_rcif': emc_rcif,
        'defects': {
            'polygons': []
        }
    }

    await mission_image_collection.insert_one(data)

    return MissionImage.parse_obj(data)


async def handle_unprocessed_images(images: list[MissionImage], update: MissionScoreUpdatePayload, emc_rcif: str, mission_id: str) -> None:
    """Check for unprocessed image in update list
    Save data for unprocessed image to db
    """
    for img_update in update.image_updates:
        img_index = get_update_image_index(img_update, images)

        # image update doesn't exist in initial mission images
        if img_index is None:
            # try to check if image is not ML processed image by getting from s3
            img_mask = get_image_data_from_s3(emc_rcif, mission_id, img_update.img_name)
            await save_unprocessed_image_data(img_mask, emc_rcif, mission_id, img_update.img_name)


def calculate_roof_score_updates(images: list[MissionImage], update: MissionScoreUpdatePayload, emc_rcif: str, mission_id: str) -> Tuple[float, list[float]]:
    image_scores = [i.score for i in images]
    image_update_scores = [1 for _ in update.image_updates]
    
    # recalculate all images_scores if project threshold settings change
    if update.project_threshold_settings and (update.project_threshold_settings.defect_type_threshold is not None or update.project_threshold_settings.general_threshold is not None):
        for img_index, img in enumerate(images):
            image_data = images[img_index]
            # ============= roof score
            roof_mask = get_roof_mask(image_data)

            score = get_roof_score(roof_mask=roof_mask, img_data=img, project_threshold_settings=update.project_threshold_settings)
            image_scores[img_index] = score
            
    for img_index, image in enumerate(images):
        image_update_data = None
        img_update_index = None
        for update_index, image_update in enumerate(update.image_updates or []):
            # match image and update by name
            if Path(image.img_name).stem == Path(image_update.img_name).stem:
                image_update_data = image_update
                img_update_index = update_index
                break

        # image is not updated, continue
        if not image_update_data:
            continue

        # image is updated, recalculate score for specific image
        # ============= roof score
        roof_mask = get_roof_mask(image, image_update_data.roof_contours)
        score = get_roof_score(roof_mask=roof_mask, img_data=image_update_data, project_threshold_settings=update.project_threshold_settings)
        image_scores[img_index] = score

        image_update_scores[img_update_index] = score
    # recalculate total average score
    avg_roof_score = np.sum(image_scores) / len(image_scores)

    return (avg_roof_score, image_update_scores)
