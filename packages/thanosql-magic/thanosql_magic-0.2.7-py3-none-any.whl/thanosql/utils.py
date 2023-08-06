import pandas as pd
from IPython.display import Audio, Image, Video, display

from thanosql.exceptions import ThanoSQLInternalError


def print_image(df, print_option):
    column_name = print_option.get("image_column", "image_path")
    image_file_list = list(df[column_name])

    ### display 10 iamges
    limit = 10
    base_dir = print_option.get("base_dir", "")
    for image_path in image_file_list[:limit]:
        iamge_full_path = f"{base_dir}/{image_path}"
        print(iamge_full_path)
        display(Image(iamge_full_path, width=240, height=240))
    return


def print_audio(df, print_option):
    column_name = print_option.get("audio_column", "audio_path")
    audio_file_list = list(df[column_name])

    ### display 5 audios
    limit = 5
    base_dir = print_option.get("base_dir", "")
    for audio_path in audio_file_list[:limit]:
        audio_full_path = f"{base_dir}/{audio_path}"
        print(audio_full_path)
        display(Audio(audio_full_path))
    return


def print_video(df, print_option):
    column_name = print_option.get("video_column", "video_path")
    video_file_list = list(df[column_name])

    ### display 5 videos
    limit = 5
    base_dir = print_option.get("base_dir", "")
    for video_path in video_file_list[:limit]:
        video_full_path = f"{base_dir}/{video_path}"
        print(video_full_path)
        display(Video(video_full_path, embed=True))
    return


def format_result(output_dict: dict):
    query_result = output_dict["output_message"]["data"].get("df")
    if query_result:
        result = pd.read_json(query_result, orient="split")
        print_type = output_dict["output_message"]["data"].get("print")

        if print_type:
            print_option = output_dict["output_message"]["data"].get("print_option", {})

            if print_type == "print_image":
                return print_image(result, print_option)
            elif print_type == "print_audio":
                return print_audio(result, print_option)
            elif print_type == "print_video":
                return print_video(result, print_option)
            else:
                raise ThanoSQLInternalError("Error: Wrong print_type.")
        return result

    print("Success")
    return
