import os
import cv2
import glob
import ffmpeg


def addExt(path: str, ext: str) -> str:
    """
    Add ext to path

    :param path: Path to file
    :param ext: Added ext
    :rtype: str
    :return: Path with added ext
    """

    pathExt = os.path.splitext(path)
    return pathExt[0] + '.' + ext + pathExt[1]


def compareFrames(framePath_1: str, framePath_2: str) -> bool:
    """
    Compare 2 frames

    :param framePath_1: Path to frame 1
    :param framePath_2: Path to frame 2
    :return: bool
    """

    # TODO: Check different frames size

    frame_1 = cv2.imread(framePath_1)
    frame_2 = cv2.imread(framePath_2)
    diff = cv2.norm(frame_1, frame_2, cv2.NORM_L2)

    if diff == 0.0:
        return True

    return False


def delExt(path: str, extCount: int = 1) -> str:
    """
    Del ext from path

    :param path: Path to file
    :param extCount: Count of deleted ext
    :rtype: str
    :return: Path without ext
    """

    pathNoExt = path
    for _ in range(extCount):
        pathNoExt = os.path.splitext(pathNoExt)[0]

    return pathNoExt


def templatedRemoveFiles(template: str) -> None:
    """
    Remove files by template

    :param template: Template
    :return: None
    """

    removeFiles = glob.iglob(template)

    for _file in removeFiles:
        os.remove(_file)


def getExt(path: str, extCount: int = 1) -> str:
    """
    Return file extension from path

    :param path: Path to file
    :param extCount: Count of returned extension
    :rtype: str
    :return: Extension
    """

    pathNoExt = path
    lastExt = ''
    for _ in range(extCount):
        splitPath = os.path.splitext(pathNoExt)
        pathNoExt = splitPath[0]
        lastExt = splitPath[1]

    if lastExt != '':
        # Del .
        lastExt = lastExt[1:]

    return lastExt


def concatVideo(inPath_1: str, inPath_2: str, outPath: str):
    """
    Concat 2 video files with same codecs (it use ffmpeg)
    :param inPath_1: Path to 1 input video file
    :param inPath_2: Path to 2 input video file
    :param outPath: Path to output video file
    :return: None
    """

    ffmpeg.input(f'concat:{inPath_1}|{inPath_2}')\
        .output(outPath, vcodec='copy', acodec='copy')\
        .overwrite_output()\
        .run(quiet = True)


def getFilesCount(filesTemplate: str) -> int:
    """
    Get files count from filesTemplate
    :param filesTemplate:
    :return: Files count from filesTemplate
    """

    files = glob.iglob(filesTemplate)

    i = 0
    for _ in files:
        i += 1

    return i


def intTo2str(number: int) -> str:
    """
    Convert integer to 2 chars string with 0
    :param number: 1 or 2 digit integer number
    :return: 2 chars number with 0
    """

    if number < 10:
        return '0' + str(number)

    return str(number)
