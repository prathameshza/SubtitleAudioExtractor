import streamlit as st
import pandas as pd
from moviepy.editor import AudioFileClip
import pysrt
import os
import shutil
from tqdm import tqdm


# Read the SRT file and return the subtitle data
def read_srt_file(file_path, min_duration=10):
    subs = pysrt.open(file_path)
    subtitle_data = []
    et = 0
    st = subs[0].start
    seg_text = ''
    tot_duration = 0
    for sub in subs:
        start_time = sub.start
        end_time = sub.end
        duration = (end_time - start_time).seconds
        tot_duration += duration
        if tot_duration < min_duration:
            et = sub.end
            seg_text += ' ' + sub.text
        else:
            et = sub.end
            seg_text += ' ' + sub.text
            subtitle_data.append((st, et, seg_text))
            st = sub.end
            tot_duration = 0
            seg_text = ''
    subtitle_data.append((st, et, seg_text))

    return subtitle_data


def save_subtitle_segments(subtitle_data, subtitle_directory):
    if not os.path.exists(subtitle_directory):
        os.makedirs(subtitle_directory)
    else:
        shutil.rmtree(subtitle_directory)
        os.makedirs(subtitle_directory)

    for idx, (_, _, text) in enumerate(subtitle_data):
        subtitle_file_path = os.path.join(subtitle_directory, f'segment_{idx}.txt')
        if text == "":
            continue
        else:
            with open(subtitle_file_path, 'w') as f:
                f.write(text.strip() + '\n')
    return subtitle_directory


def extract_and_store_audio_segments(audio_file, subtitle_data, output_dir):
    audio_clip = AudioFileClip(audio_file)
    data = {'audio': [], 'text': []}  # Initialize dictionary to store audio paths and subtitles
    progress_bar = st.progress(0)  # Initialize the progress bar
    progress_text = st.empty()  # Placeholder for progress text

    for idx, (start_time, end_time, text) in enumerate(tqdm(subtitle_data, desc="Extracting audio segments")):
        output_file = os.path.join(output_dir, f"segment_{idx}.wav")

        # Convert start_time and end_time to seconds
        start_seconds = start_time.hours * 3600 + start_time.minutes * 60 + start_time.seconds + start_time.milliseconds / 1000
        end_seconds = end_time.hours * 3600 + end_time.minutes * 60 + end_time.seconds + end_time.milliseconds / 1000

        # Skip the segment if the duration is less than 1 second, empty or contains only whitespace
        if end_seconds - start_seconds < 1:
            continue

        # Extract the audio segment using moviepy
        segment = audio_clip.subclip(start_seconds, end_seconds)

        try:
            segment.write_audiofile(output_file, fps=22050, codec='pcm_s16le', verbose=False, logger=None)
        except Exception as e:
            idx-=1
            print(e)
        
        # Append the path of the audio segment and the subtitle to the dictionary
        data['audio'].append(output_file)
        data['text'].append(text.strip())

        # Update the progress bar
        progress_bar.progress((idx + 2) / len(subtitle_data))
        progress_text.text(f"Processed {idx + 2}/{len(subtitle_data)} segments")

    # Convert the dictionary to a pandas DataFrame
    df = pd.DataFrame(data)
    return df


# Streamlit Home
st.title("Subtitle Audio Extractor")

audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "ogg"])
srt_file = st.file_uploader("Upload an SRT file", type=["srt"])
audio_directory = 'audio_directory'
subtitle_directory = 'subtitle_directory'

# Check Directory existance
if not os.path.exists(audio_directory):
    os.makedirs(audio_directory)
else:
    shutil.rmtree(audio_directory)
    os.mkdir(audio_directory)

# Define a Process button
if st.button("Process"):
    if audio_file and srt_file:
        with open("temp_audio_file.mp3", "wb") as f:
            f.write(audio_file.getbuffer())

        with open("temp_srt_file.srt", "wb") as f:
            f.write(srt_file.getbuffer())

        # Process the files
        subtitle_data = read_srt_file("temp_srt_file.srt")
        save_subtitle_segments(subtitle_data, subtitle_directory)
        audio_df = extract_and_store_audio_segments("temp_audio_file.mp3", subtitle_data, audio_directory)

        st.success("Processing complete! Showing first 5 files below.")

        # Display the DataFrame
        st.text("Showing ttsdata.csv")
        st.dataframe(audio_df.head(5))

        # Save the DataFrame to a CSV file
        audio_df.to_csv('ttsdata.csv', index=False)

        # Create ttsdata2 DataFrame
        df_data=[]
        for idx in range(len(os.listdir(subtitle_directory))):
            df_data.append({'audio':"audio_directory/segment_{}.wav".format(idx), 'text':"subtitle_directory/segment_{}.txt".format(idx)})
        ttsdata2 = pd.DataFrame(df_data)
        ttsdata2.to_csv('ttsdata2.csv', index=False, sep="|")

        # Display the DataFrame
        st.text("Showing ttsdata2.csv")
        st.dataframe(ttsdata2.head(5))

        # Show the path to the subtitle data directory
        st.write(f"Subtitle and Audio segments saved to {subtitle_directory} & {audio_directory}")

        # Remove temp files
        os.remove("temp_audio_file.mp3")
        os.remove("temp_srt_file.srt")
    else:
        st.error("Please upload both an audio file and an SRT file.")

