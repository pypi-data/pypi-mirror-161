import pandas
import os
import cv2
import youtube_dl
import math
import re

# from download_youtube_clips import main
failed_videos_due_to_unavailability = []
failed_without_reason = []


def video_processing(VIDEO_ID, OUTPUT_DIRECTORY):
    video_id = VIDEO_ID
    video_url = VIDEO_ID
    output_directory = OUTPUT_DIRECTORY

    url = "https://www.youtube.com/watch?v=" + video_id

    ydl_opts = {}
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    try:
        info_dict = ydl.extract_info(video_url, download=False)

    except:
        print("Failed:" + video_id)
        failed_videos_due_to_unavailability.append('..' + video_id + '..')
        return

    formats = info_dict.get('formats', None)
    length = math.floor(info_dict['duration'])
    title = info_dict["title"]
    regex = re.compile('[^a-zA-Z0-9()]')
    title = regex.sub('_', title)

    for f in formats:
        if f.get('format_note', None) == '144p':
            url = f.get('url', None)
            break
        if f.get('format_note', None) == '360p':
            url = f.get('url', None)
            break
        if f.get('format_note', None) == '240p':
            url = f.get('url', None)
            break

    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        print('video not opened')
        failed_without_reason.append(video_id)
        return

    frame_rate = math.floor(cap.get(5))

    os.chdir(output_directory)

    if not (os.path.isdir(output_directory + "/" + title + "-" + video_id)):
        os.mkdir(title + "-" + video_id)

    os.chdir(output_directory + "/" + title + "-" + video_id)

    flag = 0

    if length > 28740:
        length = 28740
    gap = math.floor(length / 8)

    while True:
        ret, frame = cap.read()
        if flag == 0 or 1 or 2 or 3 or 4 or 5 or 6 or 7:
            point = ((flag * gap) + gap)
            cap.set(1, point * frame_rate)
        if flag == 8:
            break
        if ret:
            minute = point // 60
            if length < 60:
                if flag == 0:
                    file_name = "-" + str(point) + "s.png"
                else:
                    cv2.imwrite(f"clip" + file_name, frame)
                    file_name = "-" + str(point) + "s.png"
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            if length > 60 and 60 > minute:
                minute = point // 60
                second = point - (minute * 60)
                if flag == 0:
                    file_name = "-" + str(minute) + "m-" + str(second) + "s.png"
                else:
                    cv2.imwrite(f"clip" + file_name, frame)
                    file_name = "-" + str(minute) + "m-" + str(second) + "s.png"
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            if minute >= 60:
                hr = minute // 60
                minute = (point - (hr * 60 * 60)) // 60
                second = point - ((minute * 60) + (hr * 60 * 60))
                cv2.imwrite(f"clip" + file_name, frame)
                file_name = "-" + str(hr) + "h-" + str(minute) + "m-" + str(second) + "s.png"
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
        else:
            break
        flag += 1
    cap.release()
    print("Success:" + video_id)
    cv2.destroyAllWindows()


def read_xlsx_file(FILE_LOCATION):
    df = pandas.read_excel(FILE_LOCATION, usecols="A")
    return df


def process_video(FILE_LOCATION, OUTPUT_DIRECTORY):
    df = read_xlsx_file(FILE_LOCATION)
    for index, row in df.iterrows():
        print("Processing video with ID: "+row['video_id'])
        video_processing(row['video_id'], OUTPUT_DIRECTORY)
        print("***************************************************")
    print("---------------------------------------------------------")
    print("FAILED (UNAVAILABLE) : "+' '.join(failed_videos_due_to_unavailability))
    print("FAILED (NO SPECIFIC REASON) : "+' '.join(failed_without_reason))
